#!/usr/bin/env python3
"""
CPQ Agent 工具函数

使用 langchain @tool 装饰器封装的 CPQ App API 工具。
包含认证管理、产品搜索、配置验证、BOM、定价、CRM、报价单等工具。
"""

import json
import os
import time
from typing import Any

import requests
from langchain.tools import tool

from config import CPQConfig


# ── 认证管理 ──────────────────────────────────────────────

_token_cache: dict[str, Any] = {
    "token": None,
    "expires_at": 0,
}

# Will be set dynamically at server startup
_cpq_config: CPQConfig | None = None


def set_cpq_config(cfg: CPQConfig) -> None:
    """设置 CPQ 连接配置（由 server.py 启动时调用）"""
    global _cpq_config
    _cpq_config = cfg
    # 清除缓存的 token
    _token_cache["token"] = None
    _token_cache["expires_at"] = 0


def _get_token() -> str:
    """获取 Bearer Token，带缓存"""
    global _token_cache, _cpq_config

    cfg = _cpq_config or CPQConfig()

    # 如果 token 还有效，直接返回
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    # 登录获取新 token
    url = f"{cfg.base_url}/auth/login"
    payload = {
        "username": cfg.username,
        "password": cfg.password,
        "clientId": cfg.client_id,
        "grantType": "password",
        "tenantId": "000000",
    }
    headers = {
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=cfg.timeout)
    resp.raise_for_status()
    body = resp.json()

    # 尝试从不同路径提取 token
    raw_token = None
    if "data" in body and isinstance(body["data"], dict):
        raw_token = body["data"].get("access_token")
    elif "access_token" in body:
        raw_token = body["access_token"]

    if not raw_token:
        raise RuntimeError(f"认证失败: 无法从响应中提取 access_token, body={body}")

    _token_cache["token"] = raw_token
    # 默认缓存 30 分钟
    _token_cache["expires_at"] = time.time() + 1800
    return raw_token


def _request(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
    """通用 HTTP 请求"""
    cfg = _cpq_config or CPQConfig()
    token = _get_token()
    url = f"{cfg.base_url}{path}"

    headers = {
        "clientid": cfg.client_id,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = requests.request(
        method=method.upper(),
        url=url,
        json=body,
        params=params,
        headers=headers,
        timeout=cfg.timeout,
    )

    if resp.status_code == 401:
        # Token 过期，清除缓存重试一次
        _token_cache["token"] = None
        _token_cache["expires_at"] = 0
        token = _get_token()
        headers["Authorization"] = f"Bearer {token}"
        resp = requests.request(
            method=method.upper(),
            url=url,
            json=body,
            params=params,
            headers=headers,
            timeout=cfg.timeout,
        )

    resp.raise_for_status()
    return resp.json()


# ── 工具函数 ──────────────────────────────────────────────


@tool
def search_product(keyword: str, limit: int = 5) -> list[dict]:
    """搜索 CPQ 产品型号。

    根据关键词搜索匹配的产品型号，返回产品列表。
    每个产品包含 modelId（型号ID）、modelCode（型号编码）、modelName（型号名称）、
    configType（配置类型）等字段。

    Args:
        keyword: 搜索关键词，如 "HVI"、"壁挂"、"储能"
        limit: 返回结果数量上限，默认 5

    Returns:
        list[dict]: 匹配的产品型号列表
    """
    result = _request("GET", "/cpq/product/model/search", params={"keyword": keyword})
    # 处理多种响应格式: {"data": [...]} / {"data": {"records": [...]}} / {"rows": [...]}
    if isinstance(result, dict):
        # RuoYi-Vue-Plus 标准格式: {"code":200, "data": [...]}
        if "data" in result:
            if isinstance(result["data"], list):
                items = result["data"]
            elif isinstance(result["data"], dict):
                items = result["data"].get("records") or result["data"].get("list") or []
            else:
                items = []
        elif "rows" in result:
            items = result["rows"]
        else:
            items = []
    elif isinstance(result, list):
        items = result
    else:
        items = []
    return items[:limit]


@tool
def get_model_detail(model_id: int) -> dict:
    """获取产品配置模型详情。

    返回产品的完整配置模型，包括属性列表（attributeTypes）、每个属性的选项、
    BOM 行等信息。用于了解某个产品有哪些可配置属性。

    Args:
        model_id: 产品型号 ID（从 search_product 返回的 modelId）

    Returns:
        dict: 产品配置模型详情，包含 modelId, attributeTypes, bomLines, basePrice 等
    """
    return _request("GET", f"/cpq/configure/model/{model_id}")


@tool
def validate_configuration(model_id: int, attributes: dict) -> dict:
    """验证产品配置是否合规。

    根据 CPQ 引擎规则验证已选的属性配置是否合法。
    会检查约束规则、兼容性等，返回验证结果（通过/警告/冲突）。

    Args:
        model_id: 产品型号 ID
        attributes: 属性选择字典，如 {"电芯型号": "LF304", "电网标准": "EU_VDE"}

    Returns:
        dict: 验证结果，包含 validation 状态（PASS/WARNING/ERROR）和详细信息
    """
    return _request("POST", "/cpq/configure/validate",
                    body=attributes, params={"modelId": str(model_id)})


@tool
def get_bom(model_id: int, attributes: dict) -> dict:
    """获取 BOM 物料清单预览。

    根据已选的产品属性配置，展开 BOM 物料清单。
    返回物料的编码、名称、数量、单位等详细信息。

    Args:
        model_id: 产品型号 ID
        attributes: 属性选择字典，如 {"电芯型号": "LF304", "电网标准": "EU_VDE"}

    Returns:
        dict: BOM 清单，包含 mbomLines 列表
    """
    return _request("POST", "/cpq/configure/bom-preview",
                    body=attributes, params={"modelId": str(model_id)})


@tool
def get_pricing(model_id: int, attributes: dict, quantity: int = 1) -> dict:
    """获取产品完整定价。

    完成配置并计算最终定价，包括基准价（基准报价）、折扣后价格、
    建议售价、最低限价等。同时会完成验证和 BOM 展开。

    Args:
        model_id: 产品型号 ID
        attributes: 属性选择字典
        quantity: 数量，默认 1

    Returns:
        dict: 完整定价信息，包含 validation（验证结果）、mbomLines（BOM行）、
              price（定价详情，含 basePrice, discountRate, salePrice, minPrice 等）
    """
    return _request("POST", "/cpq/configure/complete",
                    body=attributes,
                    params={"modelId": str(model_id), "quantity": str(quantity)})


@tool
def search_customers(keyword: str) -> list[dict]:
    """搜索 CRM 客户。

    根据关键词搜索 CRM 系统中的客户账户。
    支持按客户名称、编码等关键词搜索。

    Args:
        keyword: 搜索关键词，如公司名、客户名、编码

    Returns:
        list[dict]: 匹配的客户列表，每个客户包含 accountId（客户ID）、
                    accountName（客户名称）、accountCode（客户编码）等
    """
    result = _request("GET", "/cpq/customer/account/list", params={"keyword": keyword})
    # 处理多种响应格式
    if isinstance(result, dict):
        if "data" in result:
            if isinstance(result["data"], list):
                items = result["data"]
            elif isinstance(result["data"], dict):
                items = result["data"].get("records") or result["data"].get("list") or []
            else:
                items = []
        elif "rows" in result:
            items = result["rows"]
        else:
            items = []
    elif isinstance(result, list):
        items = result
    else:
        items = []
    return items


@tool
def create_quote(customer_id: str, items: list[dict]) -> dict:
    """创建报价单。

    为指定客户创建报价单，包含报价行项（产品配置结果）。
    每个行项应包含 modelId、attributes、quantity 等信息。

    Args:
        customer_id: 客户 ID（从 search_customers 返回的 accountId）
        items: 报价行项列表，每个元素是一个字典，包含：
               - modelId: 产品型号 ID
               - attributes: 属性选择字典
               - quantity: 数量
               - price: (可选) 定价信息

    Returns:
        dict: 创建的报价单信息，包含 quoteId（报价单ID）
    """
    payload = {
        "accountId": customer_id,
        "items": items,
    }
    return _request("POST", "/cpq/quote/header", body=payload)


@tool
def reverse_match_price(target_price: float, requirements: str = "", keywords: str = "", preferred_specs: dict | None = None) -> dict:
    """价格反向匹配：根据目标预算推荐最佳产品配置。

    当客户有明确的预算上限时，此工具自动搜索匹配的产品，
    尝试不同配置从高到低降级，找到符合预算的最佳方案。
    如果无法匹配预算，推荐最接近的替代方案并说明差距。

    Args:
        target_price: 客户目标预算（人民币元）
        requirements: 客户需求描述，如 "德国市场、VDE认证、40kWh"
        keywords: 产品搜索关键词，如 "高压储能"、"电芯"
        preferred_specs: 偏好规格字典，如 {"容量_kWh": 40, "认证": "VDE"}

    Returns:
        dict: 匹配结果，包含：
              - matched: 是否找到预算内的方案
              - best_match: 最佳匹配产品详情
              - price_gap: 与预算的差距
              - alternatives: 其他可选方案列表
              - trade_offs: 降配建议
    """
    # 第一步：搜索产品
    search_keyword = keywords or requirements[:30] or "储能"
    products = search_product.func(search_keyword, limit=10)

    if not products:
        return {
            "matched": False,
            "message": f"未找到与 '{search_keyword}' 匹配的产品",
            "best_match": None,
            "alternatives": []
        }

    # 第二步：对每个产品尝试获取定价
    candidates = []
    for product in products[:5]:
        model_id = product.get("modelId")
        model_name = product.get("modelName", "未知")
        model_code = product.get("modelCode", "")
        base_price_raw = product.get("basePrice", 0)
        try:
            base_price = float(base_price_raw) if base_price_raw else 0
        except (ValueError, TypeError):
            base_price = 0

        # 尝试获取详细定价（如果有属性配置的话）
        pricing_data = None
        try:
            pricing_data = get_pricing.func(model_id, {}, quantity=1)
        except Exception:
            pass

        # 提取建议售价
        suggested_price = base_price
        if pricing_data and isinstance(pricing_data, dict):
            price_info = pricing_data.get("price") or pricing_data
            if isinstance(price_info, dict):
                suggested_price = float(price_info.get("salePrice") or price_info.get("basePrice") or base_price)

        candidates.append({
            "modelId": model_id,
            "modelCode": model_code,
            "modelName": model_name,
            "basePrice": base_price,
            "suggestedPrice": suggested_price,
            "withinBudget": suggested_price <= target_price,
            "gap": suggested_price - target_price,
            "gapPercent": round((suggested_price - target_price) / target_price * 100, 1) if target_price > 0 else 0
        })

    # 第三步：排序：预算内优先，价格从高到低；预算外按差距从小到大
    in_budget = sorted([c for c in candidates if c["withinBudget"]], key=lambda x: -x["suggestedPrice"])
    over_budget = sorted([c for c in candidates if not c["withinBudget"]], key=lambda x: x["gap"])

    best = (in_budget or over_budget)[:1]
    best_match = best[0] if best else None

    return {
        "matched": len(in_budget) > 0,
        "targetPrice": target_price,
        "requirements": requirements or search_keyword,
        "totalCandidates": len(candidates),
        "inBudgetCount": len(in_budget),
        "overBudgetCount": len(over_budget),
        "bestMatch": best_match,
        "withinBudgetOptions": in_budget[:3],
        "overBudgetOptions": over_budget[:3],
        "priceGap": best_match["gap"] if best_match else target_price,
        "recommendation": (
            f"✅ 最佳方案：{best_match['modelName']} ¥{best_match['suggestedPrice']:,.0f} "
            f"{'在预算内' if best_match['withinBudget'] else f'超出预算 {best_match["gap"]:+,.0f} 元'}"
        ) if best_match else "未找到可行方案"
    }


@tool
def compare_solutions(solution_a_id: int, solution_b_id: int,
                      solution_a_desc: str = "方案A", solution_b_desc: str = "方案B") -> dict:
    """方案对比：对比两个产品配置的规格、BOM、定价差异。

    同时获取两个方案的完整信息（详情+BOM+定价），
    并逐项对比，突出差异点（新增/减少/变更）。

    Args:
        solution_a_id: 方案A的产品型号ID
        solution_b_id: 方案B的产品型号ID
        solution_a_desc: 方案A的描述标签（如"HVI高压方案"）
        solution_b_desc: 方案B的描述标签（如"LVI低压方案"）

    Returns:
        dict: 对比结果，包含：
              - basic_comparison: 基本参数对比表
              - pricing_comparison: 定价对比
              - differences: 关键差异列表
              - recommendation: 推荐总结
    """
    def fetch_solution(model_id: int) -> dict:
        """获取方案的完整信息"""
        try:
            # 先搜索产品列表找到目标
            all_products = _request("GET", "/cpq/product/model/search", params={"keyword": ""})
            if isinstance(all_products, dict) and "data" in all_products:
                if isinstance(all_products["data"], list):
                    matched = [p for p in all_products["data"] if p.get("modelId") == model_id]
                elif isinstance(all_products["data"], dict):
                    records = all_products["data"].get("records") or all_products["data"].get("list") or []
                    matched = [p for p in records if p.get("modelId") == model_id]
                else:
                    matched = []
            else:
                matched = []

            product = matched[0] if matched else {}
        except Exception:
            product = {}

        # 尝试获取 BOM 和定价
        try:
            detail = get_model_detail.func(model_id)
        except Exception:
            detail = product

        try:
            pricing = get_pricing.func(model_id, {}, 1)
        except Exception:
            pricing = {}

        return {"product": product, "detail": detail, "pricing": pricing}

    sol_a = fetch_solution(solution_a_id)
    sol_b = fetch_solution(solution_b_id)

    a_product = sol_a.get("product", {})
    b_product = sol_b.get("product", {})
    a_pricing = sol_a.get("pricing", {})
    b_pricing = sol_b.get("pricing", {})

    # 提取价格
    def extract_price(pricing_data) -> float:
        if not pricing_data or not isinstance(pricing_data, dict):
            return 0
        price_info = pricing_data.get("price") or pricing_data
        if isinstance(price_info, dict):
            return float(price_info.get("salePrice") or price_info.get("basePrice") or 0)
        return 0

    price_a = extract_price(a_pricing) or float(a_product.get("basePrice", 0))
    price_b = extract_price(b_pricing) or float(b_product.get("basePrice", 0))

    # 基本参数对比
    basic_comparison = [
        {"field": "型号编码", "valueA": a_product.get("modelCode", "N/A"), "valueB": b_product.get("modelCode", "N/A"),
         "diff": a_product.get("modelCode") != b_product.get("modelCode")},
        {"field": "产品名称", "valueA": a_product.get("modelName", "N/A"), "valueB": b_product.get("modelName", "N/A"),
         "diff": a_product.get("modelName") != b_product.get("modelName")},
        {"field": "建议售价", "valueA": f"¥{price_a:,.0f}", "valueB": f"¥{price_b:,.0f}",
         "diff": price_a != price_b,
         "note": f"差价: ¥{price_a - price_b:+,.0f}"},
        {"field": "配置类型", "valueA": a_product.get("configType", "N/A"), "valueB": b_product.get("configType", "N/A"),
         "diff": a_product.get("configType") != b_product.get("configType")},
    ]

    # 差异分析
    differences = []
    price_diff = price_a - price_b
    if price_diff > 0:
        differences.append(f"💰 {solution_a_desc} 比 {solution_b_desc} 贵 ¥{price_diff:,.0f}")
    elif price_diff < 0:
        differences.append(f"💰 {solution_a_desc} 比 {solution_b_desc} 便宜 ¥{abs(price_diff):,.0f}")
    else:
        differences.append("💰 两个方案价格相同")

    # 推荐
    if price_a <= price_b:
        recommendation = f"如果预算优先，推荐 {solution_a_desc}（¥{price_a:,.0f}）"
    else:
        recommendation = f"如果预算优先，推荐 {solution_b_desc}（¥{price_b:,.0f}）"

    return {
        "solutionA": {"label": solution_a_desc, "modelId": solution_a_id,
                      "modelCode": a_product.get("modelCode"), "price": price_a},
        "solutionB": {"label": solution_b_desc, "modelId": solution_b_id,
                      "modelCode": b_product.get("modelCode"), "price": price_b},
        "basicComparison": basic_comparison,
        "priceDifference": price_diff,
        "differences": differences,
        "recommendation": recommendation
    }


def health_check(base_url: str | None = None) -> tuple[bool, str]:
    """检查 CPQ 服务是否可达"""
    cfg = _cpq_config or CPQConfig()
    url = base_url or cfg.base_url
    try:
        resp = requests.get(f"{url}/auth/login", timeout=5)
        # 能连上就算 OK（认证失败说明服务在运行）
        return True, f"CPQ 服务可达 ({url})"
    except requests.exceptions.ConnectionError:
        return False, f"无法连接到 CPQ 服务 ({url})"
    except requests.exceptions.Timeout:
        return False, f"CPQ 服务连接超时 ({url})"
    except Exception as e:
        return False, f"CPQ 连接异常: {e}"
