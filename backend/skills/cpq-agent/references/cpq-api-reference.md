# CPQ App API Reference

> 后端地址：`http://localhost:30000`
> 所有响应格式：`{"code":200,"msg":"ok","data":...}`
> 分页响应：`{"code":200,"msg":"ok","rows":[...],"total":N,"size":10,"current":1}`

## 认证

```
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123",
  "clientId": "e5cd7e4891bf95d1d19206ce24a7b32e",
  "grantType": "password",
  "tenantId": "000000"
}

→ { "code":200, "data": { "access_token":"eyJ..." } }
```

## 产品

| 端点 | 说明 |
|------|------|
| `GET /cpq/product/model/list` | 产品列表（分页） |
| `GET /cpq/product/model/search?keyword=HVI&configType=ATO` | 搜索产品 |
| `GET /cpq/product/model/search?keyword=Germany&configType=ATO` | 关键词搜索 |

### 产品Model字段
`modelId, modelCode, modelName, configType, defaultBomId, basePrice, currency, leadTimeDays, description`

configType枚举：`STANDARD` / `ATO` / `CTO` / `ETO` / `BUNDLE`

## 配置器

| 端点 | 说明 | 请求/响应 |
|------|------|-----------|
| `GET /cpq/configure/model/{modelId}` | 加载配置模型 | 返回：attributes、bomLines、basePrice等 |
| `POST /cpq/configure/validate?modelId={}` | 验证属性选择 | Body: `{"颜色":"珍珠白","基站":"标准版"}` → ValidationResult |
| `POST /cpq/configure/complete?modelId={}&quantity=10` | 完成配置 | 返回：validation + mbomLines + price |
| `POST /cpq/configure/guide?modelId={}` | 向导下一步 | Body: 当前selections → GuideStep |
| `POST /cpq/configure/bom-preview?modelId={}` | BOM预览 | Body: selections → MbomLine[] |

### ValidationResult
```json
{
  "status": "PASS|SOFT_FAIL|HARD_FAIL",
  "errors": ["错误1"],
  "warnings": ["警告1"]
}
```

### GuideStep
```json
{
  "state": "QUESTIONING|NARROWING|RECOMMENDING|CONFIGURING|COMPLETED",
  "currentAttribute": "属性名",
  "options": [{"code":"", "label":"", "available":true, "recommended":false, "reason":""}],
  "recommendation": "推荐说明",
  "prohibited": {},
  "attributeOptions": {"属性名":["可选值"]}
}
```

### MbomLine
```json
{
  "mbomLineId": 123, "sbomLineId": 456, "modelId": 2091,
  "lineNumber": 1, "materialCode": "MAT-LF304", "materialDesc": "LF304电芯",
  "materialType": "CELL", "quantity": 192, "unit": "PCS",
  "requirementType": "REQUIRED", "costComponent": "BATTERY",
  "leadTimeDays": 30, "sortOrder": 1
}
```

### ConfigCompleteResponse
```json
{
  "validation": { ... },
  "mbomLines": [ ... ],
  "price": {
    "basePrice": 3980000, "bomCost": 0, "bestMatchPrice": 3980000,
    "tierAdjustedPrice": 3980000, "discountPct": 0,
    "netPrice": 3980000, "needsApproval": false,
    "approvalReason": null, "pricingDetail": null
  }
}
```

## 配置引擎

| 端点 | 说明 |
|------|------|
| `POST /cpq/engine/config/validate?modelId={}` | 引擎级验证 |
| `POST /cpq/engine/config/propagate?modelId={}` | 约束传播（返回每属性的可用/禁用选项） |
| `POST /cpq/engine/config/guide?modelId={}` | 向导步骤 |
| `GET /cpq/engine/config/compatibility?sourceProductId={}&targetProductId={}` | 跨产品兼容检查 |
| `GET /cpq/engine/bom/explodeFlat/{sbomHeaderId}` | BOM展开 |

## CRM

| 端点 | 说明 |
|------|------|
| `GET /cpq/customer/account/list` | 客户列表 |
| `GET /cpq/crm/opportunity/list` | 商机列表 |

## 报价

| 端点 | 说明 |
|------|------|
| `GET /cpq/quote/header/list` | 报价单列表 |
| `POST /cpq/quote/header` | 创建报价单头 |

## 价格相关

| 端点 | 说明 |
|------|------|
| `POST /cpq/engine/pricing/calculate?productModelId={}&quantity={}&currency=CNY` | 定价计算 |
| `POST /cpq/engine/pricing/calculate?productModelId={}&quantity=1&currency=CNY&requestedDiscount=5` | 带折扣定价 |

## 配置规则关键产品ID

| 产品 | ID | configType |
|------|----|-----------|
| EVE-LVI-5.0 5.12kWh | 2063 | STANDARD |
| EVE-LVI-10.0-P 10.24kWh | 2067 | ATO |
| EVE-LVI-20.0 20.48kWh | 2069 | ATO |
| EVE-HVI-40.0 40.96kWh | 2091 | ATO |
| EVE-HVI-60.0 61.44kWh | 2092 | ATO |
| EVE-STACK-B25K 25.6kWh | 2079 | ATO |
| EVE-CTP-30K 30kWh | 2058 | ATO |
| EVE-CONT-5M 5MWh | 2185 | ETO |
| EVE-AIO-100K 100kW/200kWh | 2190 | ETO |
| EVE-PCS-100K 100kW | 2196 | ATO |
