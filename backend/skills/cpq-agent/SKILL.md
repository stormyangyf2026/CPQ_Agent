---
name: cpq-agent
description: |
  CPQ 智能配置报价助手。支持自然语言驱动的产品搜索、属性配置、约束规则验证、
  BOM展开、定价计算、CRM客户数据查询、报价单生成。触发场景：
  - 用户说"帮我配"、"配置产品"、"报价"、"生成BOM"、"查产品"、"成本核算"
  - 用户上传技术规格文档要求配置
  - 用户要求自动生成报价单或BOM清单
  - 用户问"有哪些可选"、"这个配置可以吗"、"推荐什么配置"
  - 用户需要CRM数据（客户、商机）
  CPQ后端地址：http://localhost:30000，认证方式见 scripts/cpq_api.py。
---

# CPQ Agent Skill

制造业智能CPQ（配置-定价-报价）系统的AI编排层。通过调用CPQ App REST API，
实现自然语言驱动的产品配置、BOM展开、定价计算和报价单生成。

## 使用场景

| 场景 | 触发词 |
|------|--------|
| 搜索产品 | "有哪些储能产品"、"查找电芯" |
| 配置产品 | "帮我配一台"、"选型推荐"、"推荐配置" |
| 验证配置 | "这个配置可以吗"、"检查一下规则" |
| 展开BOM | "生成BOM"、"物料清单"、"BOM清单" |
| 计算价格 | "报价"、"算一下价格"、"成本多少" |
| 查CRM数据 | "查客户"、"商机列表" |
| 生成报价单 | "出一份报价"、"生成报价单" |
| 文档配置 | 上传Excel/PDF规格书要求自动配置 |

## 认证方式

所有API调用需要Bearer Token。获取方式：

```bash
TOKEN=$(curl -s -X POST 'http://localhost:30000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123","clientId":"e5cd7e4891bf95d1d19206ce24a7b32e","grantType":"password","tenantId":"000000"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

后续请求Header：
- `clientid: e5cd7e4891bf95d1d19206ce24a7b32e`
- `Authorization: Bearer {token}`

## 工作流

### 流程1：自然语言配置报价

1. **理解意图** → 从用户输入提取：产品关键词、属性偏好、数量
2. **搜索产品** → `GET /cpq/product/model/search?keyword={keyword}`
3. **加载配置模型** → `GET /cpq/configure/model/{modelId}` 拿到属性列表
4. **智能推荐** → `POST /cpq/configure/guide?modelId={modelId}` 获取向导步骤
5. **约束验证** → `POST /cpq/configure/validate?modelId={modelId}` 验证选择
6. **展开BOM** → `POST /cpq/configure/bom-preview?modelId={modelId}` 获取物料清单
7. **计算价格** → `POST /cpq/configure/complete?modelId={modelId}&quantity={qty}` 定价
8. **呈现结果** → 格式化输出BOM清单+报价+规则验证结果

### 流程2：文档驱动配置

1. 用户上传技术规格文档（Excel/PDF）
2. 提取关键参数（电压、容量、数量、标准等）
3. 匹配CPQ产品 → 自动配置 → 验证 → 输出BOM+报价

### 流程3：报价单生成

1. 完成配置后 → 关联CRM客户/商机
2. `POST /cpq/quote/header` 创建报价单头
3. 关联BOM行项 → 返回报价单ID

## 核心API

详见 `references/cpq-api-reference.md`

| API | 方法 | 端点 |
|-----|------|------|
| 搜索产品 | GET | `/cpq/product/model/search?keyword={}` |
| 加载模型 | GET | `/cpq/configure/model/{modelId}` |
| 验证选择 | POST | `/cpq/configure/validate?modelId={}` |
| 完成配置 | POST | `/cpq/configure/complete?modelId={}&quantity={}` |
| 向导推荐 | POST | `/cpq/configure/guide?modelId={}` |
| BOM预览 | POST | `/cpq/configure/bom-preview?modelId={}` |
| 约束传播 | POST | `/cpq/engine/config/propagate?modelId={}` |
| CRM客户 | GET | `/cpq/customer/account/list` |
| CRM商机 | GET | `/cpq/crm/opportunity/list` |

## 规则引擎使用

系统有30条配置规则（`cpq_config_rule`表）。规则引擎通过 `POST /cpq/configure/validate` 自动调用，
Agent只需将用户选择传给API，引擎自动评估所有规则。

关键产品ID参考：
- 户用低压壁挂储能：EVE-LVI系列 (ID 2063-2074)
- 高压壁挂储能：EVE-HVI系列 (ID 2089-2096)
- 堆叠储能：EVE-STACK系列 (ID 2075-2082)
- 机架式储能：EVE-RACK系列 (ID 2083-2088)
- 储能集装箱：EVE-CONT系列 (ID 2184-2188)

## 输出规范

配置完成后输出结构化卡片：

```markdown
## 📋 配置结果 · {产品名称}

| 项目 | 内容 |
|------|------|
| 产品 | {modelCode} {modelName} |
| 数量 | {quantity} |
| 属性 | {属性=值列表} |
| 验证 | ✅ PASS / ⚠️ 警告 / 🛑 冲突 |

### 📦 BOM清单 ({N}项)
| # | 物料编码 | 名称 | 数量 | 单位 |
|---|----------|------|------|------|
| 1 | MAT-001 | xxx | 12 | PCS |

### 💰 报价
- 基准价：¥{basePrice}
- 折扣后：¥{netPrice}
- 币种：{currency}
```
