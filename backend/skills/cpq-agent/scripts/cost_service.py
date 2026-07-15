#!/usr/bin/env python3
"""
ERP 成本核算服务（模拟）
实际对接时替换为真实 ERP API 调用
"""
import json
import sys

# ========== 物料成本主数据 ==========
MATERIAL_COST_DB = {
    "CAB-HVI40K-BASE":      {"unit_cost": 8500,  "currency": "CNY", "supplier": "深圳钣金科技",   "lead_time": 15},
    "MOD-HVI-4K-STD":       {"unit_cost": 1850,  "currency": "CNY", "supplier": "亿纬自产",       "lead_time": 7},
    "BMS-HVI-ADV-V3":       {"unit_cost": 3200,  "currency": "CNY", "supplier": "杭州智控电子",   "lead_time": 20},
    "PCS-HYBRID-8K":        {"unit_cost": 4800,  "currency": "CNY", "supplier": "阳光电源",        "lead_time": 25},
    "ENCLOSURE-HVI-IP55":   {"unit_cost": 2200,  "currency": "CNY", "supplier": "深圳钣金科技",   "lead_time": 10},
    "HV-CABLE-SET":         {"unit_cost": 850,   "currency": "CNY", "supplier": "东莞线缆",       "lead_time": 5},
    "BREAKER-HVI-80A":      {"unit_cost": 1200,  "currency": "CNY", "supplier": "正泰电器",        "lead_time": 10},
    "FIRE-SUPPRESS-HVI":    {"unit_cost": 650,   "currency": "CNY", "supplier": "西安消防科技",   "lead_time": 7},
    "EMS-GATEWAY":          {"unit_cost": 1800,  "currency": "CNY", "supplier": "华为技术",        "lead_time": 15},
}

# 制造成本系数
LABOR_RATE = 3200     # 安装调试人工
TESTING_COST = 1500   # 出厂测试
PACKAGING_COST = 800  # 包装运输

# ========== 定价规则 ==========
PRICING_RULES = {
    "EVE-HVI": {          # 高压壁挂产品线
        "target_margin": 0.20,     # 目标毛利率 20%
        "min_margin": 0.12,        # 最低毛利率 12%（低于需审批）
        "max_discount": 0.10,      # 最大折扣 10%
    },
    "EVE-LVI": {          # 低压壁挂产品线
        "target_margin": 0.22,
        "min_margin": 0.15,
        "max_discount": 0.12,
    },
    "DEFAULT": {
        "target_margin": 0.20,
        "min_margin": 0.15,
        "max_discount": 0.10,
    }
}

def get_bom_cost(bom_lines):
    """ERP Agent: 根据BOM物料清单查询成本"""
    result = {"lines": [], "total_material": 0, "total_labor": 0, "total_testing": 0, "total_packaging": 0, "grand_total": 0}

    for line in bom_lines:
        code = line.get("materialCode", "")
        qty = float(line.get("quantity", 0))
        cost_info = MATERIAL_COST_DB.get(code, {"unit_cost": 0, "supplier": "未知", "lead_time": 0})
        unit_cost = cost_info["unit_cost"]
        subtotal = unit_cost * qty

        result["lines"].append({
            "material_code": code,
            "material_desc": line.get("materialDesc", ""),
            "quantity": qty,
            "unit": line.get("unit", ""),
            "unit_cost": unit_cost,
            "subtotal": subtotal,
            "supplier": cost_info["supplier"],
            "lead_time": cost_info["lead_time"]
        })
        result["total_material"] += subtotal

    result["total_labor"] = LABOR_RATE
    result["total_testing"] = TESTING_COST
    result["total_packaging"] = PACKAGING_COST
    result["grand_total"] = result["total_material"] + LABOR_RATE + TESTING_COST + PACKAGING_COST

    return result

def get_pricing_rule(product_code):
    """定价规则 Agent: 获取产品线定价规则"""
    for prefix, rule in PRICING_RULES.items():
        if product_code.startswith(prefix):
            return rule
    return PRICING_RULES["DEFAULT"]

def calculate_suggested_price(cost_total, product_code):
    """定价 Agent: 根据产品线规则计算建议价"""
    rule = get_pricing_rule(product_code)
    suggested = cost_total / (1 - rule["target_margin"])
    min_price = cost_total / (1 - rule["min_margin"])
    return {
        "cost_total": cost_total,
        "target_margin": rule["target_margin"],
        "suggested_price": round(suggested),
        "min_price": round(min_price),
        "max_discount": rule["max_discount"],
        "product_line": product_code.split("-")[1] if "-" in product_code else product_code
    }

def check_price(cost_total, proposed_price, product_code):
    """审批 Agent: 检查价格是否符合成本要求"""
    rule = get_pricing_rule(product_code)
    min_price = cost_total / (1 - rule["min_margin"])
    actual_margin = (proposed_price - cost_total) / proposed_price

    if proposed_price >= min_price:
        return {
            "approved": True,
            "reason": f"报价 ¥{proposed_price:,.0f} ≥ 最低限价 ¥{min_price:,.0f}，毛利率 {actual_margin:.1%} ≥ {rule['min_margin']:.0%}",
            "actual_margin": round(actual_margin, 4),
            "min_margin": rule["min_margin"],
            "needs_approval": False
        }
    else:
        loss = cost_total - proposed_price
        return {
            "approved": False,
            "reason": f"报价 ¥{proposed_price:,.0f} < 最低限价 ¥{min_price:,.0f}，亏损 ¥{loss:,.0f}，毛利率 {actual_margin:.1%} < {rule['min_margin']:.0%}",
            "actual_margin": round(actual_margin, 4),
            "min_margin": rule["min_margin"],
            "needs_approval": True,
            "approval_level": "部门经理" if actual_margin > 0 else "事业部总经理"
        }

# ========== CLI ==========
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "bom_cost":
        bom_lines = json.loads(sys.stdin.read())
        print(json.dumps(get_bom_cost(bom_lines), ensure_ascii=False, indent=2))
    elif cmd == "suggest":
        cost = float(sys.argv[2])
        product = sys.argv[3] if len(sys.argv) > 3 else "DEFAULT"
        print(json.dumps(calculate_suggested_price(cost, product), ensure_ascii=False, indent=2))
    elif cmd == "check":
        cost = float(sys.argv[2])
        price = float(sys.argv[3])
        product = sys.argv[4] if len(sys.argv) > 4 else "DEFAULT"
        print(json.dumps(check_price(cost, price, product), ensure_ascii=False, indent=2))
    else:
        print("Usage: python3 cost_service.py <command> [args...]")
        print("  bom_cost        # stdin: BOM JSON array")
        print("  suggest <cost> <product_code>")
        print("  check <cost> <price> <product_code>")
