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
    """
    params = {"keyword": keyword}
    if config_type:
        params["configType"] = config_type
    return _request("GET", "/cpq/product/model/search", params=params)


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

def list_quotes():
    """获取报价单列表"""
    return _request("GET", "/cpq/quote/header/list")


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
        print(json.dumps(list_quotes(), ensure_ascii=False, indent=2))
    else:
        print("Usage: python3 cpq_api.py <command> [args...]")
        print("  search <keyword> [configType]")
        print("  model <modelId>")
        print("  validate <modelId> <json_selections>")
        print("  complete <modelId> <json_selections>")
        print("  guide <modelId> [json_selections]")
        print("  propagate <modelId> [json_selections]")
        print("  rules [modelId]")
        print("  customers")
        print("  quotes")
