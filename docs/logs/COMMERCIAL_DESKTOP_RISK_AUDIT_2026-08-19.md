# 商用桌面化大排查 — 2026-08-19

**状态：** STATIC AUDIT SNAPSHOT  
**范围：** 当前 `main` + 已知 Stage-A Product Probe / Windows 实测 + Packaging / Provider / UI 商用边界。  
**注意：** 这是一轮证据导向的静态大排查，不宣称替代未来 clean-machine security review、fuzz、installer probe 或完整代码逐行审计。

---

# 0. 审计原则

本轮首先保护核心生产关系：

```text
Provider / local analysis
        ↓
proposal / evidence
        ↓
Director
        ↓
Resolver
        ↓
canonical EDL
        ↓
Renderer
        ↓
Review
```

任何“改善 UX / 增加 Provider / 打包”都不得把 source-window authority 偷给 LLM、UI、Renderer 或第三方库。

---

# 1. P0 — 当前必须盯住

## P0-01 Editing Product/Human Gate 尚未完成

**类型：** Product gate  
**证据：** 当前 Stage A 仍 90%；Planning PASS；Editing Engineering PASS，但真实 final-MP4 Product/Human Gate OPEN。

最新真实 Editing 路径已经推进到视觉 provider，失败原因从 Director typed proposal 移到了 Gemini HTTP 429 quota。

**处理：** provider quota 恢复后继续真实 Editing-only gate；不得用 synthetic probe/GUI 完成度替代。

---

## P0-02 Product adapter/runtime 的 Provider lock-in 与上层原则不一致

**类型：** Architecture implementation debt  
**状态：** VERIFIED

当前远端：

- `api_settings.py` 将视觉 provider 限为 Gemini/OpenAI；
- Thinking key 实际绑定 DeepSeek；
- `runtime.py` 写死 DeepSeek/Gemini/OpenAI 默认模型和环境变量；
- `composition.py` 直接调用 DeepSeek planning/director factories；
- Environment Doctor 直接检查 `DEEPSEEK_API_KEY`。

而 Product Constitution / Architecture Contract 已明确 provider/model 可替换。

**处理：** 按 `PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md` 在 adapter/composition 层迁移。禁止借机改 Domain/Resolver/EDL。

---

## P0-03 本地 UX 候选尚未形成远端 accepted baseline

**类型：** Release/process risk  
**状态：** VERIFIED

用户本地已有大批 Tk UX 改动；一次完整 gate 曾达到：

- 713 pytest PASS；
- Ruff/mypy/import-linter/build/repo-doctor PASS；
- launcher/Tk smoke PASS；
- API profile plaintext-secret smoke PASS。

但之后又补了 Splash repaint 与 Canvas pixel mark。

**处理：** 最终 commit 前完整重跑 gate；本审计期间 GitHub 不碰同一批 UI source files，以免覆盖本地工作树。

---

## P0-04 Windows 正式打包依赖闭包未建立

**类型：** Commercial release blocker  
**状态：** VERIFIED

`pyproject.toml` 当前普通 dependencies 为空；真实 launcher 仍依赖 `uv run --with transnetv2-pytorch==1.0.5 ...` 一类开发路径。

**影响：** 开发机能跑 ≠ 客户机能装。

**处理：** 先做 reproducible PyInstaller `onedir` probe，再决定 onefile/installer。详见 `WINDOWS_DESKTOP_PACKAGING_READINESS.md`。

---

## P0-05 FFmpeg / 外部模型分发仍有 license gate

**类型：** Legal/distribution blocker  
**状态：** VERIFIED

- ADR-001 明确禁止随便重分发未知 third-party FFmpeg binary；
- exact version/config/external libs/hash/build recipe/notices/codec review 都是 release gate；
- R0.11 EfficientDet Lite0 模型仍 `RELEASE_LICENSE_PENDING`。

**处理：** packaging 之前完成 release manifest；optional unresolved model 不进入 default bundle。

---

# 2. P1 — 高价值稳定性问题

## P1-01 输出路径会由 FFmpeg `-y` 覆盖已有文件

**类型：** Data-safety / UX  
**状态：** VERIFIED

Renderer 已正确阻止 output path 与 canonical source media 相同，这是红榜能力；但 FFmpeg invocation 当前包含 `-y`。

因此如果用户选择一个已存在的非源 MP4，底层执行允许覆盖。

**建议：**

- Controller/UI 在任务开始前检查目标是否已存在；
- 普通用户明确选择 `覆盖 / 另存为 / 取消`；
- 默认建议新文件名更安全；
- Renderer 继续保持 execution-only，不把确认逻辑塞进 EDL。

---

## P1-02 多实例同时打开同一项目的写冲突语义不明确

**类型：** Desktop concurrency  
**状态：** RISK — static inference

SQLite repository 使用 transaction + `BEGIN IMMEDIATE`，能提供数据库层写锁；但当前 `ProjectWorkspace.open()` 没看到 application-level project lease/instance lock。

**风险：** 用户双开应用、同时打开同一 project，可能出现锁等待、写失败、认知混乱；默认 sqlite timeout 也不是完整产品 UX。

**建议：**

- 先做 multi-process same-project probe；
- 若冲突真实存在，增加 project lease/read-only fallback 或明确“该项目正在另一个实例使用”；
- 不用隐藏重试掩盖并发冲突。

---

## P1-03 ProjectWorkspace 打开即创建目录/SQLite，缺少更明确的 writable preflight

**类型：** Filesystem UX  
**状态：** VERIFIED behavior / risk inference

`ProjectWorkspace.open()` 会 `mkdir`、初始化 `project.sqlite3`、`provider_audio`、artifact store。

**风险场景：**

- OneDrive/网络盘；
- Program Files/只读目录；
- U 盘；
- 中文/长路径；
- 磁盘空间不足；
- 杀软/同步软件锁文件。

**建议：** 在真正创建 project 前做轻量 writable/disk/path preflight，失败给普通用户可理解说明。

---

## P1-04 运行取消机制尚未形成 owner-safe 链

**类型：** Responsiveness/recovery  
**状态：** OPEN

本地 UX 候选已把长任务移出 Tk 主线程，这是必要基础，但当前没有证据表明：

- provider HTTP call；
- Shot analysis loop；
- FFmpeg render；
- Review

已经拥有统一 cancellation token / safe interruption semantics。

**建议：** 不先加“取消”按钮。先定义 cancel owner、artifact state、child process termination、restart/resume 规则，再暴露 UI。

---

## P1-05 同一 Editing run 中按 Shot 顺序调用视觉 provider，quota shaping 仍不足

**类型：** Cloud reliability/cost  
**状态：** VERIFIED architecture + Product Probe evidence

每个 detected Shot 会调用 UnderstandingService；provider 单次可携带多帧，但多 Shot 仍会形成多次请求。

目前已有：

- transient retry；
- provider retry-after；
- 429 fail honest；

仍缺：

- provider-specific rate/concurrency budget；
- per-run API call estimate；
- usage/cost telemetry；
- quota dimension 结构化展示。

**建议：** rate policy 保持 product/provider boundary，不让 quota 反向修改 Resolver evidence semantics。

---

## P1-06 Error taxonomy 仍有 adapter-specific 文本泄漏到产品面的风险

**类型：** UX/diagnostics  
**状态：** PARTIALLY REPAIRED

本地 UX 候选已增加 common localization，但 provider/domain exception 体系仍广泛存在于内部。

**建议：** 统一：

`stable product summary + optional bounded technical detail + repair action`

同时保留原始 error provenance 供日志/诊断，不在主界面直接甩 Python class name。

---

## P1-07 `tkinter_app.py` 继续成为大文件的风险

**类型：** Maintainability  
**状态：** VERIFIED trend

Codex UX wave 对 Tk launcher 增加数百行。部分 profile/ETA/secret helper 已下沉 `ux_support.py`，方向正确。

**建议：** 下一轮商业壳层继续拆：

- theme/design tokens；
- widgets/sections；
- provider settings presentation；
- platform/resource helpers；
- orchestration state presenter。

不要为“拆文件”改核心流程，只分离 UI concern。

---

## P1-08 普通用户不知道项目目录里哪些是“自己的资料”、哪些是内部 artifacts

**类型：** Product mental model  
**状态：** UX gap

ProjectWorkspace 里有：

- `project.sqlite3`；
- `artifacts/`；
- `provider_audio/`；
- 用户 output。

普通用户未来可能手工清理/移动时误删内部数据。

**建议：**

- 项目目录结构文档化；
- UI 用“打开项目目录 / 打开输出目录”区分；
- 不鼓励用户直接编辑内部 SQLite/artifacts；
- future project export/archive 明确哪些内容可重建。

---

## P1-09 临时文件与中间 subtitle artifact 的生命周期要做 crash probe

**类型：** Cleanup/recovery  
**状态：** NEEDS PROBE

LocalArtifactStore 已采用 temp file + fsync + `os.replace`，这一点很稳健；Renderer 也会生成隐藏 `.subtitles.ass` 中间文件。

**仍需证明：**

- FFmpeg crash/kill 时 subtitle/temp file 是否残留；
- 重跑是否安全；
- failed render 是否留下被误认为成功的 MP4；
- cleanup 不会删除 canonical artifact。

---

## P1-10 Preview/runtime 与 Packaging 之间存在潜在“开发机路径通过、安装包路径失败”风险

**类型：** Frozen-resource/runtime discovery  
**状态：** HIGH LIKELIHOOD

项目历史中已有 private GStreamer/runtime、软件 fallback、独立环境差异等经验。

**建议：** 所有 executable/model/resource 查找统一走 resource/runtime locator；Environment Doctor 必须在 frozen app 模式重复验证，不能只验证 PATH。

---

# 3. P2 — 产品质量与扩展性

## P2-01 UI 还没有真正的商业信息层级

已单独建立 `DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`。

重点不是加皮肤，而是：

- Header / workflow / inputs / status / results 分区；
- Primary CTA；
- selected-media summary；
- result vs run-log；
- capability-role settings；
- 高 DPI / 键盘 / 中英文布局。

---

## P2-02 Recent projects / open output folder / copy result / Doctor entry 值得加入

这些是“工作效率”能力，不涉及编辑核心语义。

加入原则：

- 有真实 backend 再显示；
- 不保存 secret；
- recent project 只保存路径/非敏感 meta；
- Doctor 默认静态检查不烧 API。

---

## P2-03 Planning 的 placeholder 文案仍过长

当前本地 UX 候选 placeholder 已解决“空白不知道填什么”，但截图中重复 `此行必填/此行可空置，示例：...` 造成视觉密度高。

下一轮建议：

- required/optional 放 label/help；
- placeholder 只保留短示例；
- 复杂解释用 tooltip/help line；
- placeholder 仍绝不能提交为真实值。

---

## P2-04 Auto Reframe 与 BeatMap 已知 minor limitations 不应被“美化阶段”遗忘

- R0.10 某真实样本 BeatMap confidence 低；
- R0.11 occlusion recovery 有 micro-jump。

这些不是当前 Stage-A blocker，但要继续留在红黑榜，等 corpus 扩大再判断是否系统性。

---

# 4. 安全/生产关系检查结果

本轮复查几个负载点，没有发现需要立刻推翻核心架构的证据：

## Renderer

- 使用 typed `DeterministicToolInvocation`；
- `subprocess.run([...], shell=False)`；
- source/output conflict 有显式 guard；
- canonical EDL 先 validate；
- unsupported automation fail closed。

这条生产关系应保留。

## ArtifactStore

- content-addressed SHA-256；
- temp file → fsync → `os.replace`；
- read 时 hash/size integrity check。

这条存储机制是稳定资产，不要为 UI 改造。

## SQLite

- schema versioning；
- explicit migration；
- foreign keys ON；
- write transaction rollback。

未来要补的是 desktop concurrency/product UX，而不是重做 persistence。

---

# 5. 推荐施工顺序

在不破坏当前本地 UX 候选的前提下：

1. **先把本地 UX candidate 最终 gate + commit + CI 接受**；
2. quota 可用后完成 Editing Product/Human Gate；
3. Provider-neutral product binding，限定 adapter/composition；
4. commercial UI shell polish，限定 product adapter/UI；
5. first Windows onedir packaging Engineering Probe；
6. fresh machine + license manifest；
7. 再决定 installer/update/onefile。

不要把 2～5 混成一个巨型 commit。

---

# 6. 本轮没有做的事

为了保护本地未提交工作，本轮 GitHub 审计**没有**：

- 远程修改 `tkinter_app.py`；
- 改 Provider production code；
- 改 Resolver；
- 改 EDL；
- 改 Renderer；
- 改 Review；
- 宣布 Stage A PASS/100%；
- 引入新的 UI/framework/runtime dependency。

这不是保守不干活，而是避免 GitHub 远端提交与用户 Windows 本地候选互相覆盖。
