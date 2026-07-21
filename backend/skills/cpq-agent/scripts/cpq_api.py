#!/usr/bin/env python3
"""
CPQ App API Client

Provides helper functions for CPQ Agent to call CPQ App REST APIs.
All functions return JSON-serializable Python dicts.
"""

import json
import os
import sys
import urllib.request
import urllib.error

CPQ_URL = os.environ.get("CPQ_URL", "http://localhost:30000")
CLIENT_ID = os.environ.get("CPQ_CLIENT_ID", "e5cd7e4891bf95d1d19206ce24a7b32e")

_cached_token = None


def get_token():
    """获取Bearer Token（缓存，避免重复登录）"""
    global _cached_token
    if _cached_token:
        return _cached_token

    data = json.dumps({
        "username": "admin",
        "password": "admin123",
        "clientId": CLIENT_ID,
        "grantType": "password",
        "tenantId": "000000"
    }).encode()
    req = urllib.request.Request(
        f"{CPQ_URL}/auth/login",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read())
        _cached_token = body["data"]["access_token"]
        return _cached_token


def _request(method, path, body=None, params=None):
    """通用HTTP请求"""
    token = get_token()
    url = f"{CPQ_URL}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())

    headers = {
        "clientid": CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": True, "status": e.code, "message": str(e)}


# ==================== 产品查询 ====================

def search_products(keyword, config_type=None):
    """搜索产品
    Example: search_products("HVI") → [CpqProductModelVo, ...]

    注意：search 接口的数据覆盖范围可能不完整。如果 search 返回空，请尝试
    调用 list_all_products() 手动过滤以获得全量产品列表。
    """
    params = {"keyword": keyword}
    if config_type:
        params["configType"] = config_type
    return _request("GET", "/cpq/product/model/search", params=params)


def list_all_products(page_num=1, page_size=200):
    """获取全量产品列表（分页）

    使用 /cpq/product/model/list 接口获取完整产品列表（200个），
    包含物联网电池方案（ER/CR系列）等 search 接口无法覆盖的产品。

    Example: list_all_products() → {"total": 200, "rows": [...]}
    """
    params = {"pageNum": str(page_num), "pageSize": str(page_size)}
    return _request("GET", "/cpq/product/model/list", params=params)


# ==================== 配置器 ====================

def load_config_model(model_id):
    """加载产品配置模型（属性+选项+默认BOM）
    Example: load_config_model(2091) → {modelId, attributes, bomLines, basePrice, ...}
    """
    return _request("GET", f"/cpq/configure/model/{model_id}")


def validate_selections(model_id, selections):
    """验证属性选择
    Example: validate_selections(2091, {"电芯型号":"LF304","电网标准":"EU_VDE"})
    → ValidationResult
    """
    return _request("POST", f"/cpq/configure/validate", body=selections, params={"modelId": model_id})


def complete_configuration(model_id, selections, quantity=1):
    """完成配置（验证+BOM+定价）
    → ConfigCompleteResponse {validation, mbomLines, price}
    """
    return _request("POST", "/cpq/configure/complete", body=selections,
                    params={"modelId": model_id, "quantity": quantity})


def get_bom_preview(model_id, selections):
    """获取BOM预览（根据属性选择展开）
    → MbomLine[]
    """
    return _request("POST", "/cpq/configure/bom-preview", body=selections, params={"modelId": model_id})


def get_guide_step(model_id, selections):
    """获取向导下一步推荐
    → GuideStep {state, currentAttribute, options, recommendation, ...}
    """
    return _request("POST", "/cpq/configure/guide", body=(selections if selections else {}), params={"modelId": model_id})


# ==================== 配置引擎 ====================

def propagate_constraints(model_id, selections):
    """约束传播：查看当前选择下各属性的可用/禁用选项
    → Map<String, OptionInfo[]>
    """
    return _request("POST", "/cpq/engine/config/propagate", body=selections, params={"modelId": model_id})


def check_compatibility(source_product_id, target_product_id):
    """跨产品兼容性检查
    → "COMPATIBLE" | "CONDITIONAL" | "INCOMPATIBLE"
    """
    return _request("GET", "/cpq/engine/config/compatibility",
                    params={"sourceProductId": source_product_id, "targetProductId": target_product_id})


# ==================== CRM ====================

def list_customers(keyword=None):
    """获取客户列表"""
    params = {}
    if keyword:
        params["keyword"] = keyword
    return _request("GET", "/cpq/customer/account/list", params=params)


def list_opportunities():
    """获取商机列表"""
    return _request("GET", "/cpq/crm/opportunity/list")


# ==================== 报价 ====================

def list_quotes(keyword=None, status=None):
    """获取报价单列表，支持按报价单号和状态搜索
    Example: list_quotes() → 所有报价单
             list_quotes(keyword="QTE-2026") → 按报价单号搜索
             list_quotes(status="DRAFT") → 按状态筛选
    """
    params = {}
    if keyword:
        params["keyword"] = keyword
    if status:
        params["status"] = status
    result = _request("GET", "/cpq/quote/header/list", params=params)
    # 兼容三种响应格式：
    # 1. RuoYi 分页: {"total": N, "rows": [...]}
    # 2. 标准 data: {"data": [...]} 或 {"data": {"records": [...]}}
    # 3. 直接列表: [...]
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if "rows" in result:
            return result["rows"]
        if "data" in result:
            data = result["data"]
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("records") or data.get("list") or []
    return []


def get_quote(quote_id):
    """获取报价单详情（含行项目）
    Example: get_quote(123) → {header: ..., lineItems: [...]}
    """
    return _request("GET", f"/cpq/quote/header/{quote_id}")


def create_quote(account_id, contact=None, department=None, quote_date=None, description=None):
    """创建报价单头（含客户信息）
    Example: create_quote("acc001", contact="张三") → {quoteId, quoteNo, ...}
    """
    body = {
        "accountId": account_id
    }
    if contact:
        body["contact"] = contact
    if department:
        body["department"] = department
    if quote_date:
        body["quoteDate"] = quote_date
    if description:
        body["description"] = description
    return _request("POST", "/cpq/quote/header", body=body)


def add_quote_line_item(quote_id, model_id=None, material_code=None, material_name=None,
                        quantity=1, unit=None, unit_price=None, discount_rate=None,
                        attributes=None, remark=None):
    """向报价单逐行添加物料
    Example:
      add_quote_line_item(456, model_id=2091, quantity=1, unit_price=25000)
      add_quote_line_item(456, material_code="MAT001", material_name="铜排",
                          quantity=2, unit_price=500)
    """
    body = {
        "quoteId": quote_id,
        "quantity": quantity
    }
    if model_id:
        body["modelId"] = model_id
    if material_code:
        body["materialCode"] = material_code
    if material_name:
        body["materialName"] = material_name
    if unit:
        body["unit"] = unit
    if unit_price is not None:
        body["unitPrice"] = unit_price
    if discount_rate is not None:
        body["discountRate"] = discount_rate
    if attributes:
        body["attributes"] = attributes
    if remark:
        body["remark"] = remark
    return _request("POST", "/cpq/quote/lineitem", body=body)


def create_quote_full(account_id, line_items, contact=None, department=None,
                      quote_date=None, description=None):
    """一站式创建报价单：创建报价单头 → 获取ID → 逐行写入物料
    Example:
      line_items = [
        {"modelId": 2091, "quantity": 1, "unitPrice": 25000},
        {"materialCode": "MAT001", "materialName": "铜排", "quantity": 2, "unitPrice": 500},
      ]
      create_quote_full("acc001", line_items, contact="张三")
      → {quoteId, quoteNo, lineCount, message}
    """
    # 第一步：创建报价单头（含客户信息）
    header = create_quote(account_id, contact=contact, department=department,
                          quote_date=quote_date, description=description)
    if header.get("error"):
        return header

    # 第二步：从 header 响应中提取新创建的报价单 ID
    # CPQ 后端 POST /cpq/quote/header 返回 {code:200, data:null}
    # 不走 data 提取，而是通过列表查询找出刚创建的报价单
    raw_header = header.get("data", header)
    quote_id = None
    if raw_header and isinstance(raw_header, dict):
        quote_id = raw_header.get("quoteId")

    if not quote_id:
        # 兜底：查询刚创建的草稿报价单，按 createTime DESC 排序
        # 优先匹配当前客户的最新草稿
        quotes = list_quotes(status="DRAFT")
        if isinstance(quotes, list) and quotes:
            for q in quotes:
                if q.get("accountId") == account_id:
                    quote_id = q.get("quoteId")
                    break
            if not quote_id:
                quote_id = quotes[0].get("quoteId")

    if not quote_id:
        return {"error": True, "message": "创建报价单后无法获取 quoteId", "header": header}

    # 获取报价单详情，提取 quoteNumber
    # CPQ 后端返回的键名为 quoteNumber（而非 quoteNo）
    detail = get_quote(quote_id)
    header_detail = detail.get("data", detail) if isinstance(detail, dict) else {}
    quote_no = (
        header_detail.get("quoteNumber") or
        header_detail.get("quoteNo") or
        f"QTE-{quote_id:04d}"
    )

    # 第三步：逐行写入行项目
    line_count = 0
    errors = []
    for item in line_items:
        result = add_quote_line_item(quote_id, **item)
        if result.get("error"):
            errors.append({"item": item, "error": result.get("message", "unknown")})
        else:
            line_count += 1

    result = {
        "quoteId": quote_id,
        "quoteNo": quote_no,
        "lineCount": line_count,
        "totalItems": len(line_items),
        "errors": errors if errors else None,
        "message": f"报价单 {quote_no} 创建成功，共 {line_count}/{len(line_items)} 行物料"
    }

    # 如果行项目全部失败（例如 CPQ 后端 lineitem 接口 500），标记为 error
    if line_count == 0 and errors:
        result["error"] = True
        error_msgs = [e.get("error", "未知错误") for e in errors[:3]]
        result["message"] = (
            f"报价单 {quote_no} 已创建但行项目全部写入失败: {'; '.join(error_msgs)}。"
            f"请在系统中手动补充行项目。"
        )

    return result


# ==================== 定价 ====================

def calculate_price(product_model_id, quantity=1, currency="CNY", variant_id=None,
                    region=None, channel_id=None, requested_discount=None, bom_cost=None):
    """定价计算"""
    params = {
        "productModelId": product_model_id,
        "quantity": quantity,
        "currency": currency
    }
    if variant_id:
        params["variantId"] = variant_id
    if region:
        params["region"] = region
    if channel_id:
        params["channelId"] = channel_id
    if requested_discount:
        params["requestedDiscount"] = requested_discount
    if bom_cost:
        params["bomCost"] = bom_cost
    return _request("POST", "/cpq/engine/pricing/calculate", params=params)


# ==================== 配置规则 ====================

def list_config_rules(model_id=None, rule_type=None):
    """获取配置规则列表"""
    params = {}
    if model_id:
        params["modelId"] = model_id
    if rule_type:
        params["ruleType"] = rule_type
    return _request("GET", "/cpq/config/rule/list", params=params)


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    if cmd == "search":
        keyword = args[0] if args else ""
        config_type = args[1] if len(args) > 1 else None
        print(json.dumps(search_products(keyword, config_type), ensure_ascii=False, indent=2))
    elif cmd == "model":
        print(json.dumps(load_config_model(int(args[0])), ensure_ascii=False, indent=2))
    elif cmd == "validate":
        model_id = int(args[0])
        selections = json.loads(" ".join(args[1:]))
        print(json.dumps(validate_selections(model_id, selections), ensure_ascii=False, indent=2))
    elif cmd == "complete":
        model_id = int(args[0])
        selections = json.loads(" ".join(args[1:]))
        print(json.dumps(complete_configuration(model_id, selections), ensure_ascii=False, indent=2))
    elif cmd == "guide":
        model_id = int(args[0])
        if args and len(args) > 1:
            selections = json.loads(" ".join(args[1:]))
        else:
            try:
                selections = json.loads(sys.stdin.read().strip())
            except:
                selections = {}
        print(json.dumps(get_guide_step(model_id, selections), ensure_ascii=False, indent=2))
    elif cmd == "propagate":
        model_id = int(args[0])
        if args and len(args) > 1:
            selections = json.loads(" ".join(args[1:]))
        else:
            try:
                selections = json.loads(sys.stdin.read().strip())
            except:
                selections = {}
        print(json.dumps(propagate_constraints(model_id, selections), ensure_ascii=False, indent=2))
    elif cmd == "rules":
        model_id = int(args[0]) if args else None
        print(json.dumps(list_config_rules(model_id), ensure_ascii=False, indent=2))
    elif cmd == "customers":
        print(json.dumps(list_customers(), ensure_ascii=False, indent=2))
    elif cmd == "quotes":
        keyword = args[0] if args else None
        print(json.dumps(list_quotes(keyword=keyword), ensure_ascii=False, indent=2))
    elif cmd == "get-quote":
        print(json.dumps(get_quote(int(args[0])), ensure_ascii=False, indent=2))
    elif cmd == "create-quote":
        account_id = args[0]
        line_items = json.loads(" ".join(args[1:])) if len(args) > 1 else []
        print(json.dumps(create_quote_full(account_id, line_items), ensure_ascii=False, indent=2))
    else:
        print("Usage: python3 cpq_api.py <command> [args...]")
        print("")
        print("  产品搜索:")
        print("    search <keyword> [configType]")
        print("    model <modelId>")
        print("")
        print("  配置器:")
        print("    validate <modelId> <json_selections>")
        print("    complete <modelId> <json_selections>  ← 验证+BOM+定价一次完成")
        print("    guide <modelId> [json_selections]")
        print("    propagate <modelId> [json_selections]")
        print("    rules [modelId]")
        print("")
        print("  CRM:")
        print("    customers")
        print("")
        print("  报价单:")
        print("    quotes [keyword]                      ← 查报价单列表（支持按单号搜索）")
        print("    get-quote <quoteId>                   ← 查报价单详情（含行项目）")
        print("    create-quote <accountId> <json_items> ← 一站式创建报价单（头+行项目）")
        print("")
        print("  Example: python3 cpq_api.py create-quote acc001 '[{\"modelId\":2091,\"quantity\":1,\"unitPrice\":25000}]'")
