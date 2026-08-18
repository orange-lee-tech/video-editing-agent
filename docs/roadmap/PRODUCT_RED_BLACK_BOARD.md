# 产品红黑榜

**状态：** ACTIVE DASHBOARD  
**首次建立：** 2026-08-19  
**最后更新：** 2026-08-19 — Stage-A Editing 集成审计  
**用途：** 用普通人能快速理解的方式，持续记录已经被证据证明的核心优势，以及尚未解决的攻关目标/风险。  
**权威边界：** 本文件是动态看板，不替代 Product Constitution、Architecture Contract、`CURRENT_CONTROL_STATE.md`、`CURRENT_PHASE_STATUS.md` 或 `CURRENT_WORK_ORDER.md`。

---

## 使用规则

1. **红榜只收已被代码、CI、Engineering/Product/Human Gate 或正式 validation 支撑的事实。** 不把愿望写成优势。
2. **黑榜不是“项目失败清单”。** 它记录尚未闭环、需要持续盯住的产品问题、工程风险和商用化门槛。
3. 某项从黑榜解决后，应写明闭环证据，再移入红榜或归档；不要静默删除历史问题。
4. 红黑榜不能改变核心生产关系：Provider 只提议/观察，Resolver 选择源窗口，canonical EDL 拥有精确时间线，Renderer 只执行，Review 只分类/路由。
5. Stage-A 结构进度仍受 `STAGE_A_COMPLETION_GATE.md` 约束；UI 美化、测试全绿或文档完善都不能单独把 90% 提到 100%。

---

# 红榜 — 已验证的核心功能与优势

## R1. 产品方向没有被“AI 生成视频”带偏

产品已经冻结为 **AI Director + AI Video Editor**：

- 前期：Brief → ScriptPlan → ShootingPlan；
- 后期：用户本地素材 → 理解 → Director → Resolver → EDL → Renderer → Review → MP4；
- 商业成片视觉素材默认只来自用户本地文件；
- 参考视频默认只用于分析，不会偷渡进最终素材候选。

**价值：** 避免为了“看起来自动化”而牺牲商业可控性、版权边界和可追溯性。

## R2. 精确剪辑时间不交给 LLM 猜

R0.9 已用真实素材证明 grounded Resolver 能从真实证据生成精确 source window，canonical EDL 独占最终时间线权威；LLM/VLM 不拥有最终时间戳。

**价值：** 这是软件从“聊天机器人调用 FFmpeg”走向可靠编辑系统的关键分界线。

## R3. 真实素材证据链已经建立

R0.8 在 CPU 路径上完成真实素材验证：镜头、语音/VAD、运动、跟踪、检索等证据能够映射回原始 source time，并在重启后保持 revision/provenance。

**价值：** 后续编辑决策可以基于证据，而不是基于文件名或模型想象。

## R4. 音乐/音频决策不是隐藏魔法

R0.10 完成真实音乐 Product/Human Gate：

- rights-aware 音乐候选；
- BeatMap/音乐窗口；
- source-audio policy；
- structured mix；
- decision truth 与 execution truth 对齐；
- 原始音乐和视频未被破坏。

**价值：** 自动剪辑不只“切画面”，而是已经拥有一套被真实 Human Gate 验证过的可审计听觉编辑机制。当前缺口是把它接回普通 ProductFlow，而不是重新造一套。

## R5. Auto Reframe 已有真实产品证据

R0.11 的 provider-neutral 空间链路在真实素材上完成 Product/Human Gate；用户偏好 stabilized 结果。空间观察者不拥有可执行裁切，`SpatialComposer`/`SpatialTransformPlan` 保持权威边界。

**价值：** 为横竖屏混合素材进入短视频生产提供了非生成式、可解释的基础。当前同样是普通 ProductFlow 集成问题，不是能力从零问题。

## R6. Windows 执行与诊断基础不是纸面设计

R0.12 前已建立 Environment Doctor、FFmpeg/ffprobe、TransNetV2 等 Windows 运行时检查与 probe；当前真实用户机器已完成多轮 launcher/product probe。

**价值：** 项目持续以“普通 Windows 用户最终能运行”为约束，而不是只在开发机/CI 上自洽。

## R7. Planning 普通用户门已经 PASS

2026-08-18，普通 Windows launcher 完成真实 Planning：用户输入 → 持久化可检查 ScriptPlan → 可执行 ShootingPlan；用户明确判定可接受。

**价值：** 两个核心产品能力中的第一个已经有真实普通用户证据，而不仅是单元测试。

## R8. 真实失败会反向修正系统

近期真实 Product Probe 已连续暴露并修复：

- Gemini 3.6 structured-output 兼容；
- transient transport 诊断与重试；
- rational timestamp 传递；
- DeepSeek Director `minimum_duration` 非法提案的 bounded repair；
- Gemini provider-directed retry delay / HTTP 429 处理。

**价值：** “测试全绿”不被当作产品正确性的替代品；真实用户路径持续给工程系统施加压力。

## R9. 核心依赖方向有自动化守门

Import-linter 当前持续约束：

- Domain 不依赖外层；
- Application 通过 Ports 依赖能力；
- Providers 不依赖 Adapters。

**价值：** UI、厂家 API、FFmpeg 等可以迭代而不应反向吞掉核心 Domain ownership。

## R10. API secret 已进入正确的产品安全方向

当前本地 UX 候选已做 Windows protected credential / profile smoke；用户用假 key 验证 profile TXT 中没有明文 secret。

**状态说明：** 该成果仍在 Windows 本地未提交候选中，必须在最终 commit + CI 后才能升级为远端 accepted baseline。

---

# 黑榜 — 未解决问题 / 重大攻关目标 / 隐患

## B0. 普通 Editing ProductFlow 尚未接齐 Stage-A 必须的编辑表达链【最高优先级 / Gate Blocker】

2026-08-19 大排查发现：**我们已有不少强能力，但普通“一键自动剪辑”编排没有把它们全部接进来。**

冻结的 Stage-A Gate 要求：

`Resolver → music/rhythm + spatial/audio + subtitle/graphics/minimal transitions → canonical EDL → Renderer/Review`

但当前 `build_editing_product_flow()` 实际只把：

- media understanding；
- Director；
- grounded Resolver；
- conservative source audio；
- EDLBuilder；
- Renderer / Review

接成了普通产品路线。

当前没有在该 route 中提供：

- 已有 R0.10 MusicSelection / BeatMap / Audio Editorial 决策；
- 已有 R0.11 Spatial / Auto Reframe 决策；
- structured Subtitle product wiring；
- Stage-A 要求的 basic title/CTA/price-card graphics；
- minimum transition vocabulary。

**危险：** 如果不纠正控制面，我们可能拿到一个“能播放的纯切 MP4”就误判 Stage A 完成。

**闭环条件：** 先做一个 bounded integration repair，复用既有 capability owners，把批准的决策真正送入 EDLBuilder；对 graphics/transition 只补 Stage-A 所需的小型 typed semantics；再通过 decision→EDL→render 集成测试，之后才允许真实 Editing Gate。

## B1. Editing 普通用户 Product/Human Gate 仍未闭环【P0】

当前状态已从“等 Gemini 配额”升级为：

- Planning Product/Human Gate：PASS；
- Editing subsystem mechanisms：已有大量 PASS 证据；
- Editing ordinary ProductFlow integration：OPEN；
- Product Probe：在 B0 修复前 **NOT GATE-READY**；
- Human Gate：OPEN。

**闭环条件：** B0 修复 → 用户本地素材走完整自动链 → 真实 final MP4 → source hash 不变 → Review PASS → 用户实际观看并判断可用。

## B2. 普通产品壳层存在明显 Provider/Vendor 锁定【P0 商用架构债】

虽然 Constitution/Architecture 已明确 Provider Neutral，但当前远端产品壳层仍硬编码：

- Thinking/Planning/Director → `DEEPSEEK_API_KEY` / DeepSeek adapter；
- Vision → Gemini/OpenAI 两项枚举；
- runtime 默认模型直接写死 `deepseek-v4-flash`、`gemini-3.6-flash`、`gpt-5-mini`；
- Environment Doctor 也把 reasoning capability 绑定到 DeepSeek 环境变量。

**目标：** UI 和 product runtime 以“能力角色”配置，厂家/协议/模型只是可替换绑定；不得通过这次改造改变 Domain/Resolver/EDL ownership，也不得静默 provider fallback。

实施计划：`docs/architecture/PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md`。

## B3. 本地 UX stabilization 候选还没有最终 commit/CI【P0 流程风险】

已观察：完整本地 Quality Gate 曾为 713 passed，人工 UI smoke 通过；之后又补了 Splash 真正显示与像素标记。

**风险：** 最终 Splash 微调发生在上一次完整 713-test gate 之后。

**必须做：** 最终提交前重跑 formatter / Ruff / mypy / full pytest / import-linter / build / diff-check / repo-doctor / launcher smoke；先本地 commit，再 rebase 最新 docs main，push 后远端 CI 复审。

## B4. 当前 Tk/ttk 主界面功能可用，但产品门面与信息层级不足【P1】

真实截图显示：

- 表单横向铺满、层级弱；
- 必填/可选说明重复占据 placeholder；
- Primary/Secondary 按钮视觉权重接近；
- 运行状态、输入、结果区缺乏清晰分区；
- 设置窗口仍更像工程配置面板而不是商用应用设置。

**目标：** 在不换核心 UI 技术栈、不引入重型主题依赖的前提下，建立 design tokens、卡片/分组、明显主 CTA、状态栏、结果动作区和更好的高 DPI/键盘/窗口布局。

设计基线：`docs/product/DESKTOP_UI_DESIGN_SYSTEM_V0.1.md`。

## B5. 输出覆盖 UX 仍需商用级确认【P1】

Renderer 当前 FFmpeg invocation 使用 `-y`，并已防止 output 覆盖 canonical source media；但普通用户仍需要明确处理“目标 MP4 已存在”的覆盖确认/版本策略，避免误覆盖已有成片。

## B6. 取消 / 恢复 / 失败重试尚未形成完整普通用户语义【P1】

后台线程让 UI 不再冻结是必要基础，但商用长任务还需要：

- 安全 Cancel；
- provider wait 可见；
- 失败后从最小必要阶段恢复；
- 不留下伪成功输出/半成品状态；
- 不因取消而破坏 canonical artifacts。

在真正机制完成前，不应加一个装饰性“取消”按钮。

## B7. 打包分发尚未闭环【P0 商用发布门】

当前 `pyproject.toml` 没有普通 runtime dependencies，真实 Windows 启动仍会使用 `uv run --with transnetv2-pytorch==1.0.5 ...` 这类开发/验证路径；普通客户不能被要求安装 uv/Python/模型依赖。

还需闭环：

- Windows private runtime / executable bundle；
- FFmpeg/ffprobe 分发配置和许可证；
- TransNetV2 runtime/weights 分发边界；
- 可选 MediaPipe recovery 模型的 redistribution 条款；
- 图标/字体/模型/notice 资源定位；
- 首次启动与无 Python/uv 机器 smoke；
- installer/update/rollback。

准备基线：`docs/operations/WINDOWS_DESKTOP_PACKAGING_READINESS.md`。

## B8. 外部依赖许可证仍有几个发布级硬门【P0】

已知包括：

- FFmpeg 构建配置会改变 LGPL/GPL/非自由组件义务；
- R0.11 的 EfficientDet Lite0 外部模型仍是 `RELEASE_LICENSE_PENDING`；
- 预览候选的插件/build license 需要按实际发行包审查；
- 上游 `REFERENCE-*` 只能学习机制，不能自动转化为可复制代码。

## B9. 真实视觉 API 成本/配额与调用整形还不够产品化【P1】

当前 understanding 按 Shot 调视觉 provider，一次 request 可包含多帧；已处理 transient retry 与 provider retry hint，但仍缺：

- provider quota identifier 的一致结构化诊断；
- 对不同供应商限制的 rate shaping / concurrency policy；
- 可观察的调用量/成本预算；
- 能力降级策略（明确失败，而不是伪装等价或静默换厂）。

## B10. 自动视觉语义质量仍需要更广真实素材证据【P1 核心质量】

R0.9 closure 明确记录：当时语义检索部分仍用了 human-confirmed managed-corpus coverage text；当前 Stage-A Editing 正是在继续验证真实 VisualUnderstanding 驱动完整链路。

**目标：** 让用户随手投入的无序素材，而不是人工整理描述，真正驱动 Resolver 与最终成片。

## B11. BeatMap / Auto Reframe 仍有已知质量尾巴【P2 质量扩展】

- R0.10 real-music probe 中存在低 BeatMap confidence 样例，虽未影响该次 Human Gate；
- R0.11 occlusion recovery 有轻微 micro-jump；
- 需要更广 corpus 才能判断是否系统性问题，不能因为单样本继续盲调参数。

## B12. `tkinter_app.py` 膨胀风险【P1 可维护性】

本轮 UX 候选对 Tk launcher 增加了大量界面行为。应继续把：

- design tokens/theme；
- profile/credential；
- ETA/status；
- provider binding；
- platform helpers

维持为可测试的小模块，避免 GUI 文件重新变成“万能上帝文件”。

## B13. 多实例/项目目录/磁盘/长路径等桌面边界仍需系统验证【P1】

后续 fresh-Windows / packaging probe 至少覆盖：

- 同一项目多实例打开；
- 中文/Unicode/长路径；
- 无写权限目录；
- 低磁盘空间；
- 网络中断；
- provider timeout/429/5xx；
- FFmpeg 异常退出；
- 临时文件清理；
- Windows Defender/杀软常见行为；
- 日志脱敏；
- 崩溃重启后项目可恢复。

---

# 当前一句话状态

> **我们并不是“缺剪辑算法”，而是已经有很多被独立验证过的能力，却还差最后一段关键工作：把这些能力真实接入普通用户的一键 Editing ProductFlow；在这条主线之外，再逐步完成 Provider Neutral、商业 UI 与 Windows 可分发性。**
