# Architecture Contract v0.1
## Script-Driven Personal Video Editing Agent

**状态：Draft Baseline**  
**目标：在创建正式仓库之前冻结核心领域对象、依赖方向与模块边界。**

---

# 0. 核心工作流

系统主链固定为：

**Brief → ScriptPlan → ShootingPlan → Footage → Asset Understanding → Music → BeatMap → EditPlan → EDL → Render → ReviewReport**

其中：

- `Footage` 不是独立领域对象，而是进入系统的 `Asset`
- `Music` 在 v0.1 中不单独建立领域对象，而表示一个 `Asset(kind=audio)`；其音乐分析结果由 `BeatMap` 承载
- `Render` 是执行过程，输出视频文件等 Artifact，不定义为核心领域对象

因此 v0.1 的九个核心领域对象正式定义为：

**Brief / ScriptPlan / ShootingPlan / Asset / Shot / BeatMap / EditPlan / EDL / ReviewReport**

---

# 1. 全局架构原则

## 1.1 领域对象高于具体 AI、API 与框架

以下内容都不能成为领域模型本身：

- OpenAI / Claude / Gemini / DeepSeek
- MCP
- LangChain / LiteLLM
- MoviePy
- FFmpeg
- Pexels / Pixabay / Coverr
- FireRed
- MoneyPrinterTurbo
- CutClaw

这些全部属于 **Adapter / Provider / Infrastructure**。

系统真正长期存在的资产是：

`ScriptPlan`

`ShootingPlan`

`Asset`

`Shot`

`BeatMap`

`EditPlan`

`EDL`

等对象。

即使未来全部模型、供应商和渲染后端都更换，领域模型不应因此重构。

---

# 2. 通用对象规则

所有持久化核心对象统一具有：

- `id`
- `revision`
- `schema_version`
- `created_at`
- `created_by`
- `derived_from`
- `status`

建议 ID 语义前缀：

- Brief：`brf_*`
- ScriptPlan：`scp_*`
- ShootingPlan：`shp_*`
- Asset：`ast_*`
- Shot：`sht_*`
- BeatMap：`btm_*`
- EditPlan：`edp_*`
- EDL：`edl_*`
- ReviewReport：`rvr_*`

具体 UUID / ULID 技术暂不在 v0.1 冻结。

## 2.1 revision 原则

对象不是被无痕覆盖，而是产生新 revision。

例如：

`scp_xxx@1`

修改文案后成为：

`scp_xxx@2`

任何下游对象都必须引用**确切 revision**，不能只引用模糊的对象 ID。

因此未来系统可以准确回答：

> 这条 EDL 究竟依据的是哪一版脚本？

---

# 3. Brief

## 3.1 定义

`Brief` 是整个项目的**创作意图源头**。

它回答：

> 我要做什么视频？

而不是：

> 具体怎么剪？

## 3.2 核心内容

Brief 包含：

- 视频目的
- 发布平台
- 目标受众
- 目标时长
- 横竖屏要求
- 核心信息
- 内容主题
- 情绪与风格
- 参考文案
- 参考视频
- 爆款案例
- 禁止出现的内容
- 品牌约束
- 用户特殊要求
- 成功标准

## 3.3 明确禁止

Brief **不得包含**：

- asset_id
- shot_id
- 视频源时间戳
- EDL segment
- FFmpeg 参数
- 某个具体 AI 模型

Brief 是“意图”，不是执行方案。

---

# 4. ScriptPlan

## 4.1 定义

`ScriptPlan` 是对 Brief 的**叙事展开**。

它回答：

> 这个视频应该怎么讲？

ScriptPlan 不是单纯的一大段文案。

它应该是结构化叙事计划。

## 4.2 核心结构

一个 ScriptPlan 包含若干 Narrative Section。

每个 Section 至少描述：

- section_id
- narrative_role
  - hook
  - setup
  - development
  - proof
  - climax
  - CTA
  - outro
- narration / spoken text
- subtitle intent
- target_duration
- emotion
- pacing
- visual_intent
- information_goal
- transition_intent

例如：

> Hook：前三秒必须说明“35 年木匠第一次尝试把传统手艺带到海外”。

这里定义的是叙事要求。

不是某个具体镜头。

## 4.3 ScriptPlan 与 FireRed 的关键区别

FireRed 当前主要是：

**Footage → Script**

我们的主流程正式定义为：

**Brief → ScriptPlan → ShootingPlan → Footage**

已有素材驱动脚本仍可未来作为特殊模式存在，但不是系统默认因果关系。

---

# 5. ShootingPlan

## 5.1 定义

`ShootingPlan` 是：

**ScriptPlan → 可执行拍摄需求**

它回答：

> 为了实现这个脚本，我应该拍什么？

这是本项目区别于普通 AI 自动视频生成器的重要领域对象。

## 5.2 核心单位：ShotRequirement

`ShotRequirement` 暂时作为 ShootingPlan 内部结构，不提升为顶级领域对象。

包含：

- requirement_id
- script_section_ref
- purpose
- subject
- action
- environment
- framing
  - wide
  - medium
  - close-up
  - macro
- camera_motion
- orientation
- target_duration
- minimum_duration
- desired_take_count
- priority
  - required
  - preferred
  - optional
- audio_requirement
- dialogue_requirement
- visual_constraints
- continuity_hint
- search_queries
- source_policy

### source_policy

非常重要：

例如：

- `captured_only`
- `local_preferred`
- `remote_allowed`
- `remote_only`
- `generated_allowed`

这样系统才能知道：

> 这个镜头必须本人拍摄，还是缺失以后可以去 Pexels 补。

## 5.3 明确禁止

ShootingPlan 不绑定实际：

- Asset
- Shot
- 文件路径
- source timestamp

它描述的是**需求**，不是素材选择结果。

---

# 6. Asset

## 6.1 定义

`Asset` 是系统中一个**真实媒体资源的身份对象**。

可以是：

- 用户拍摄视频
- 用户导入视频
- 图片
- 音频
- BGM
- 公网素材
- AI 生成素材

## 6.2 一个 Asset 对应一个源媒体

Asset 至少包含：

### Identity
- asset_id
- media_kind
  - video
  - image
  - audio

### Origin
- captured
- imported
- remote
- generated

### Storage
- storage_ref
- content_hash
- file_size

### Technical Metadata
- duration
- width
- height
- fps
- codec
- sample_rate
- channels

### Provenance
- provider
- provider_asset_id
- source_page
- creator
- retrieved_at
- license_information
- attribution

## 6.3 强约束

**Asset 源内容一旦完成 ingest，不允许原地替换。**

如果文件内容改变：

> 创建新的 Asset。

不能出现：

`asset_001`

今天指向 A.mp4，

明天悄悄变成 B.mp4。

这是素材可追溯性的底线。

---

# 7. Shot

## 7.1 定义

`Shot` 是：

> Asset 内具有剪辑意义的一个时间区间。

因此：

**Asset ≠ Shot**

一个 5 分钟视频是一个 Asset。

里面可能产生：

`Shot 001`

`Shot 002`

...

`Shot 057`

## 7.2 Shot 基础身份

- shot_id
- asset_ref
- source_start
- source_end
- duration
- boundary_method
- previous_shot_ref
- next_shot_ref

## 7.3 Shot Understanding

Shot 可以附加：

### Technical
- blur
- exposure
- shake
- resolution_quality

### Visual
- people
- faces
- objects
- actions
- environment
- framing
- camera_motion

### Semantic
- caption
- keywords
- emotion
- topic
- aesthetic_score

### Speech
- transcript
- speakers
- dialogue_type

### Retrieval
- embedding_ref

### Structure
- scene_ref
- neighbor_refs

## 7.4 Shot ID 稳定规则

如果只是：

- caption 改进
- embedding 更换
- 新增人物识别
- 新模型重新评分

则：

**Shot ID 不变，只产生新的分析 revision。**

如果：

**source_start / source_end 发生实质变化**

则视为新的 Shot。

---

# 8. BeatMap

## 8.1 定义

`BeatMap` 是对一个音乐 Asset 的**客观音乐结构分析结果**。

它回答：

> 音乐发生了什么？

而不是：

> 视频应该在哪里切？

这是非常关键的边界。

## 8.2 BeatMap 包含

- beatmap_id
- audio_asset_ref
- duration
- bpm
- confidence
- beats[]
- downbeats[]
- accents[]
- phrase_anchors[]
- sections[]
- energy_curve
- onset_curve
- drops[]
- build_ups[]
- breakdowns[]
- chorus_ranges[]
- optional time_signature

音乐 Section 可以表示：

- Intro
- Verse
- Chorus
- Bridge
- Build-up
- Drop
- Outro

## 8.3 明确禁止

BeatMap 不应该包含：

> 在 13.2 秒切镜头。

因为：

**音乐出现强拍 ≠ 视频必须切。**

BeatMap 是事实层。

剪辑决策属于 EditPlan。

这意味着：

**BeatSync Engine / FireRed / CutClaw 的音乐算法提供分析信号，但不能拥有最终 Timeline。**

---

# 9. EditPlan

## 9.1 定义

`EditPlan` 是系统真正意义上的**导演方案**。

它回答：

> 这个故事应该如何剪？

但仍然不回答：

> 最终具体截取哪个文件的第几秒。

因此：

**EditPlan ≠ EDL**

这是整个架构最重要的边界之一。

## 9.2 EditPlan 输入

一个 EditPlan 可以引用：

- Brief revision
- ScriptPlan revision
- ShootingPlan revision
- 当前 AssetCatalog 状态
- BeatMap revision
- 用户剪辑指令

## 9.3 核心单位：EditSlot

EditSlot 暂时作为内部结构。

例如：

### SLOT-001
目的：

> 强 Hook

时间预算：

> 0–2.5 s

需要：

> 木匠工作细节特写

来源策略：

> captured_only

节奏：

> aggressive

音乐：

> Align near phrase anchor，允许提前/延后 200 ms

转场：

> hard cut

这里依然没有：

`C:\videos\abc.mp4 13.4–15.7s`

## 9.4 EditPlan 可以包含

- slot_id
- script_section_ref
- shot_requirement_refs
- narrative_role
- target_duration
- pacing
- desired_visual
- selection_constraints
- candidate_policy
- music_alignment_policy
- transition_intent
- continuity_policy
- reuse_policy
- source_policy

可以存在：

`candidate_shot_refs`

作为推荐候选。

但这些候选**不是最终剪辑承诺**。

---

# 10. EDL

## 10.1 定义

`EDL — Edit Decision List`

是：

> 完全确定的、机器可执行的视频编辑方案。

这里第一次真正冻结：

**哪个素材、哪一段、放在哪里。**

## 10.2 EDLSegment

每个 segment 包含：

- segment_id
- timeline_track
- asset_ref
- optional shot_ref
- source_in
- source_out
- timeline_in
- timeline_out
- playback_rate
- crop
- scale
- position
- opacity
- audio_gain
- transition_in
- transition_out

其他 Track：

- video
- source_audio
- BGM
- voiceover
- subtitle
- overlay

## 10.3 EDL 最重要的原则

**EDL 必须能够在完全没有 LLM 的情况下被 Renderer 执行。**

即：

```text
EDL
 ↓
Renderer
 ↓
Video
```

这条链必须 deterministic。

Renderer 不允许问：

> “AI，你觉得这里应该剪哪一段？”

如果还需要 AI 决策，

说明它仍然处于 EditPlan / Resolve 阶段。

---

# 11. ReviewReport

## 11.1 定义

ReviewReport 是：

> 对某个确定对象 revision 的质量评估。

它不直接修改原对象。

## 11.2 Review 分三层

### Candidate Review

发生在 Shot Resolver 选镜头时。

检查：

- 是否符合 ShotRequirement
- 人物是否正确
- 是否重复
- 清晰度
- 时长
- 动作完整性
- 连续性

### EDL Review

检查：

- timeline overlap
- 时间越界
- 素材重复
- 时长偏差
- 节奏
- BeatMap alignment
- narration coverage
- subtitle timing
- source policy violation

### Render Review

检查最终视频：

- 黑帧
- 音画不同步
- 音量
- 字幕越界
- encoding
- resolution
- 人脸裁切
- transition artifact
- 内容一致性

## 11.3 ReviewReport 内容

- review_id
- stage
- target_ref
- checks
- metrics
- findings
- severity
- passed
- suggested_actions

ReviewReport **只能提出修改建议**。

如果用户或系统接受修改：

> 创建新的 EditPlan / EDL revision。

而不是 ReviewReport 自己偷偷修改 Timeline。

---

# 12. 九对象依赖拓扑

```text
Brief
  │
  ▼
ScriptPlan
  │
  ▼
ShootingPlan
  │
  │        Captured / Imported / Remote
  │                    │
  │                    ▼
  │                  Asset
  │                    │
  │                    ▼
  │                   Shot
  │                    │
  └──────────────┐     │
                 ▼     ▼
               EditPlan ◀──── BeatMap
                  │              ▲
                  │              │
                  │         Audio Asset
                  ▼
                 EDL
                  │
                  ▼
                Render
                  │
                  ▼
             ReviewReport
```

注意：

**Shot 不从 ShootingPlan 派生。**

Shot 是对真实 Asset 的解析结果。

真正负责把：

`ShotRequirement`

和

`Shot`

连接起来的是：

**EditPlan / Shot Resolver。**

这是一个非常重要的解耦点。

---

# 13. 修改传播规则

## Brief 改变

可能使以下全部 stale：

ScriptPlan  
ShootingPlan  
EditPlan  
EDL

但不会使现有 Asset / Shot 消失。

---

## ScriptPlan 改变

可能使：

ShootingPlan  
EditPlan  
EDL

失效。

---

## ShootingPlan 改变

不会改变已经拍摄的 Asset。

但可能让部分素材重新变成：

> 缺失 / 多余 / 不匹配。

---

## 新增 Asset

不会反向改变 ScriptPlan。

只更新：

Asset Catalog / Shot Index

并允许 EditPlan 重新 Resolve。

---

## Shot Understanding 升级

通常不改变 Shot identity。

但可能影响：

candidate ranking  
EditPlan resolution  
EDL review

---

## BeatMap 改变

可能影响：

EditPlan  
EDL

但不会影响 Asset / Shot / Script。

---

## EditPlan 改变

只要求：

重新 Resolve / 生成 EDL。

---

## EDL 改变

只需要：

重新 Render + Review。

不应该重新生成 Script。

---

# 14. 强制架构不变量

v0.1 正式冻结以下规则：

### I. Agent 输出不能成为隐式机器协议

禁止：

> `[shot: 01:23 to 01:27]`

这种自然语言文本作为系统核心接口。

Agent 输出必须进入 typed schema。

---

### II. Domain 不直接传文件路径作为身份

领域对象引用：

`asset_id`

不是：

`C:\Users\...\video.mp4`

文件路径属于 Storage Adapter。

---

### III. Renderer 无创作权

Renderer：

**只执行 EDL。**

---

### IV. BeatMap 无剪辑权

BeatMap：

**只描述音乐。**

---

### V. Shot 无叙事权

Shot：

**只描述素材。**

---

### VI. ScriptPlan 不绑定具体素材

它描述故事。

---

### VII. ShootingPlan 不绑定最终镜头

它描述应该拍什么。

---

### VIII. EditPlan 不拥有精确 source timestamp

它描述导演决策。

---

### IX. EDL 不拥有创作推理

它只描述执行决定。

---

### X. Review 不直接修改历史结果

任何修改产生新 revision。

---

# 15. 模块边界 v0.1

未来仓库建议围绕领域而非上游项目组织：

```text
domain/
├─ brief/
├─ script/
├─ shooting/
├─ asset/
├─ shot/
├─ beatmap/
├─ edit/
├─ edl/
└─ review/

application/
├─ workflows/
├─ services/
├─ resolvers/
└─ pipeline/

providers/
├─ llm/
├─ material/
├─ music/
├─ vision/
└─ speech/

media/
├─ ingest/
├─ shot_detection/
├─ analysis/
└─ indexing/

render/
├─ renderer/
├─ ffmpeg/
└─ moviepy/

storage/
├─ project/
├─ asset/
├─ index/
└─ artifact/

adapters/
├─ cli/
├─ api/
├─ desktop/
└─ mcp/
```

### 核心原则

**Agent 不属于 domain。**

MCP 不属于 domain。

FFmpeg 不属于 domain。

Pexels 不属于 domain。

---

# 16. 继承 / 重写 / 舍弃工程地图

## FireRed-OpenStoryline

### 继承

- Node Registry 思想
- NodeMeta / dependency graph 思想
- Pipeline 节点化
- Artifact 思想
- TransNetV2 Shot Detection
- FFmpeg 媒体处理经验
- BGM 推荐思路
- Render 经验
- Agent / MCP 适配思想

### 重写

- BaseNode
- Script 领域模型
- Understand Clips
- Group Clips
- Search Media
- Select BGM 与音乐分析的耦合
- Timeline Planner
- Timeline 数据模型
- Session / Artifact ownership

### 舍弃

- `Footage → Script` 作为默认主流程
- Dict 作为核心长期协议
- Domain 与 MCP 文件传输耦合
- Pexels 写死在核心节点
- Beat = Cut 的简化逻辑
- Timeline Planner 直接充当最终剪辑大脑

---

# 17. MoneyPrinterTurbo

## 继承

- Pexels 接入经验
- Pixabay 接入经验
- Coverr 接入经验
- API Key rotation
- TLS / secret protection
- material cache
- same-query concurrency control
- source provenance
- creator/source page
- 下载失败降级
- FFmpeg codec fallback
- script-order-aware material retrieval 思想

## 重写

统一变成：

`MaterialProvider`

接口体系。

原来的：

`video_terms`

升级为：

`ShotRequirement.search_queries`

以及 EditPlan 的素材查询需求。

---

## 舍弃

- 大型 `task.py` 做中心编排
- `if source == pexels/pixabay/...` 无限扩张
- random material concat
- “搜索一些素材然后凑够旁白时长”的产品逻辑

公网素材未来只能是：

> **满足 ShotRequirement 的一个候选来源。**

---

# 18. CutClaw

CutClaw 正式定义为：

**Engineering Reference Only**

不成为代码依赖。

## 继承的是思想

### 分层理解

Raw Video  
→ Shot  
→ Scene  
→ Semantic Summary

### Plan / Resolve 分离

Screenwriter  
→ shot_plan

Editor  
→ shot_point

映射为我们的：

EditPlan  
→ Shot Resolver  
→ EDL

### Constrained Agent Search

Agent 只能在素材数据库和受限邻域内探索。

### Reviewer Loop

Proposal  
→ Validation  
→ Correction  
→ Commit

---

## 重写

以上所有思想全部基于我们的：

Asset  
Shot  
EditPlan  
EDL  
ReviewReport

重新实现。

---

## 舍弃

- CutClaw 代码直接依赖
- global config.py
- 文件夹作为状态机
- JSON 文件作为模块间总线
- natural-language tool protocol
- regex 解析 shot timestamp
- local_run.py 巨型 pipeline
- Agent 直接拥有文件系统结构知识

---

# 19. BeatSync Engine 的位置

BeatSync Engine 暂不进入代码继承范围。

它承担：

**BeatMap 算法参考。**

我们关注的是：

- beat
- downbeat
- onset
- phrase
- energy
- section
- drop
- build-up
- musical structure

这些音乐分析思想。

最终实现必须服务于我们自己的 `BeatMap Contract`。

---

# 20. v0.1 最核心的三条链

## 创作链

**Brief → ScriptPlan → ShootingPlan**

回答：

> 想做什么 → 怎么讲 → 应该拍什么

---

## 素材链

**Asset → Shot → Understanding / Index**

回答：

> 我实际上拥有什么素材

---

## 剪辑链

**EditPlan → Shot Resolver → EDL → Render → ReviewReport**

回答：

> 应该怎么剪 → 最终剪哪一段 → 执行 → 检查

这三条链在架构上必须彼此独立，但通过明确 ID 引用发生关系。

---

# Architecture Contract v0.1 Final Principle

系统的核心价值不是：

> AI 帮我调用 FFmpeg。

而是建立一套从：

**创作意图**

到：

**拍摄需求**

到：

**真实素材理解**

到：

**导演决策**

再到：

**确定性剪辑执行**

的结构化中间表示。

因此真正需要长期保护的不是某段模型 Prompt，也不是某个开源项目的代码。

而是：

**Brief → ScriptPlan → ShootingPlan → Asset / Shot → BeatMap → EditPlan → EDL → ReviewReport**

这一套领域拓扑。