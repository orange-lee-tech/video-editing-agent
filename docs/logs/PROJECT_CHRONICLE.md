# 视频剪辑智能体项目编年史

**状态：** ACTIVE HISTORY  
**首次整理：** 2026-08-19  
**语言：** 简体中文  
**用途：** 记录“为什么这样造、何时证明了什么、哪些失败改变了设计”，避免项目只剩提交哈希而失去工程脉络。  
**权威边界：** 本文件是历史叙事与事实索引；当前真实状态仍以 `CURRENT_CONTROL_STATE.md` / `CURRENT_PHASE_STATUS.md` / `CURRENT_WORK_ORDER.md` 为准。

---

# 一、初心：不是让 AI 代替剪辑软件，而是建立 AI 导演 + AI 剪辑师

项目的根本诉求从一开始就只有两件事：

1. 根据目标、参考、商业约束，为普通用户生成**真正能拿去拍摄**的脚本与 Shooting Plan；
2. 用户把自己拍好的素材交进来后，让系统完成理解、选镜、卡点、声音、字幕、画面处理、渲染和复核，最终得到可用 MP4。

经过早期开源项目调研，长期参考路线逐渐收敛：

- FireRed-OpenStoryline：学习 pipeline / media / render 工程组织；
- MoneyPrinterTurbo：学习 provider、缓存、重试、provenance 等工程机制；
- CutClaw：只学习自动剪辑架构/算法思想，不依赖许可证变化，不复制其源码；
- BeatSync Engine：学习音乐节拍/卡点思想；
- 其他研究/开源项目只作为机制证据，不允许反过来拥有本项目 Domain。

核心工作流被固定为：

`Brief → Script → Shooting Plan → Footage → Asset Understanding → Music → BeatMap → Auto Edit → EDL → Render → Review`

后来又进一步明确：Planning-only、Editing-only、Combined 都必须成立；Planning 不能成为 Editing 的强制前置。

---

# 二、2026-08-10：仓库从“参考项目拼装”转向本地语义所有权

## 2.1 R0.1 — Shot Detection

PR #1 `R0.1-A: add pure shot boundary policy` 是一个很重要的工程风格宣言：

- 参考 FireRed 的机制；
- 先只落纯 Python boundary policy；
- 不急着把 Torch/FFmpeg/上游对象一股脑搬进来；
- 对上游会产生自相矛盾片段的情况，本项目选择 fail explicitly，而不是照抄行为。

**意义：** 从第一阶段开始，项目就选择“学思想，语义归自己所有”。

## 2.2 Product Constitution / Architecture v0.2 成形

随后产品宪法与 Architecture Contract 固化了几条以后反复救项目于跑偏的原则：

- 产品是 AI Director + AI Video Editor，不是 AI video generator；
- 商业成片中的视觉源默认只能来自用户本地素材；
- reference media 默认 analysis-only；
- Provider 是观察者/提议者，不拥有最终时间线；
- Resolver 负责 grounded source selection；
- canonical EDL 是唯一精确时间线权威；
- Renderer 只执行；Review 只检查、分类与路由；
- API/model/provider 必须可替换。

这使后面每一次“为了快速出片，要不要偷偷放宽边界”的诱惑都有了明确答案。

---

# 三、R0.2–R0.6：先把媒体事实和持久化地基打牢

Roadmap V2 将这一段总结为：

## R0.2 — Asset / Shot Identity

建立：

- immutable Asset identity；
- ffprobe ingest；
- Asset → Shot 链；
- ShotCatalog ownership。

## R0.3 — Provider-Neutral Footage Understanding

建立：

- deterministic frame sampling/extraction；
- content-addressed ArtifactStore；
- VisualUnderstandingPort；
- provider proposal → UnderstandingService owner commit。

## R0.4 — Local Structured Persistence

建立 SQLite revisioned persistence，使 Asset / Shot / ShotAnalysis 在进程重启后仍可恢复。

## R0.5 — Shot Retrieval Foundation

建立 CJK/lexical retrieval、revision-aware index 与 rebuildable ShotIndex。

## R0.6 — First Concrete Visual Provider

Gemini 成为第一个真实视觉 provider，OpenAI 作为可选适配；但它们都位于 provider seam 外侧，不拥有 ShotAnalysis 或 EDL。

**这一阶段回答的问题：**

> 我们能否先建立可靠的媒体事实、身份、持久化和 provider seam，而不是一上来让模型“直接剪视频”？

答案是可以。

---

# 四、2026-08-11～12：R0.7B 把“AI 写文案”变成可执行前期制作

R0.7B 目标是让：

`Brief → ScriptPlan → ShootingPlan`

成为正式产品链，而不是一次性聊天文本。

## 4.1 Reference Style Evidence

PR #2/#3 建立 reference-only style evidence 并把它送入前期 planning：

- reference Asset revision 明确；
- 只学习节奏、构图、结构等抽象技法；
- unavailable 维度明确写 unavailable；
- reference 不能变成 editable footage；
- 不从参考里偷出不存在的 source authority。

## 4.2 Script Duration Assessment

PR #4 增加精确 duration assessment：只报告 ScriptPlan 已声明的 duration 事实，不虚构 words-per-second 或隐藏容忍阈值。

## 4.3 第一次真实 Product Probe 给项目上了一课

第一次真实 R0.7B Product Probe 暴露：结构 schema 全对，不代表商业语义正确。

模型曾：

- 在没有依据时添加产品卖点/事实暗示；
- 在 ShootingPlan 中引入用户没有声明的拍摄地点/条件。

这推动了后续：

- Commercial Authority；
- semantic review；
- veto-only reviewer；
- bounded repair；
- factual/production constraint regressions。

历史 PR #5 最终没有直接合并，而是被 main 上更完整的设计取代。

**工程教训：** schema validation 不能替代语义 Product Gate；AI proposal 必须经过 authority/review 后才能 owner commit。

R0.7B 最终在 2026-08-12 完成 Product Ad + Natural Vlog Product Probe 与 Human Gate，正式闭环。

---

# 五、2026-08-13：R0.8 把真实素材变成 grounded evidence

R0.8 Final Closure 使用七段匿名、gitignored 的真实产品素材，在 CPU-only 路径上验证：

- FFmpeg；
- OpenCV；
- faster-whisper；
- Silero VAD；
- multilingual E5；
- motion / tracking / retrieval / speech time evidence。

关键结果包括：

- source-time evidence 可回到原素材；
- camera motion 不被简单误判为局部动作；
- hand/product interaction 能形成局部动作证据；
- tracking 有明确 target_exit，而不是伪造几何；
- speech/VAD 与 revision provenance 能跨进程恢复。

**意义：** 后面的 Resolver 第一次拥有了真正可以“站得住脚”的候选时间证据。

---

# 六、2026-08-13：R0.9 建立 Director → Retrieval → Resolver → EDL 前的核心大脑

R0.9 是项目最关键的分水岭之一。

最终链路：

`lexical/E5 → RRF → temporal evidence → CandidateWindow → Resolver/optimizer`

真实 Product Probe 产生 15 个 CandidateWindows，并由用户检查本地 preview。

Human Gate 的结论非常克制：

- visual selections：可接受；
- trim/cut points：可接受；
- Resolver 是否在广义上胜过所有基线：证据不足，不夸大；
- audio 不在该阶段范围内，不偷算成能力。

**R0.9 真正证明的是：**

> 我们能从真实用户素材得到 grounded exact source-selection plan，而不需要让 LLM 发明毫秒级时间戳。

这是“AI 调 FFmpeg”与“有权威链的自动剪辑系统”的真正区别。

---

# 七、2026-08-14：R0.10 让音乐与声音进入正式编辑决策

R0.10 完成 Music Selection + BeatMap + Audio Editorial：

- local/user-rights-attested music；
- rights-aware candidate；
- music window；
- source-audio policy；
- duck/fade/mix decision；
- post-mix QC；
- decision truth → execution truth。

真实音乐 Product Probe 中，系统在故意反转输入候选顺序时仍选择全局最优候选，证明选择不依赖 caller ordering。

用户 Human Gate 选择：

- Track B；
- selected music moment；
- structured mix；
- 无明显 audible defect。

同时项目没有掩盖 BeatMap confidence 低的事实。

**教训：** 人类接受结果 ≠ 某个内部置信度就可以偷偷被改高；证据要保留原貌。

---

# 八、2026-08-14：R0.11 Auto Reframe 从“中心裁切”走向可执行空间计划

R0.11 建立：

- provider-neutral spatial evidence；
- SpatialComposer ownership；
- SpatialTransformPlan；
- HOLD / LINEAR interpolation；
- FFmpeg canonical crop execution；
- lost observation 不伪造 geometry；
- manual locks 高于 automatic solve。

用户真实比较后偏好 stabilized 版本。

已知缺陷被保留而不是掩盖：occlusion recovery 附近有轻微 micro-jump。

另一个重要遗留：MediaPipe recovery 使用的外部 EfficientDet Lite0 模型分发条款仍为 `RELEASE_LICENSE_PENDING`，因此工程能力闭环不等于商用打包许可闭环。

---

# 九、2026-08-15～17：R0.12 把研究型引擎推向 Windows 产品执行面

R0.12 的重点从单点算法转向：

- EDL productization；
- FFmpeg Renderer；
- Subtitle；
- Preview；
- ProductFlow；
- Windows Environment Doctor；
- ordinary-user launcher。

## 9.1 Preview / Windows 现实世界验证

项目先后对 GStreamer / VLC / libmpv 等 preview 路径做真实 Windows benchmark 与 license hard gate。

过程中出现一个非常典型的工程教训：

- WSL/某些环境失败并不能代表所有 Linux/Windows 路径失败；
- real/VFR、软件 fallback、硬件路径需要分开测；
- license/build profile 是 preview 技术选择的一部分，不是“能播就行”。

## 9.2 Environment Doctor

2026-08-17 建立并关闭 Windows Environment Doctor foundation/probe，使 FFmpeg、TransNet、provider secret 等能力开始有显式 readiness 检查。

## 9.3 ProductFlow orchestration

核心提交包括：

- `c85904c...` product flow orchestration foundation；
- `bdd81db...` Resolver 正确消费 EditPlan slots；
- `5a61a4a...` canonical EDL revisions 持久化；
- `db8db211...` product-facing planning/editing flow surface；
- `1e90e2d...` ProductFlow engineering probe。

此阶段始终坚持：Engineering Probe 可以证明机械链路，但不能冒充真实 Product/Human Gate。

---

# 十、2026-08-18：普通用户 GUI 首次真正进入产品验收

## 10.1 Stage-A launcher

`c765d409...` 建立 Stage-A product launcher，`0134d0c...` 修复 Combined path，随后增加 bilingual UI。

这一天的意义是：过去藏在 CLI、probe、SQLite、domain object 中的能力第一次被迫面对“普通人是否看得懂、会不会点错、失败时知不知道发生了什么”。

## 10.2 API 设置面

先加入 session API capability settings，再加入双语界面。

但这个实现也留下新的商用架构债：UI/Runtime 把 Thinking role 直接写成 DeepSeek，把 Vision 限为 Gemini/OpenAI。它与上层已经冻结的 Provider Neutral 原则并不一致，后续必须在 adapter/composition 层修正，而不能为了修 UI 去破坏 Domain。

## 10.3 Gemini 真实兼容问题

真实 Planning 先后暴露：

- Gemini 3.6 model/structured-output contract 变化；
- response format enum；
- transient provider failures；
- provider diagnostics；
- rational frame timestamp preservation。

项目没有把这些归因于“用户环境玄学”，而是补 adapter contract + regression。

## 10.4 Planning Product/Human Gate PASS

2026-08-18，真实普通 Windows launcher 完成 Planning：

`用户输入 → persisted ScriptPlan → ShootingPlan`

用户明确认为结果可用，没有 blocking issue。

这是 Stage A 两个核心产品门中的第一个 PASS。

---

# 十一、2026-08-18：Editing Product Probe 连续撞上真实世界

## 11.1 Director `minimum_duration` 非法提案

真实 Editing-only 运行成功通过：

- project/input validation；
- local-media ingest/understanding；

然后在 Director 处失败：

`DeepSeekPlanningResponseError: invalid minimum_duration`

这证明不是“整个系统不能运行”，而是 Director provider proposal 未满足 typed contract。

修复采用 bounded repair：

- 第一次无效 proposal → 结构化拒绝原因；
- 只允许有限修复；
- 不降低 schema/Resolver 权威。

对应实现/测试序列：`e72748c...`、`49552bad...`、`607ad353...`，接受基线 `c61c7e5...`。

## 11.2 Gemini 429 / provider-directed retry

Director 修完后，真实路径继续向前，下一次失败移动到了视觉 provider：HTTP 429 quota。

项目随后补上：

- `VisualProviderTransientError.retry_after_seconds`；
- retry decorator 尊重 provider hint；
- Gemini 解析 structured RetryInfo；
- 非 transient 错误仍 fail；
- 不静默切换 provider。

接受代码基线：`af5865df...`。

**重要认知：** “limit: 20 + retry N 秒”本身不能被武断解释成“每天 20 次”或“每分钟 20 次”；quota dimension 要看真实 quotaId/dashboard。工程上先做到诚实失败和正确等待。

---

# 十二、2026-08-18～19：把配额等待时间用于 UX stabilization

因为当日 Gemini free-tier quota 已不适合继续烧真实 Editing Probe，用户决定把时间集中用于此前积累的普通用户问题。

一次 bounded Codex wave 在本地完成/候选实现：

- Tk background worker + 主线程安全 UI 更新；
- multi-select Media Files，普通 UI 移除 Media Folder；
- scroll/output export；
- 中英文状态/结果本地化；
- ETA；
- form/API profile；
- Windows protected secret seam；
- placeholder；
- share-text URL；
- no-facts repair regressions；
- quota UX；
- Splash。

随后因为 Codex 执行额度耗尽，ChatGPT + 用户通过 PowerShell 接管验收。

本地一次完整质量门得到：

- Ruff：PASS；
- mypy：225 source files PASS；
- pytest：**713 passed**；
- import-linter：3 contracts kept；
- build：PASS；
- repo doctor：PASS；
- launcher smoke：PASS；
- Tk：PASS。

人工 UI smoke 发现了一个自动测试没发现的问题：Splash 代码存在，但在 Tk event loop 进入之前就被销毁，所以真人看不到。

修复后 Splash 可见；又发现代码根本没有图像资源，于是增加一个 dependency-free Canvas 像素标记。用户最终确认：**启动图标正常**。

**这段经历再次证明：** 713 tests 全绿 ≠ 人类真的看得到那个窗口；Product/Human Gate 不能被 CI 替代。

> 注意：Splash 最后微调发生在上述完整 713-test gate 之后，因此该本地候选在最终 commit 前仍必须重跑全套质量门。

---

# 十三、2026-08-19：进入“引擎能力 → 商用桌面产品”转折点

当前新一轮产品观察提出四个必须同时推进的方向：

1. **门面：** 当前 Tk/ttk UI 功能已可用，但视觉层级、布局、按钮权重和设置体验仍明显偏工程工具；
2. **Provider Neutral：** API 应按能力角色绑定任意合适 provider/model，而不是把厂家写死成产品角色；
3. **商用包装：** 最终用户不能依赖 Python/uv/开发工作区；Windows packaging、FFmpeg/模型/license/installer/update 必须开始准备；
4. **持续记忆：** 建立本编年史和红黑榜，让成功、失败、风险和工程初心长期可检索。

这不是一个新“花活阶段”。Stage A 仍是 90%，真正的近期终点仍然是：

> **完成真实 Editing-only final MP4 Product/Human Gate。**

---

# 十四、长期工程习惯：哪些事情已经被证明值得坚持

## 14.1 真实失败比漂亮 Demo 更值钱

404、429、非法 proposal、Preview fallback、UI splash 不显示，都是系统在真实环境中给出的信息。正确动作不是绕过 gate，而是找到 owner、最小修复、回归、再走真实路径。

## 14.2 上游项目是老师，不是新老板

无论 FireRed、MoneyPrinterTurbo、CutClaw、BeatSync、GStreamer、MediaPipe 还是未来任何 provider，都必须进入本地 Port/Domain 语义；许可证与模型条款逐项审计。

## 14.3 Provider 名字不应成为产品架构

DeepSeek/Gemini/OpenAI 可以是今天的实现，但 Planning/Director/Vision 才是产品能力角色。真正可商用的软件必须允许 provider/model 被替换，而不重写核心编辑语义。

## 14.4 成片质量优先，但不能用不可追溯换质量

Final video quality 是最高产品优先级；但“为了质量”不能成为让模型绕过 Resolver、让 Renderer重写 EDL、或偷偷补公网视觉素材的理由。

## 14.5 GitHub 是长期记忆，聊天是控制室

聊天可以很长，但真正决定未来 AI 能否接手项目的是：

- Product Constitution；
- Architecture Contract；
- CAP / ADR；
- Roadmap；
- current control trio；
- validation；
- incident/probe/chronicle；
- 真实代码与 CI。

本编年史的任务，就是让这些离散事实重新拥有一条人类看得懂的时间线。
