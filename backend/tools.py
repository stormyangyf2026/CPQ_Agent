#!/usr/bin/env python3
"""
CPQ Agent 工具函数

使用 langchain @tool 装饰器封装的 CPQ App API 工具。
包含认证管理、产品搜索、配置验证、BOM、定价、CRM、报价单等工具。
"""

import json
import os
import sys
import time
from typing import Any

import requests
from langchain.tools import tool

# 确保 cpq_api.py 所在目录在搜索路径中
_CPQ_API_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills", "cpq-agent", "scripts")
if _CPQ_API_DIR not in sys.path:
    sys.path.insert(0, _CPQ_API_DIR)

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


# ── 会话级匹配结果缓存（让 LLM 只需传 rank，不需传 resultId/modelId）──

_session_match_cache: dict[str, dict] = {}
_current_session_id: str = ""


def set_current_session(session_id: str):
    """设置当前会话 ID（由 server.py 在每次 SSE 请求时调用）"""
    global _current_session_id
    _current_session_id = session_id or ""


def get_cached_match() -> dict | None:
    """获取当前会话缓存的匹配结果"""
    return _session_match_cache.get(_current_session_id)


def get_last_confirm_ids() -> dict:
    """获取当前会话最后一次工艺确认的 resultId 和 confirmId"""
    cached = _session_match_cache.get(_current_session_id, {})
    return {
        "resultId": cached.get("lastResultId"),
        "confirmId": cached.get("lastConfirmId"),
        "recordId": cached.get("lastRecordId"),      # ★ 审批编号
    }


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


def _extract_items(result: dict | list) -> list:
    """从多种响应格式中提取产品列表"""
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if "data" in result:
            if isinstance(result["data"], list):
                return result["data"]
            elif isinstance(result["data"], dict):
                return result["data"].get("records") or result["data"].get("list") or []
        elif "rows" in result:
            return result["rows"]
    return []


def _find_all_products_fallback(keyword: str) -> list[dict]:
    """兜底：调用 /cpq/product/model/list 分页获取全量产品，再按关键词过滤。

    因为 /cpq/product/model/search 接口数据不完整（只返回约34个产品），
    而 CPQ 系统有 200+ 个产品（包括 ER/CR 物联网电池系列），
    所以当 search 返回空时，通过 list 接口手动模糊匹配。
    支持去空格重试（如 "ER 14250" → "ER14250"）。
    """
    from cpq_api import list_all_products
    try:
        result = list_all_products()
        rows = []
        if isinstance(result, dict):
            if "rows" in result:
                rows = result["rows"]
            elif "data" in result:
                d = result["data"]
                if isinstance(d, list):
                    rows = d
                elif isinstance(d, dict):
                    rows = d.get("records") or d.get("list") or []
        if not rows:
            return []

        # 生成多个匹配变体：原始关键词 → 去空格 → 每个单词片段
        kw_raw = keyword.lower().strip()
        kw_no_space = kw_raw.replace(" ", "")
        kw_parts = [p for p in kw_raw.split() if p]

        candidates = set()  # 用 set 避免重复
        for p in rows:
            code = (p.get("modelCode") or "").lower()
            name = (p.get("modelName") or "").lower()
            cat = (p.get("categoryPath") or "").lower()
            combined = code + " " + name + " " + cat

            if kw_raw in combined or kw_no_space in combined:
                candidates.add(p.get("modelId"))
                continue

            # 词片段匹配（每个搜索词至少匹配一个片段）
            if len(kw_parts) > 1:
                if all(part in combined for part in kw_parts):
                    candidates.add(p.get("modelId"))

        return [p for p in rows if p.get("modelId") in candidates]
    except Exception:
        return []


@tool
def search_product(keyword: str, limit: int = 5) -> list[dict]:
    """搜索 CPQ 产品型号。

    根据关键词搜索匹配的产品型号，返回产品列表。

    Args:
        keyword: 搜索关键词，如 "ER14250"、"壁挂"
        limit: 返回结果数量上限，默认 5
    """
    kw = keyword.strip()
    items = []
    seen = set()

    def add_result(data):
        if data and isinstance(data, dict) and data.get("modelId") and data["modelId"] not in seen:
            seen.add(data["modelId"])
            items.append(data)

    # ★ 策略1：精确 code 查找（快速）
    variants = [kw]
    if not kw.upper().startswith("EVE-"):
        variants.append("EVE-" + kw)
    if kw.isdigit() or (kw[0].isdigit() and not kw.startswith("ER")):
        variants.append("EVE-ER" + kw.lstrip("ER").lstrip("er"))
    if "-" in kw:
        base = kw.split("-")[0]
        if base not in variants: variants.append(base)
        if not base.upper().startswith("EVE-"): variants.append("EVE-" + base)

    for v in variants[:5]:  # 最多5个变体
        try:
            result = _request("GET", f"/cpq/product/model/code/{v}")
            add_result(result.get("data") or result)
        except Exception: pass

    # ★ 策略2：如果结果不够，尝试 LIKE 匹配（通过 list 接口按 model_code 前缀）
    if len(items) < limit:
        # 提取基础型号（去掉后缀）
        base_model = kw.split("-")[0].upper()
        if base_model.startswith("EVE-"):
            base_model = base_model[4:]
        try:
            listResult = _request("GET", "/cpq/product/model/list", params={"keyword": base_model, "pageSize": str(limit + 5)})
            rows = _extract_items(listResult)
            for r in rows:
                code = (r.get("modelCode") or "").upper()
                if base_model in code:
                    add_result(r)
        except Exception: pass

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
    items = _extract_items(result)
    return items


@tool
def list_quotes(keyword: str = "", status: str = "") -> list[dict]:
    """查询报价单列表。

    获取 CPQ 系统中的报价单列表，支持按报价单号和状态过滤搜索。
    创建报价单后可以用此工具查询新报价单的编号（quoteNo）和ID。

    Args:
        keyword: 搜索关键词，如报价单号 "QTE-20260720-0001"（可选）
        status: 状态过滤，如 "DRAFT" （可选）

    Returns:
        list[dict]: 报价单列表，每个报价单包含 quoteId、quoteNo、accountId、
                    accountName、totalPrice、status 等字段
    """
    import cpq_api
    return cpq_api.list_quotes(keyword=keyword if keyword else None, status=status if status else None)


@tool
def create_quote(customer_id: str, items: list[dict], customer_name: str = "") -> dict:
    """创建报价单（一站式：报价单头+行项目）。

    为指定客户创建完整报价单，包含客户信息和所有BOM行项。
    内部自动三步：创建报价单头 → 获取ID → 逐行写入物料。

    Args:
        customer_id: 客户 ID（从 search_customers 返回的 accountId）
        items: 报价行项列表，每个元素包含：
               - modelId: 产品型号 ID（可选，有配置的产品）
               - materialCode: 物料编码（可选）
               - materialName: 物料名称
               - quantity: 数量
               - unitPrice: 单价
               - unit: 单位（可选，默认 PCS）
               - attributes: 属性选择字典（可选）
               - remark: 备注（可选）
        customer_name: 客户名称（可选，传入后写入报价单的 accountName 字段）

    Returns:
        dict: 创建的报价单信息，包含：
              - quoteId: 报价单ID
              - quoteNo: 报价单编号（如 QTE-20260720-0001）
              - lineCount: 成功写入的行数
              - totalItems: 总行数
              - errors: 写入失败的行（如果有）
    """
    # 转换 items 格式为 cpq_api 期望的 line_items 格式
    line_items = []
    for item in items:
        line_item = {
            "modelId": item.get("modelId"),
            "materialCode": item.get("materialCode"),
            "materialName": item.get("materialName", f"产品_{item.get('modelId', '')}"),
            "quantity": item.get("quantity", 1),
            "unitPrice": item.get("unitPrice") or item.get("price", 0),
        }
        # 只传非 None 的字段
        line_item = {k: v for k, v in line_item.items() if v is not None}
        if item.get("unit"):
            line_item["unit"] = item["unit"]
        if item.get("attributes"):
            line_item["attributes"] = item["attributes"]
        if item.get("remark"):
            line_item["remark"] = item["remark"]
        line_items.append(line_item)

    # 调用 cpq_api 一站式创建
    import cpq_api
    return cpq_api.create_quote_full(
        account_id=customer_id,
        account_name=customer_name if customer_name else None,
        line_items=line_items,
        description=f"通过Agent创建，共{len(line_items)}行物料",
    )


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
            + ("在预算内" if best_match['withinBudget'] else f"超出预算 {best_match['gap']:+,.0f} 元")
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


@tool
def match_product(category_id: int, requirements: dict) -> dict:
    """评分匹配：根据客户需求在产品线内进行6维评分匹配，返回Top10推荐。

    将逐轮对话采集的客户需求（用途、温度、尺寸、密封、寿命、认证）提交给CPQ评分引擎，
    引擎按照产品线配置的维度权重自动评分、排序、过滤，返回达标产品列表。
    每款产品附评分明细、匹配差异点、报价区间、AI选型理由。

    Args:
        category_id: 产品线ID（如 507=锂亚ER电池）
        requirements: 客户需求字典，可包含：
            - usageType: 用途 (如 "智能水表")
            - tempMin/tempMax: 温度范围 (℃)
            - dimensions: {"length": 14.5, "width": 14.5, "height": 50.5} (mm)
            - sealLevel: 密封等级 (如 "IP67")
            - lifeCycleYears: 期望寿命 (年)
            - requiredCertifications: ["CE","UL1642","RoHS"]
            - extraNotes: 补充说明

    Returns:
        dict: 匹配结果，包含 recommendations (Top10列表)、thresholdPassed、suggestDiy 等
    """
    try:
        body = {"categoryId": category_id, "requirements": requirements}
        result = _request("POST", "/cpq/match/score", body=body)
        # 解包 RuoYi R<T> 响应
        data = result.get("data") or result
        # ★ 追加摘要，方便 LLM 一眼看到 resultId + 每款产品的 modelId
        recs = data.get("recommendations", [])
        if recs:
            lines = [f"resultId={data.get('resultId')}"]
            for r in recs[:10]:
                lines.append(f"#{r.get('rank')} {r.get('modelCode')}(modelId={r.get('modelId')}) {r.get('totalScore')}分")
            data["matchSummary"] = " | ".join(lines)

        # ★ 缓存匹配结果，供 select_product 使用（LLM 只需传 rank）
        if _current_session_id and recs:
            _session_match_cache[_current_session_id] = {
                "resultId": data.get("resultId"),
                "recommendations": recs,
                "categoryId": category_id,
                "requirements": requirements,
            }
        return data
    except Exception as e:
        return {"error": str(e), "message": "评分服务暂时不可用，请稍后重试。您也可以手动输入产品型号如 ER14505，我帮您直接查询。"}


@tool
def submit_feasibility_confirm(result_id: int, model_id: int, action: str = "CONFIRM", comment: str = "", requirement_text: str = "", replaced_model_id: int = None, replaced_reason: str = "") -> dict:
    """提交工艺可行性确认。

    将销售选定的产品推送到工艺部门审核。必须附带客户需求的自然语言描述。

    Args:
        result_id: 匹配结果ID（从 match_product 返回的 resultId）
        model_id: 选定的产品型号ID
        action: CONFIRM/REJECT/REPLACE，默认 CONFIRM
        comment: 审核备注
        requirement_text: ★ 客户需求自然语言描述（如"用途:GPS追踪器, 温度:-40~85℃, 防护:IP54..."）
        replaced_model_id: 替代产品ID（仅 REPLACE）
        replaced_reason: 替代推荐理由（仅 REPLACE）

    Returns:
        dict: {confirmId, status, message, modelId}
    """
    try:
        body = {
            "resultId": result_id,
            "modelId": model_id,
            "action": action,
            "comment": comment,
            "requirementText": requirement_text,
        }
        if replaced_model_id:
            body["replacedModelId"] = replaced_model_id
            body["replacedReason"] = replaced_reason or ""
        result = _request("POST", "/cpq/process/confirm", body=body)
        data = result.get("data") or result

        # ★ 补全产品型号信息，供前端卡片展示
        data["resultId"] = result_id
        try:
            prod = _request("GET", f"/cpq/product/model/list", params={"keyword": str(model_id)})
            rows = []
            if isinstance(prod, dict):
                rows = prod.get("rows") or prod.get("data", {}).get("rows", [])
            if rows:
                data["modelCode"] = rows[0].get("modelCode", "")
                data["modelName"] = rows[0].get("modelName", "")
        except Exception:
            pass  # 查不到不影响主流程

        return data
    except Exception as e:
        return {"error": str(e), "status": "ERROR", "message": "提交审核失败，请稍后重试"}


@tool
def select_product(rank: int, requirement_text: str = "", comment: str = "") -> dict:
    """选择第几款推荐产品并提交工艺确认。

    销售说"选第X款"时调用此工具。只需传排名 rank=X，不要自己编 resultId 或 modelId。
    后台会从缓存的 match_product 结果中自动提取真实的 resultId 和 modelId。

    ★ requirement_text: 将第2步确认的完整客户需求原样传入（如"用途：GPS追踪器\\n温度：-40℃ ~ 85℃\\n..."）。
    这是最准确的客户需求描述，会保存到工艺确认单上，不要省略或改写。

    Args:
        rank: 排名数字，如1表示选第1款，2表示选第2款
        requirement_text: ★ 之前确认的完整客户需求文本，原样传入
        comment: 可选备注

    Returns:
        dict: 工艺确认结果
    """
    cached = _session_match_cache.get(_current_session_id)
    if not cached:
        return {"error": "没有缓存的匹配结果", "message": "请先调用 match_product 获取推荐列表，再选择产品"}

    result_id = cached.get("resultId")
    recs = cached.get("recommendations", [])
    if not result_id or not recs:
        return {"error": "缓存数据不完整", "message": "匹配结果缺失，请重新调用 match_product"}

    # 找到指定排名的产品
    product = None
    for r in recs:
        if r.get("rank") == rank:
            product = r
            break

    if not product:
        return {
            "error": f"排名 {rank} 不存在",
            "message": f"当前推荐列表共 {len(recs)} 款产品，请选择 1-{len(recs)} 之间的排名"
        }

    model_id = product.get("modelId")
    model_code = product.get("modelCode", "")
    model_name = product.get("modelName", "")
    print(f"[select_product] session={_current_session_id}, rank={rank}, resultId={result_id}, modelId={model_id}, model={model_code}")

    # ★ LLM 传了确认后的需求文本 → 直接使用，不篡改
    if requirement_text and requirement_text.strip():
        req_text = requirement_text.strip()
    else:
        # 兜底：从缓存的需求 dict 构建文本
        req = cached.get("requirements", {}) or {}
        req_parts = []
        if isinstance(req, dict):
            if req.get("usageType"): req_parts.append(f"用途：{req['usageType']}")
            if req.get("tempMin") is not None or req.get("tempMax") is not None:
                req_parts.append(f"温度：{req.get('tempMin')}℃ ~ {req.get('tempMax')}℃")
            if req.get("sealLevel"): req_parts.append(f"防护等级：{req['sealLevel']}")
            if req.get("lifeCycleYears"): req_parts.append(f"期望寿命：≥{req['lifeCycleYears']}年")
            certs = req.get("requiredCertifications", [])
            if certs: req_parts.append(f"认证要求：{'、'.join(certs)}")
        req_text = "\n".join(req_parts)

    result = submit_feasibility_confirm.func(
        int(result_id), int(model_id), "CONFIRM",
        comment=comment,
        requirement_text=req_text
    )
    # ★ 缓存最后确认的 ID，供 check_process_status / confirm_replacement / create_quote 自动使用
    if _current_session_id:
        cached = _session_match_cache.get(_current_session_id, {})
        cached["lastResultId"] = result_id
        cached["lastConfirmId"] = result.get("confirmId")
        cached["lastRecordId"] = result.get("recordId")      # ★ 审批编号（#开头）
        _session_match_cache[_current_session_id] = cached
    return result


@tool
def create_quote_from_confirm(result_id: int, customer_id: str, customer_name: str, quantity: int) -> dict:
    """根据已确认的工艺确认单创建报价单。

    工艺确认通过后，销售可以提供客户信息和采购数量来创建报价。
    客户信息通过 search_customers 查找获取。

    Args:
        result_id: 匹配结果ID（从 match_product 或 select_product 返回的 resultId），0=从缓存取
        customer_id: 客户ID（从 search_customers 返回的 accountId）
        customer_name: 客户名称
        quantity: 采购数量

    Returns:
        dict: {quoteId, quoteNo, modelCode, modelName, quantity, unitPrice, totalPrice, quoteUrl}
    """
    # 1. 优先用 recordId（审批编号）；兜底用 resultId
    if result_id == 0:
        ids = get_last_confirm_ids()
        result_id = ids.get("recordId") or ids.get("resultId") or 0
    status_result = _request("GET", f"/cpq/process/status/byRecord/{result_id}")
    status_data = status_result.get("data") or status_result
    if not status_data or status_data.get("status") == "NOT_FOUND":
        status_result = _request("GET", f"/cpq/process/status/{result_id}")
        status_data = status_result.get("data") or status_result
    if not status_data or not status_data.get("modelId"):
        return {"error": "确认单不存在或未找到产品信息", "message": "请先完成产品选择和工艺确认"}

    model_id = status_data.get("modelId")
    model_code = status_data.get("modelCode", "")
    model_name = status_data.get("modelName", "")

    # 2. 查产品价格
    unit_price = 0
    try:
        prod = _request("GET", f"/cpq/product/model/{model_id}")
        prod_data = prod.get("data") or prod
        if prod_data and prod_data.get("basePrice") is not None:
            unit_price = float(prod_data["basePrice"])
    except Exception:
        unit_price = 0

    # 3. 创建报价单 — 统一用 _request，不依赖 cpq_api 独立 token
    quote_body = {
        "accountId": int(customer_id),
        "accountName": customer_name,
        "description": f"Agent auto - {model_code} x {quantity}",
    }
    header = _request("POST", "/cpq/quote/header", body=quote_body)
    quote_id = str(header.get("data", ""))
    if not quote_id:
        return {"error": "创建报价单头失败", "message": str(header.get("msg", ""))}

    # 写行项目
    _request("POST", "/cpq/quote/lineitem", body={
        "quoteId": quote_id, "modelId": model_id,
        "quantity": quantity, "unitPrice": unit_price,
        "itemName": f"{model_code} {model_name}",
        "itemCode": model_code,
        "itemType": "PRODUCT", "unit": "PCS",
    })

    total_price = round(unit_price * quantity, 2)
    cfg = _cpq_config or CPQConfig()
    result = {
        "quoteId": quote_id,
        "quoteNo": quote_id,
        "quoteUrl": f"{cfg.frontend_url}/quoting/{quote_id}",
        "modelCode": model_code,
        "modelName": model_name,
        "quantity": quantity,
        "unitPrice": unit_price,
        "totalPrice": total_price,
    }
    print(f"[create_quote] model={model_code} price={unit_price} total={total_price} quoteId={quote_id}")
    return result

def confirm_replacement(confirm_id: int = 0, accept: bool = True) -> dict:
    """确认或拒绝工艺推荐的替代产品。

    当工艺工程师推荐了替代产品后，销售可以说"接受替代"或"坚持原选"来调用此工具。
    confirm_id 可不传，系统会自动使用最近一次 select_product 的确认单ID。

    Args:
        confirm_id: 确认单ID（可选，不传则自动取缓存值）
        accept: True=接受替代产品, False=坚持原选择

    Returns:
        dict: 处理结果
    """
    if not confirm_id or confirm_id == 0:
        ids = get_last_confirm_ids()
        confirm_id = ids.get("confirmId") or 0
        if not confirm_id:
            return {"error": "未找到确认单ID", "message": "请先选择产品再操作替代"}
    try:
        body = {"action": "CONFIRM_REPLACEMENT", "confirmId": confirm_id, "accept": accept}
        result = _request("POST", "/cpq/process/confirm", body=body)
        data = result.get("data") or result
        return data
    except Exception as e:
        return {"error": str(e), "message": "操作失败，请稍后重试"}


@tool
def check_process_status(result_id: int = 0) -> dict:
    """查询工艺确认单状态。

    用户询问"工艺确认进度""审批状态""审核完了吗"时调用。
    如果用户提供了审批编号（如 #287183040），优先用该编号查询；
    没提供时 resultId=0，系统自动从会话缓存中取最近一次的。

    Args:
        result_id: 审批编号(recordId)或匹配结果ID(resultId)，0表示从缓存取

    Returns:
        dict: {status, modelCode, modelName, recordId, chainId, replacedModelCode, replacedReason}
    """
    if not result_id or result_id == 0:
        ids = get_last_confirm_ids()
        result_id = ids.get("recordId") or ids.get("resultId") or 0
    if not result_id:
        return {"error": "未找到活跃的工艺确认单", "message": "请先完成产品选择或提供审批编号"}

    # ★ 优先按 recordId（审批编号 #开头）查 byRecord；兜底按 resultId 查 status
    try:
        result = _request("GET", f"/cpq/process/status/byRecord/{result_id}")
    except Exception:
        result = {}
    data = result.get("data") or result
    if not data or data.get("status") == "NOT_FOUND":
        try:
            result = _request("GET", f"/cpq/process/status/{result_id}")
        except Exception:
            result = {}
        data = result.get("data") or result
    return {
        "status": data.get("status","?"),
        "modelCode": data.get("modelCode",""),
        "modelName": data.get("modelName",""),
        "recordId": data.get("recordId","") or data.get("chainId",""),
        "replacedModelCode": data.get("replacedModelCode",""),
        "replacedReason": data.get("replacedReason",""),
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
