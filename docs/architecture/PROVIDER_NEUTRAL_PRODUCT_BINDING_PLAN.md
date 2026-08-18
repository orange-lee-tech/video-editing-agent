# Provider-Neutral Product Binding Plan

**状态：** IMPLEMENTATION PLAN — non-normative  
**日期：** 2026-08-19  
**依据：** Product Constitution §16.3、Architecture Contract v0.2 Provider/Model Neutrality  
**目的：** 修复普通产品壳层对 DeepSeek/Gemini/OpenAI 的角色硬绑定，同时保持既有 Domain / Application Ports / Resolver / EDL 权威完全不变。

---

# 1. 结论先行

用户配置 API 时，产品不应该问：

> “你是不是 DeepSeek / Gemini 用户？”

而应该问：

> “这个 Provider/Profile 能不能承担 **Reasoning/Direction** 或 **Vision Understanding** 这个能力角色？”

最终绑定关系：

```text
Capability Role
    ↓
Provider Profile
    ↓
Protocol Adapter
    ↓
Provider endpoint + Model + Credential
    ↓
现有 Application Port
```

Provider 仍只是 replaceable implementation；不获得 Domain ownership。

---

# 2. 当前远端实现中的 lock-in 证据

## 2.1 `adapters/product/api_settings.py`

当前：

- `SUPPORTED_VISUAL_PROVIDERS = ("gemini", "openai")`；
- Thinking 只有一个 `thinking_key`，实际默认就是 DeepSeek；
- env bridge 只认识 `DEEPSEEK_API_KEY` / `GEMINI_API_KEY` / `OPENAI_API_KEY`。

## 2.2 `adapters/product/runtime.py`

当前：

- `deepseek_model = "deepseek-v4-flash"`；
- Gemini → `gemini-3.6-flash`；
- OpenAI → `gpt-5-mini`；
- 诊断直接写 `Planning/Director requires DEEPSEEK_API_KEY`。

## 2.3 `adapters/product/composition.py`

Planning/Editing composition 直接调用：

- `deepseek_preproduction_ports(...)`；
- `deepseek_director_port(...)`。

Vision 已经比 reasoning 更中立，因为它至少通过 `visual_understanding_port(provider, model=...)` 组合。

## 2.4 Environment Doctor

当前 doctor 把 Planning/Director cloud capability 直接绑定到 `DEEPSEEK_API_KEY`。

---

# 3. 不允许怎么修

不要：

- 把 `deepseek` 字符串全局 search/replace 成 `provider` 就宣称完成；
- 让 GUI 动态 import 任意 Python class；
- 允许用户输入任意 shell/command；
- 用一个“OpenAI compatible”名义假设所有厂商语义完全一致；
- provider 报错后静默切到另一个 provider/model；
- 为了 provider neutrality 改 Resolver、canonical EDL 或 Domain entities；
- 把 API Key 写进项目 JSON/TXT/repo/log。

---

# 4. 建议的产品配置模型

## 4.1 CapabilityRole

产品层先只定义当前真实需要的角色：

```text
reasoning_direction
vision_understanding
```

未来真实能力进入普通产品后再增加：

```text
speech_recognition
embedding
music_discovery
...
```

不要预先造几十个空角色。

## 4.2 ProviderProfile

建议是用户可保存的非 Domain 配置对象，例如：

```text
profile_id
label
protocol
base_url (optional / protocol dependent)
model
credential_ref
capabilities[]
provider_metadata (bounded)
```

它是 desktop/product configuration，不是项目领域实体。

## 4.3 Protocol/Adapter

先支持**明确、经过测试的协议族**，例如：

- `deepseek_chat`（现有实现，作为 concrete adapter）；
- `openai_responses` / `openai_compatible_chat`（如果 contract 被真实测试）；
- `gemini_generate_content`；
- future `local_*` adapters。

重要：

> “Provider neutral” ≠ “所有 API 都是同一个 HTTP JSON”。

每个 adapter 仍负责：

- request schema；
- structured output；
- retry/error mapping；
- model capability validation；
- token/timeout semantics。

---

# 5. Reasoning/Direction 迁移

现有 Application Ports 已经提供正确边界：

- ScriptPlanningPort；
- ScriptProposalReviewPort；
- ShootingPlanningPort；
- ShootingProposalReviewPort；
- DirectorPort。

因此不需要改 Domain。

建议新建 product/composition-level registry/factory：

```text
ReasoningProviderBinding
  ├─ preproduction_ports()
  └─ director_port()
```

不同 concrete provider factory 产出同一组 existing ports。

第一阶段可以允许“同一个 reasoning profile 同时承担 Planning/Review/Director”，因为当前产品就是这样；以后如果真实需求出现，再允许 role split。

不要现在过度抽象出多代理拓扑。

---

# 6. Vision 迁移

现有 `VisualUnderstandingPort` / provider-neutral UnderstandingService 边界保留。

需要做的是把产品 runtime 从：

```text
if GEMINI_API_KEY ...
elif OPENAI_API_KEY ...
```

迁到显式 `VisionProviderBinding`。

UI Profile 决定：

- protocol；
- model；
- credential_ref；
- optional base_url。

Composition 再调用现有视觉 adapter factory。

---

# 7. Credential 规则

## 7.1 Profile 文件

只保存：

- profile metadata；
- opaque credential reference。

## 7.2 Windows

继续使用 user-scoped DPAPI/Credential Manager 类机制。

## 7.3 Environment variables

环境变量继续作为：

- CLI/开发/CI compatibility path；
- migration/import source。

但 GUI 不应该长期以环境变量名作为产品配置模型。

## 7.4 删除

删除 API profile 时：

- 删除/失效对应 credential secret；
- 不影响其他 profile 复用的 secret，除非有明确 reference ownership；
- 不留下 plaintext backup。

---

# 8. Capability Test

API Settings 中每个 profile 应最终提供：

`测试连接 / Test capability`

但测试必须是**能力测试**，不是只 GET 一个 endpoint。

Reasoning 最小测试：

- authentication；
- model reachable；
- bounded structured response contract。

Vision 最小测试：

- image input truly accepted；
- bounded structured response；
- 不上传用户项目真实素材，使用内置/生成的小型测试像素图即可。

测试结果可显示：

```text
✓ 可承担视觉理解
model: ...
latency: ...
```

不要把一次测试成功等同于未来 quota 永不失败。

---

# 9. Error Taxonomy

Provider-specific HTTP/error 要映射成稳定 product diagnostics：

- auth/configuration；
- unsupported model/capability；
- transient network；
- provider overload 5xx；
- rate/quota 429；
- invalid structured response；
- safety/provider refusal（如果适用）；
- cancellation/timeout。

secondary details 可以保留：

- provider label；
- protocol；
- model；
- status code；
- retry_after；
- quota_id（若安全可用）。

永不包含 API key。

---

# 10. Failover Policy

默认：**NO SILENT FAILOVER**。

如果以后允许用户配置 fallback chain，必须：

- 用户显式开启；
- 明确优先级；
- 明确成本/隐私/能力差异；
- provenance 记录实际使用的 provider/model；
- 不把 fallback provider 的结果冒充 primary provider；
- 不因 quota 自动改变 Domain semantics。

在 Stage A 当前阶段，不需要实现自动 fallback。

---

# 11. UI 目标

设置页展示：

```text
思考与编导
  配置：我的推理 API
  协议：OpenAI-compatible / DeepSeek / ...
  模型：...
  状态：✓ 已配置

视觉理解
  配置：我的视觉 API
  协议：Gemini / OpenAI-compatible / ...
  模型：...
  状态：✓ 支持图像输入
```

“DeepSeek/Gemini/OpenAI”可以出现在 provider/profile 选择中，但不再成为产品能力标题。

---

# 12. Environment Doctor 迁移

Doctor 不再问：

`有没有 DEEPSEEK_API_KEY？`

而问：

```text
Reasoning/Direction capability configured?
Vision Understanding capability configured?
```

然后由 provider binding probe 返回：

- configured/unconfigured；
- secret accessible；
- adapter/model metadata；
- optional live test（只有用户显式触发时才消耗 API）。

Doctor 默认静态检查不应偷偷烧 token/quota。

---

# 13. Persistence / Provenance

最终产品运行记录应能知道：

- 哪个 capability role；
- 哪个 profile/provider/protocol；
- 哪个 model；
- adapter/schema version；
- 请求发生时间；
- bounded cost/usage metadata（未来）；

但：

- secret 不持久化到 project；
- provider DTO 不成为 Domain authority；
- 可以保存 provenance，不保存敏感原始 request body 作为默认日志。

---

# 14. 实施分批

## Batch A — 配置模型与兼容迁移

- ProviderProfile / CapabilityBinding；
- current DeepSeek/Gemini/OpenAI 都通过新绑定表达；
- 旧 env path 保持兼容；
- 无 UI 大改。

## Batch B — Composition/Runtime Neutrality

- product runtime 不再有 `deepseek_model` 专属字段；
- composition 从 binding registry 获得 existing Ports；
- doctor 变 capability-aware；
- tests 锁定 no silent fallback。

## Batch C — UI

- capability-role cards；
- provider/profile/model/base_url；
- credential profile；
- static capability validation；
- optional explicit Test Capability。

每批都必须完整 quality gate；任何批次都不得触碰 Resolver/EDL/Renderer ownership。

---

# 15. 退出条件

Provider-neutral product binding 完成至少满足：

1. 普通 GUI 不把 DeepSeek 写成唯一“思考指挥”实现；
2. Vision 不被产品模型限制为只能 Gemini/OpenAI 两个厂家字符串；
3. 当前三个已实现 provider 路径仍有 regression；
4. 至少一种新 provider profile 可以在**不改 Domain/Application use case**的前提下接入对应 role，或通过 fixture factory 证明扩展 seam；
5. Environment Doctor 按 capability 检查；
6. secret protection 不倒退；
7. provider failure 不静默换厂；
8. full Quality Gate + Windows manual settings smoke 全绿。
