# video-editing-agent

**最后更新：** 2026-09-18

**Last updated:** 2026-09-18

一款**本地优先、以证据为依据的 AI 导演 + AI 视频剪辑器**，面向用户提供的原始视频素材。

A **local-first, evidence-grounded AI Director + AI Video Editor** for user-supplied footage.

初始产品重点：Windows 桌面端、商业短视频、电商/产品广告和 Vlog，主要面向 60 秒以内的视频。

Initial product focus: Windows desktop, commercial short-form video, ecommerce/product advertising and Vlog, primarily under 60 seconds.

## 两项核心产品功能 | Two Core Product Functions

Stage-A 结构完备性合同要求普通 Windows 用户能够真正使用以下两项功能；该验收门槛现已通过。

The Stage-A structural-completion contract required both of the following functions to be genuinely usable by an ordinary Windows user. That gate has now been accepted.

### 1. 规划 | Planning

`reference/high-performing/commercial intent`
`→ Brief`
`→ persisted inspectable ScriptPlan`
`→ executable ShootingPlan`

用户应当能够直接获得可执行的拍摄脚本/计划，而不必编辑仓库文件或手动构造内部 Domain 对象。

The user should be able to obtain a practical shooting script/plan without editing repository files or constructing internal Domain objects.

### 2. 剪辑 | Editing

`user-selected local footage + editing intent`
`→ media understanding/evidence`
`→ Director/EditPlan`
`→ Retrieval/Resolver`
`→ music/spatial/audio/subtitle/graphics/minimal transitions`
`→ canonical EDL`
`→ Renderer/Review`
`→ final MP4`

自动化产品路径不得依赖人工手写 EditPlan、ResolutionDecision 或 EDL。

The automatic product path must not depend on a human hand-authoring EditPlan, ResolutionDecision or EDL.

仅规划、仅剪辑和组合模式都是合法的产品使用路径。组合模式可以将规划产物作为可选的精确版本补充信息；规划功能不是启用剪辑功能的许可证或前置授权。

Planning-only, Editing-only and Combined are all legitimate product paths. Combined uses Planning artifacts as optional exact-revision enrichment; Planning is not an activation license for Editing.

## 产品边界 | Product Boundary

这**不是**通用的文本生成视频工具，也不是自主素材库视频生成器。视觉素材覆盖不足时，应明确提示用户，而不是悄悄用下载或生成的图片替代。

This is **not** a generic text-to-video or autonomous stock-footage generator. Missing visual coverage is surfaced to the user instead of silently replaced with downloaded/generated imagery.

最终视觉媒体来自用户提供的本地视频素材，并受当前产品宪法约束。服务商/LLM 的输出可以提出建议或推理，但不能决定源素材时间戳、Domain 权限或最终时间线位置。

Final visual media comes from user-supplied local footage under the active Product Constitution. Provider/LLM output may propose/reason, but it does not own source timestamps, Domain authority or final timeline placement.

## 当前状态——不要在此复制过时快照 | Current State — Do Not Duplicate Stale Snapshots Here

Stage A 结构性建设已 **100% 完成**，稳定版 **v1.0.0** 已发布。目前没有正在执行的产品建设工单；发布后的安全与签名治理正在审查中。

Stage A structural construction is **complete at 100%**, and stable **v1.0.0** is published. There is currently no active product-construction work order; post-release security/signing governance is under review.

当前阶段/审查状态、精确授权边界、已接受基线和产品门禁均以以下文件中的实时信息为准：

Current phase/review state, exact authorization boundary, accepted baselines and Product Gates are live in:

- [当前控制状态](docs/operations/CURRENT_CONTROL_STATE.md)
  [Current control state](docs/operations/CURRENT_CONTROL_STATE.md)
- [当前阶段状态](docs/roadmap/CURRENT_PHASE_STATUS.md)
  [Current phase status](docs/roadmap/CURRENT_PHASE_STATUS.md)
- [当前工作工单](docs/operations/CURRENT_WORK_ORDER.md)
  [Current work order](docs/operations/CURRENT_WORK_ORDER.md)

结构性 100% 完成合同见：

The hard structural 100% contract is documented in:

- [Stage A 完成门禁](docs/roadmap/STAGE_A_COMPLETION_GATE.md)
  [Stage A completion gate](docs/roadmap/STAGE_A_COMPLETION_GATE.md)

不要根据旧提交说明、带日期的 README 文案、聊天记录或特定阶段的源代码包快照推断当前进度。

Do not infer current progress from old commit notes, dated README prose, chat history or phase-specific source-pack snapshots.

仓库治理会自动检查实时状态文档的指向；如果任一核心产品门禁不是 PASS，则会拒绝不实的 Stage-A 100% 完成声明。

Repository governance machine-checks the live-state pointers and rejects a false Stage-A 100% claim when either core Product Gate is not PASS.

## 持久化产品流水线 | Durable Product Pipeline

```text
Brief
→ ScriptPlan
→ ShootingPlan
→ user-supplied footage
→ Asset / Shot understanding
→ speech + temporal evidence
→ Music / BeatMap
→ Director / EditPlan
→ Retrieval / Resolver
→ Spatial + Audio decisions
→ EDLBuilder
→ EDL
→ Renderer
→ Review / repair
→ final MP4
```

并行入口架构意味着：仅剪辑模式可以从 Brief/编辑意图和本地视频素材直接开始，不需要伪造 ScriptPlan 或 ShootingPlan。

The parallel-entry architecture means Editing-only may begin from Brief/editorial intent + local footage without fabricated ScriptPlan/ShootingPlan.

## 权威文件与导航 | Authority and Navigation

从 [`docs/README.md`](docs/README.md) 开始阅读。

Start with [`docs/README.md`](docs/README.md).

规范文件的优先级顺序：

Normative order:

1. [产品宪法 V1.0](docs/product/PRODUCT_CONSTITUTION_V1.0.md) — 最高产品权威；
   [Product Constitution V1.0](docs/product/PRODUCT_CONSTITUTION_V1.0.md) — highest product authority.
2. [架构合同 V0.2](docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md) — 当前有效架构基线；
   [Architecture Contract V0.2](docs/architecture/ARCHITECTURE_CONTRACT_V0.2.md) — active architecture baseline.
3. [能力规格](docs/capabilities/) — 当前有效的能力规格；
   [Capabilities](docs/capabilities/) — active capability specifications.
4. [架构决策记录](docs/adr/) — 当前有效的架构决策；
   [Architecture Decision Records](docs/adr/) — active architecture decisions.
5. [路线图 V2](docs/roadmap/ROADMAP_V2.md) — 持久化 Stage-A 建设地图及历史顺序参考；
   [Roadmap V2](docs/roadmap/ROADMAP_V2.md) — durable Stage-A construction map and historical sequencing reference.
6. 实时控制状态 / 工作工单；
   Live control state / Work Order.
7. 实现代码 / 测试 / 服务商行为。
   Implementation / tests / provider behavior.

已退役文档位于 [`docs/archive/`](docs/archive/)，仅用于追溯历史。

Retired documents live under [`docs/archive/`](docs/archive/) and are preserved for provenance only.

## 不得偏移的产品规则 | Product Rules That Must Not Drift

- 商业视频的视觉源素材必须来自用户提供的本地文件。
  Commercial visual source material must come from user-supplied local files.
- 缺失镜头素材应转化为待解决事项/补拍建议，不得自动回退到素材库或生成式替代。
  Missing footage becomes unresolved/reshoot guidance, not autonomous stock/generated fallback.
- LLM/服务商输出是建议或证据，不是 Domain 或时间线权威。
  LLM/provider output is proposal/evidence, not Domain or timeline authority.
- 精确媒体时间使用规范化有理数类型 `MediaTime` / `MediaTimeRange`。
  Exact media time uses canonical rational `MediaTime` / `MediaTimeRange`.
- Resolver 不得在有依据的证据范围之外虚构源素材时间戳。
  Resolver cannot invent source timestamps outside grounded evidence.
- BeatMap 描述音乐，不负责决定视频切点。
  BeatMap describes music; it does not own video cuts.
- EDL 是唯一可执行时间线的权威来源。
  EDL is the sole executable timeline authority.
- Renderer 只执行经过验证的 EDL，不创建、修复或重新定位编辑决策。
  Renderer executes validated EDL; it does not create, repair or reposition editorial decisions.
- Engineering Probe 与 Product Probe 证据不同：合成测试夹具可以证明工程机制，不能证明真实剪辑的实用性。
  Engineering Probe and Product Probe evidence are different: synthetic fixtures may prove machinery, not real editing usefulness.
- 权利与来源必须明确；未知权利状态不得被悄悄提升为已验证。
  Rights/provenance remain explicit; unknown rights are never silently promoted to verified rights.
- Stage-A UI 可以视觉简洁，但必须实用、易懂、可控且可扩展。
  Stage-A UI may be visually plain, but must be practical, understandable, controllable and extensible.
- 普通用户操作不得要求编辑仓库文件或手动构造 Domain/EDL。
  Normal user operation must not require repository-file editing or manual Domain/EDL construction.

## 仓库地图 | Repository Map

- `.github/` — CI 和可复现的探测/维护工作流。
  CI and reproducible probe/maintenance workflows.
- `docs/` — 产品、架构、路线图、ADR、验证、日志和运维控制平面。
  Product, architecture, roadmap, ADR, validation, log, and operations control plane.
- `docs/archive/` — 为来源追溯而保留的退役文档。
  Retired documentation preserved for provenance only.
- `LICENSE` / `NOTICE` — 仓库范围内的 Apache-2.0 许可证和项目自有材料署名声明。
  Repository-wide Apache-2.0 license and attribution notice for project-authored material.
- `LICENSES/` — 第三方许可证文本的暂存/保留策略；第三方材料仍受其自身条款约束。
  Third-party license-text staging/retention policy; third-party material remains under its own terms.
- `scripts/` — 仓库/开发者辅助脚本及历史独立探测脚本。
  Repository/developer helper scripts and historical standalone probes.
- `src/` — 生产环境 Python 软件包。
  Production Python package.
- `tests/` — 单元/集成/契约测试及可再分发测试夹具。
  Unit/integration/contract tests and redistributable fixtures.
- `tools/` — 开发者、证据和维护工具；阶段探测工具位于 `tools/probes/`。
  Developer/evidence/maintenance tooling; phase probes live under `tools/probes/`.

本地/私有媒体、工具链和探测输出均有意加入 Git 忽略规则，不应进入 GitHub。

Local/private media, toolchains and probe outputs are intentionally gitignored and do not belong in GitHub.

## 开发与验证 | Development and Verification

Python 版本要求：**3.12+**。

Python requirement: **3.12+**.

典型环境初始化：

Typical environment setup:

```powershell
uv sync --frozen
```

仓库质量门禁：

Repository quality gate:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv run lint-imports
uv build
git diff --check
```

仓库/控制平面健康检查：

Repository/control-plane health check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/maintain.ps1 doctor
```

开启新对话时，重新观察 `origin/main`，并使用实时控制状态/工作工单路径；不要仅凭聊天记忆重建当前工作。

At the start of a new conversation, reobserve `origin/main` and use the live control-state/Work-Order path. Do not reconstruct current work from chat memory alone.

## 上游策略 | Upstream Strategy

当前战略参考项目包括：

Strategic references currently include:

- FireRed-OpenStoryline — 流水线、媒体和渲染工程参考；
  FireRed-OpenStoryline — pipeline/media/render engineering reference.
- MoneyPrinterTurbo — 服务商/素材供应的运营思路参考，绝不作为自动素材库回退方案；
  MoneyPrinterTurbo — provider/asset-supply operational ideas, never automatic visual-stock fallback.
- CutClaw — 仅作剪辑架构/算法参考；未复制其源代码；
  CutClaw — editing architecture/algorithm reference only; source is not copied.
- BeatSync Engine — 节拍/音乐同步参考；
  BeatSync Engine — beat/music synchronization reference.
- TransNetV2 — 镜头检测推理参考。
  TransNetV2 — shot-detection inference reference.

当前有效的上游治理文件：

Active upstream governance:

- [上游组件 V2](docs/upstream/UPSTREAM_COMPONENTS_V2.md)
  [Upstream Components V2](docs/upstream/UPSTREAM_COMPONENTS_V2.md)
- [上游策略 V2](docs/upstream/UPSTREAM_POLICY_V2.md)
  [Upstream Policy V2](docs/upstream/UPSTREAM_POLICY_V2.md)

## 代码签名策略 | Code Signing Policy

项目为正式 Windows 版本维护公开的[代码签名策略](CODE_SIGNING_POLICY.md)。

The project maintains a public [Code signing policy](CODE_SIGNING_POLICY.md) for official Windows releases.

项目的 SignPath Foundation 申请获批后，生产 Windows 版本将使用 **SignPath.io 提供的免费代码签名，证书由 SignPath Foundation 提供**。该策略记录签名团队角色、多因素认证要求、可信 GitHub Actions 构建边界、人工审批要求、第三方二进制边界、制品元数据和事件处理规则。

Upon approval of the project's SignPath Foundation application, production Windows releases will use **Free code signing provided by SignPath.io, certificate by SignPath Foundation**. The policy documents the signing-team roles, MFA requirement, trusted GitHub Actions build boundary, manual approval requirement, third-party binary boundary, artifact metadata, and incident rules.

当前 `v1.0.0` 发布早于 SignPath Foundation 签名，因此不会被标记为已通过 SignPath 签名。

The current `v1.0.0` release predates SignPath Foundation signing and is not represented as SignPath-signed.

隐私和外部服务商行为见 [`PRIVACY.md`](PRIVACY.md)。

Privacy and external-provider behavior are documented in [`PRIVACY.md`](PRIVACY.md).

## 许可证 | License

本仓库中由项目编写的材料采用 **Apache License, Version 2.0（Apache-2.0）** 许可证。详见 [`LICENSE`](LICENSE)、[`NOTICE`](NOTICE) 和 [`LICENSE_STATUS.md`](LICENSE_STATUS.md)。

Project-authored material in this repository is licensed under the **Apache License, Version 2.0** (`Apache-2.0`). See [`LICENSE`](LICENSE), [`NOTICE`](NOTICE), and [`LICENSE_STATUS.md`](LICENSE_STATUS.md).

打包和引用的第三方组件仍遵循各自的许可证和审查门禁；详见 [`LICENSES/README.md`](LICENSES/README.md) 及运行时第三方声明。

Bundled and referenced third-party components remain under their respective licenses and review gates; see [`LICENSES/README.md`](LICENSES/README.md) and the runtime third-party notices.
