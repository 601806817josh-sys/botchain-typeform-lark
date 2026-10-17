# BOT Chain Typeform → Lark 自动化

## 当前唯一数据标准

- Typeform 表单 ID：通过服务器环境变量 `TYPEFORM_FORM_ID` 配置，不写入仓库。
- Typeform 中每个实际填写问题均映射为 Lark 独立字段。
- Typeform 因条件跳转而未展示的问题，在 Lark 中保持为空。
- 一次 Typeform 提交对应 Lark 中一条申请记录。
- `Typeform 提交 ID` 用于幂等去重。

## 负责人路由

| Typeform 申请类型 | 负责人 |
|---|---|
| 生态扶持奖励 / Ecosystem Support Incentive | Evan |
| Gas返佣 / Gas Rebate | Evan |
| 活动合作 / Event Collaboration | Chris、Evan |
| 孵化加速 / Incubation Accelerator | Moses |

申请类型为多选时，合并所有对应负责人并去重，仍只创建一条申请记录。

## Lark Base 结构

- `总申请表`：保存公共字段、Typeform 提交 ID、原始响应和分流状态。
- `生态扶持奖励`：Evan 负责。
- `Gas返佣`：Evan 负责。
- `活动合作`：Chris、Evan 共同负责。
- `孵化加速`：Moses 负责。

多选申请先写总申请表，再分别写入选中的业务表；业务表通过 `关联总申请` 和 `Typeform 提交 ID` 关联总表。

## 实施顺序

1. 创建并核对 Lark 多维表格。
2. 开发 Typeform Webhook → Lark 写入与群通知。
3. 部署到服务器并联调。
4. 上传 GitHub，补充部署和维护文档。
