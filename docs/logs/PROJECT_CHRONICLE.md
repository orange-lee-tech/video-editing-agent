# 视频剪辑智能体项目编年史

**状态：** ACTIVE HISTORY  
**首次整理：** 2026-08-19  
**最近更新：** 2026-08-22  
**语言：** 简体中文  
**用途：** 记录“为什么这样造、何时证明了什么、哪些失败改变了设计”，避免项目只剩提交哈希而失去工程脉络。  
**权威边界：** 本文件是历史叙事与事实索引；当前真实状态仍以 `CURRENT_CONTROL_STATE.md` / `CURRENT_PHASE_STATUS.md` / `CURRENT_WORK_ORDER.md` 为准。  
**编日体规则：** 以自然日为最小历史单位；同一天可以包含多个阶段/PR，但不再把不同日期混成一个“模糊阶段”。早期详细叙事保留，下面的每日索引负责提供稳定日粒度入口。

---

# 每日索引

- **2026-08-09** — 长期技术路线收敛：FireRed-OpenStoryline 作骨架参考、MoneyPrinterTurbo 作素材/供应体系参考、CutClaw 只学自动剪辑架构思想、BeatSync Engine 作音乐卡点参考；核心工作流固定为 Brief → Script → Shooting Plan → Footage → Understanding → Music/BeatMap → Auto Edit → EDL → Render → Review。
- **2026-08-10** — 仓库从“拼参考项目”转向本地语义所有权；R0.1–R0.6 地基、Product Constitution、Architecture Contract、Asset/Shot identity、provider-neutral understanding、SQLite、retrieval、Gemini/OpenAI seam 成形。
- **2026-08-11** — R0.7B 将 Brief → ScriptPlan → ShootingPlan 产品化；reference style evidence、duration assessment、真实 Product Probe 暴露“schema 正确但商业语义错误”的问题。
- **2026-08-12** — Commercial Authority、semantic review、veto-only reviewer、bounded repair、ProductionLocation 等约束落地；R0.7B Product Ad + Natural Vlog Product/Human Gate 闭环。
- **2026-08-13** — R0.8 真实素材 grounded evidence 与 R0.9 Director/Retrieval/Resolver 链闭环；真实素材开始产生可回到 source-time 的证据和可接受的 exact source selection。
- **2026-08-14** — R0.10 Music/BeatMap/Audio Editorial 与 R0.11 Auto Reframe 落地；真实音乐 Human Gate 和 stabilized spatial result 被接受，同时保留置信度与 license 未闭环事实。
- **2026-08-15** — R0.12 从算法研究转向 EDL、Renderer、Subtitle、Preview、ProductFlow、Windows 产品执行面；开始对真实桌面运行和分发约束负责。
- **2026-08-16** — Preview real/VFR + software fallback 继续真实 Windows 验证；Stage-A Product I/O 影响被系统审计，确认“能播/能跑”不能替代 license、fallback、真实媒体证据。
- **2026-08-17** — Windows Environment Doctor、ProductFlow orchestration、canonical EDL persistence、reference acquisition、Engineering Probe 等集中收口；机械链与 Product/Human Gate 被明确分离。
- **2026-08-18** — ordinary-user launcher 真正进入产品验收；Planning Product/Human Gate PASS；Editing 连续暴露 Director proposal、Gemini quota 等真实 blocker，并启动 UX stabilization。
- **2026-08-19** — UX stabilization、commercial desktop shell、profile/DPAPI/ETA/Splash 等完成大幅现代化；PR #10 合并；Editing audio/media I/O 与 packaging dependency inventory 进入最后收尾。
- **2026-08-20** — 1.0 Editing 音频/字幕语义进一步收敛：默认原声、rights-safe public BGM、basic subtitle、TTS/高级分离延后；public music、SOURCE_AUDIO、字幕/voice capability、中文本地化等 dirty wave 经过完整工程验证。
- **2026-08-21** — 无讲话素材真实 Human Gate 先因 `faster-whisper` 被错误强制触发而失败，随后修成 `SKIPPED/NO_SPEECH/CAPABILITY_UNAVAILABLE` 明确语义；最终无讲话自动剪辑 Human PASS。PR #11 合并；随后完成仓库注意力/文档治理 PR #12，加入 `AGENTS.md`、Registry、archive 默认禁读、control-plane 刷新，并打开 bounded reference compatibility wave。
- **2026-08-22** — Bilibili bounded acquisition 工程 fallback 证明可行，但产品重新确认：参考视频的目标是“AI 看懂并反馈给指挥官”，不是默认完整下载后做剪辑级解析。由于当前 Gemini/OpenAI visual adapter 仅支持图片帧，provider-neutral remote/video observation 延后到 2.0；1.0 普通 GUI 隐藏 reference URL、保留本地参考。PR #13 合并。下一波转向 Project Workspace + UX consolidation，再进入 Windows packaging。

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

这不是一个新“花活阶段”。真正的近期终点仍然是：完成真实 Editing-only final MP4 Product/Human Gate，并在此基础上收口 Stage A。

---

# 十四、2026-08-20：Editing 1.0 音频、字幕与能力边界收敛

这一日的核心不是再加更多声音功能，而是明确**什么是 1.0，什么必须诚实延期**。

逐步确认：

- ordinary Editing 默认保留真实素材原声；
- rights-safe public BGM 可以自动获取并进入 BeatMap / Audio Editorial / canonical EDL；
- basic subtitles 必须来自可信 speech evidence，不能伪造；
- production synthetic voice 没有真实 backend 时不应暴露成普通成功路径；
- TTS 保留 typed `SpeechSynthesisPort` seam，但实际 backend 延后；
- advanced speech/ambience separation 保留 `AudioSeparationPort` seam，但高级分离/混音延后到 2.0；
- GUI 不应让用户点击一个必然因为无 TTS backend 而失败的普通控制；
- SOURCE_AUDIO、BGM、voice、subtitle 的 stage attribution 必须分开，不能所有失败都糊成一个阶段。

Public music、Wikimedia rights/acquisition、source audio、subtitle style/codec/ASS execution、中文本地化和一批 ProductFlow tests 被统一进同一条 dirty closeout wave。

这一日的工程经验是：

> “有一个 port”不等于“产品已经有这项能力”；1.0 的能力表面必须和真实 runtime 对齐。

---

# 十五、2026-08-21：无人声 Human Gate、PR #11 与仓库治理

## 15.1 最简单的无人声素材先把系统问倒了

真实无人讲话视频从：

`ingest → understanding → public music → BeatMap → EditPlan → Resolver → canonical EDL → SOURCE_AUDIO/BGM`

一路成功，最后却在 subtitle stage 因未安装 `faster-whisper` 整体失败。

这暴露了一个典型生产线语义错误：

- “没有字幕要生成”被错误等价成“整个视频不能编辑”。

修复后明确区分：

- `NO_SPEECH`；
- `SKIPPED`；
- `CAPABILITY_UNAVAILABLE`；
- real failure。

无可信 speech evidence 时不伪造字幕，SOURCE_AUDIO + BGM + Renderer/Review 继续；已有 grounded speech 且需要字幕但 runtime 不可用时，才在 subtitle stage 准确 fail closed。

用户重新真人运行后确认：**自动剪辑成功，原声有，rights-safe BGM 有且自然，无字幕路径正常。**

这是 Stage-A Editing 的第一条真正 ordinary Human PASS 基线。

## 15.2 PR #11 结算

长期积累的 33 文件 dirty wave 被统一提交为：

`feat: close Stage A editing audio and subtitle integration`

exact-head CI 通过后，PR #11 合并进 main。

## 15.3 仓库注意力治理

为了避免后续 ChatGPT/Codex 在 archive、缓存、历史噪声中反复消耗注意力，随后完成 PR #12：

- root `AGENTS.md`；
- `docs/DOCUMENT_REGISTRY.json`；
- 自动 exhaustive document manifest；
- `docs/archive/** = EXCLUDED_DEFAULT`；
- document lifecycle/update-date policy；
- live trio 刷新；
- repo doctor / governance 联锁；
- 旧 UX wave 归档；
- Codex entry 改为显式 release/closed 状态。

治理 PR 首轮被机器抓到 `EXCLUDED_DEFAULT` token 与 Ruff format/lint 问题，修复后 CI / repository-governance / document-registry 三线全绿再 merge。

这使“少读、读对、及时归档/刷新”第一次从口头习惯变成仓库机器约束。

---

# 十六、2026-08-22：参考 URL 退回 2.0，Project Workspace 成为下一条主线

## 16.1 Bilibili 工程 fallback 证明可行

Codex 在 bounded provider adapter 内完成：

- public BV page metadata；
- anonymous pagelist/playurl；
- HTTPS/CDN 重验证；
- SSRF/DNS/public-IP/IP-pinning/redirect/MIME/size/timeout；
- provenance / BVID；
- video-only ingest；
- ffprobe；
- TransNet shot detection。

真实 `BV1Mq4y187xR` 达到 acquisition、ffprobe、ingest、7-shot detection PASS。

## 16.2 产品意图重新压过“技术上能下载”

随后重新澄清参考视频的真实任务：

> 用户给一个爆款/参考链接，是希望视觉/多模态 API **看懂它**，再把结构化观察反馈给指挥官 API；不是要求本地软件默认把参考视频完整下载并做剪辑级时间解析。

当前 Gemini/OpenAI visual adapter 都是 image-frame oriented，不提供稳定 provider-neutral remote/video-native observation contract。

因此做出 1.0/2.0 边界决定：

- `ReferenceObservationPort` / remote-video-native observation / provider upload-media path → 2.0；
- Bilibili acquisition 保留为 fallback engineering seam；
- ordinary 1.0 Tkinter Planning 隐藏 reference URL；
- local reference video 保留；
- 不继续追 Douyin/Xiaohongshu URL 产品兼容。

PR #13 exact-head CI PASS 后 squash merge。

## 16.3 Project Workspace 从“路径字段”升级为产品结构

新的 UX 判断进一步确认：第一行项目路径不应该消失，而应该真正成为**一次视频工作的 Project Workspace**。

下一波准备目标：

- Planning / Editing 共享一个 top-level Project Workspace；
- project-specific cache/work/autosave/undo-redo/log/output 都归到 workspace；
- canonical Domain persistence 不复制；
- 默认成片输出进入 project-local outputs；
- configuration import/export/save/delete 合并到主窗口；
- form-level Clear / Undo / Redo；
- 内容目标/参考与拍摄条件、成片目标/素材与输出改成纵向可折叠区；
- 临时像素摄影机 mark 退休，优先恢复此前被用户认可的羽毛 identity；
- 完成这些再进入 Windows onedir packaging，避免把开发型路径/交互冻结进安装包。

---

# 十七、长期工程习惯：哪些事情已经被证明值得坚持

## 17.1 真实失败比漂亮 Demo 更值钱

404、429、非法 proposal、Preview fallback、UI splash 不显示、无人声视频被字幕 runtime 卡死，都是系统在真实环境中给出的信息。正确动作不是绕过 gate，而是找到 owner、最小修复、回归、再走真实路径。

## 17.2 上游项目是老师，不是新老板

无论 FireRed、MoneyPrinterTurbo、CutClaw、BeatSync、GStreamer、MediaPipe 还是未来任何 provider，都必须进入本地 Port/Domain 语义；许可证与模型条款逐项审计。

## 17.3 Provider 名字不应成为产品架构

DeepSeek/Gemini/OpenAI 可以是今天的实现，但 Planning/Director/Vision 才是产品能力角色。真正可商用的软件必须允许 provider/model 被替换，而不重写核心编辑语义。

## 17.4 成片质量优先，但不能用不可追溯换质量

Final video quality 是最高产品优先级；但“为了质量”不能成为让模型绕过 Resolver、让 Renderer 重写 EDL、或偷偷补公网视觉素材的理由。

## 17.5 GitHub 是长期记忆，聊天是控制室

聊天可以很长，但真正决定未来 AI 能否接手项目的是：

- Product Constitution；
- Architecture Contract；
- CAP / ADR；
- Roadmap；
- current control trio；
- validation；
- incident/probe/chronicle；
- 真实代码与 CI。

本编年史的任务，就是让这些离散事实重新拥有一条人类看得懂、按日可追踪的时间线。
