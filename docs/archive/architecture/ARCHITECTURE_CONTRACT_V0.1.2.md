# Architecture Contract v0.1.2
## Module Ownership & Interface Matrix

**状态：Pre-Repository Baseline**  
**上游契约：**
- Architecture Contract v0.1 — Domain Model
- Architecture Contract v0.1.1 — Object Relations & Schema Matrix

**目标：**

冻结以下问题：

1. 每一种核心领域对象由谁创建；
2. 谁可以产生新 revision；
3. 谁只能读取；
4. 模块之间通过什么接口协作；
5. Agent、Provider、Storage、Renderer 各自能做什么；
6. 哪些依赖方向被禁止；
7. FireRed / MoneyPrinterTurbo / CutClaw / BeatSync Engine 的思想分别落在哪个模块；
8. 明确第一版仓库应该包含什么、不应该包含什么。

---

# 0. 最重要原则：Ownership ≠ Storage

一个模块“拥有”某对象，含义是：

> **它拥有该对象语义上的创建权和 revision 决策权。**

不是：

> 文件存在它的目录里。

例如：

`EDLBuilder`

拥有 EDL 的生成权。

但真正把 EDL 写进 SQLite / JSON / Object Store 的是：

`EDLRepository`

Storage 只有保存权，没有创作权。

同理：

`UnderstandingService`

可以产生 Shot Analysis，

但不能修改 Shot 的：

`source_start / source_end`

因为 Shot boundary 不归它所有。

---

# 1. 顶层模块划分

v0.1.2 冻结六大层：

```text
┌────────────────────────────┐
│          Adapters          │
│ UI / CLI / API / MCP       │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│        Application         │
│ Workflow / Use Cases       │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│           Domain           │
│ Entities / Contracts       │
└────────────────────────────┘

Application 同时通过 Ports 调用：

┌────────────────────────────┐
│        Capabilities        │
│ Planning / Media / Music   │
│ Editing / Review / Render  │
└────────────────────────────┘
              │
              ▼
┌────────────────────────────┐
│       Infrastructure       │
│ Storage / FFmpeg / Models  │
│ Pexels / APIs / Index      │
└────────────────────────────┘
```

---

# 2. Domain 层职责

`domain/`

只定义：

- 核心对象
- Value Objects
- Enum
- ID / Revision Ref
- Invariants
- Schema
- Deterministic validation

Domain **不负责执行工作流**。

Domain 不允许知道：

- OpenAI
- Gemini
- Claude
- Pexels
- FFmpeg
- MoviePy
- MCP
- HTTP
- SQLite
- 文件夹位置

## 强规则

```text
domain/
    MUST NOT import
application/
providers/
render/
storage/
adapters/
```

Domain 是整个系统最稳定的层。

---

# 3. Application 层职责

`application/`

负责：

> **什么时候调用谁。**

主要包含：

- Use Cases
- Workflow Engine
- Pipeline orchestration
- Transaction boundary
- stale propagation
- retry policy
- artifact association
- capability interfaces / ports

例如：

```text
CreateScriptPlan
PrepareShootingPlan
IngestFootage
AnalyzeFootage
PrepareEditPlan
ResolveEditPlan
BuildEDL
RenderProject
ReviewProject
```

## Application 不拥有创作算法

例如：

Application 可以调用：

`Director.plan()`

但不能自己偷偷写一套：

“如果是 Hook 就随机挑最短镜头”

的逻辑。

那属于 Editing Capability。

---

# 4. Pipeline Engine 的权限

FireRed 的节点化思想会进入这里。

Pipeline Engine：

### 可以

- 判断节点依赖
- 调用 capability
- 保存 Artifact
- 管理 execution status
- retry
- cancellation
- stale propagation
- 日志
- metrics

### 不可以

- 写 Script 文案
- 选择 Shot
- 分析音乐
- 修改 EDL
- 搜索 Pexels
- 决定转场
- 自己理解视频

因此：

> **Pipeline Engine 是交通警察，不是导演。**

---

# 5. 核心对象 Ownership Matrix

| 对象 | Authoritative Owner | 可读模块 | 禁止修改者 |
|---|---|---|---|
| Brief | BriefService | 全部下游 | Agent / Renderer / Provider |
| ScriptPlan | ScriptPlanner | ShootingPlanner / Director / Review | Resolver / Renderer |
| ShootingPlan | ShootingPlanner | Coverage / Director / Resolver | ShotDetector / Renderer |
| Asset | AssetIngestService | Media / Editing / Render | Provider / Agent |
| Shot Boundary | ShotDetector + ShotCatalog | Understanding / Resolver / Review | Understanding / Director |
| Shot Analysis | UnderstandingService | Resolver / Director / Review | ShotDetector |
| BeatMap | BeatAnalysisService | Director / Timeline / Review | Renderer / Resolver |
| EditPlan | Director | Resolver / EDLBuilder / Review | Resolver / Renderer |
| ResolutionDecision | ShotResolver | EDLBuilder / Review | Director / Renderer |
| EDL | EDLBuilder | Renderer / Review | Renderer / Provider |
| ReviewReport | ReviewService | Application / User | Renderer |
| AssetCatalogSnapshot | AssetCatalogService | Director / Resolver | Agent |
| RenderArtifact | Renderer | Review / Application | Director |

---

# 6. BriefService

## Ownership

负责：

`Brief`

## Interface

```text
create_brief(input)
    → Brief

revise_brief(brief_ref, patch)
    → Brief@next_revision
```

## 允许

- 用户输入规范化
- 平台约束规范化
- Duration / aspect ratio validation

## 禁止

BriefService 不生成：

- Script
- ShotRequirement
- Shot
- EDL

---

# 7. ScriptPlanner

## Ownership

负责：

`ScriptPlan`

## Input

```text
BriefRef
optional ReferenceMaterials
optional UserInstruction
```

## Output

```text
ScriptPlan
```

## Interface

```text
plan_script(context)
    → ScriptPlanProposal

commit_script_plan(proposal)
    → ScriptPlan
```

这里刻意分：

**Proposal**

和：

**Committed Domain Object**

因为 AI 输出不能直接成为领域事实。

---

# 8. Agent Proposal Pattern

v0.1.2 正式冻结：

所有 LLM/Agent 生成型模块采用：

```text
Agent
  ↓
Proposal DTO
  ↓
Schema Validation
  ↓
Deterministic Validation
  ↓
Domain Commit
```

禁止：

```text
Agent
  ↓
直接写数据库
```

例如：

```text
LLM
 ↓
ScriptPlanProposal
 ↓
ScriptPlanValidator
 ↓
ScriptPlanner.commit()
 ↓
ScriptPlan
```

---

# 9. ShootingPlanner

## Ownership

负责：

`ShootingPlan`

和其中的：

`ShotRequirement`

## Input

```text
ScriptPlanRef
BriefRef
optional ProductionConstraints
```

## Output

```text
ShootingPlan
```

## Interface

```text
plan_shooting(context)
    → ShootingPlanProposal

validate_shooting_plan(proposal)
    → ValidationResult

commit_shooting_plan(proposal)
    → ShootingPlan
```

## 禁止

ShootingPlanner 不允许：

- 查询最终 Shot
- 写 EDL
- 决定 timeline position

因为：

> 拍摄阶段不能提前拥有剪辑执行权。

---

# 10. AssetIngestService

## Ownership

负责创建：

`Asset`

## Input

统一采用：

```text
MediaSource
```

MediaSource 可以来自：

- local file
- captured file
- remote download
- generated media

## Interface

```text
ingest(source, provenance)
    → Asset
```

## AssetIngest 必须完成

- content hash
- media probing
- canonical identity
- technical metadata
- provenance
- storage registration

## 关键规则

Provider 不能直接创建 Asset。

正确路径：

```text
PexelsProvider
     ↓
RemoteMaterialCandidate
     ↓
download
     ↓
MediaSource
     ↓
AssetIngestService
     ↓
Asset
```

---

# 11. MaterialProvider Ownership

MaterialProvider **不拥有任何 Domain Entity**。

它只拥有：

> 对外部素材服务的访问能力。

## Interface

```text
search(MaterialQuery)
    → RemoteMaterialCandidate[]

fetch(RemoteMaterialCandidate)
    → MediaSource
```

## MaterialQuery

来源于：

- ShotRequirement
- EditSlot
- Resolver fallback

而不是：

> “帮整个视频随机找点素材。”

---

# 12. MaterialProvider v0.1 目标实现

```text
MaterialProvider

├─ PexelsProvider
├─ PixabayProvider
├─ CoverrProvider
└─ LocalProvider
```

未来：

```text
WikimediaProvider
ArchiveOrgProvider
...
```

不改变领域层。

---

# 13. ShotDetector

## Ownership

负责：

> Shot boundary proposal

但最终 Shot Identity 由：

`ShotCatalog`

登记。

## Interface

```text
detect(asset_ref)
    → ShotBoundaryProposal[]
```

其中：

```text
ShotBoundaryProposal
├─ asset_ref
├─ source_start
├─ source_end
├─ detection_method
└─ confidence
```

然后：

```text
ShotCatalog.commit_boundaries(...)
    → Shot[]
```

---

# 14. 为什么 ShotDetector 不直接写 Shot Analysis

因为：

边界检测回答：

> 镜头在哪里分开？

素材理解回答：

> 镜头里是什么？

这两个问题必须独立。

这样未来可以：

TransNetV2 → 新模型

而不重做所有视觉理解架构。

也可以：

视觉模型升级

而不改变 Shot identity。

---

# 15. UnderstandingService

## Ownership

负责：

> Shot Analysis Revision

不拥有 Shot identity。

## Interface

```text
analyze(shot_ref, AnalysisProfile)
    → ShotAnalysis

reanalyze(shot_ref, AnalysisProfile)
    → ShotAnalysis@new_revision
```

## AnalysisProfile

用于控制成本。

例如：

```text
basic
semantic
speech
deep_visual
editorial
```

避免所有 Shot 永远进行最高成本 VLM 分析。

---

# 16. UnderstandingService 可以写

- caption
- people
- objects
- action
- emotion
- environment
- framing
- motion
- aesthetic score
- transcript
- embedding

## UnderstandingService 禁止写

- asset_ref
- source_start
- source_end
- timeline_in
- selected_by_editor

它只描述事实。

---

# 17. ShotIndex

ShotIndex 属于：

**Retrieval Infrastructure**

它不是 Domain authority。

## Input

```text
Shot
ShotAnalysis
```

## Output

```text
ShotCandidate[]
```

## Interface

```text
search(query, constraints)
    → ShotCandidate[]
```

ShotIndex 可以使用：

- vector search
- keyword search
- metadata filter
- SQL
- local embeddings
- hybrid retrieval

但：

> 索引里的结果不是领域事实。

Resolver 必须重新验证候选资格。

---

# 18. AssetCatalogService

## Ownership

负责：

`AssetCatalogSnapshot`

## Interface

```text
snapshot(project_ref)
    → AssetCatalogSnapshot
```

Snapshot 固定：

- Assets
- Shots
- Shot Analysis revisions

Director / Resolver 不允许面对：

> “某目录目前有什么文件”

这种不稳定状态。

---

# 19. BeatAnalysisService

## Ownership

负责：

`BeatMap`

## Input

必须是：

```text
AssetRef(kind=audio)
```

## Output

```text
BeatMap
```

## Interface

```text
analyze(audio_asset_ref)
    → BeatMap
```

## 可以使用

- librosa
- madmom
- BeatSync Engine 思想
- VLM/audio model
- DSP
- ML

这些全部是 implementation detail。

---

# 20. BeatAnalysisService 禁止

禁止输出：

```text
cut_at = 12.3s
```

正确输出是：

```text
downbeat = 12.28s
accent_strength = ...
energy = ...
section = chorus
```

至于要不要切：

归 Director / Timeline Allocation。

---

# 21. Director

这是 Auto Edit 的最高层编辑决策模块。

## Ownership

负责：

`EditPlan`

及其中：

`EditSlot`

## Input

```text
BriefRef
ScriptPlanRef
ShootingPlanRef
AssetCatalogSnapshotRef
optional BeatMapRef
optional UserEditInstruction
```

## Output

```text
EditPlan
```

---

# 22. Director 可以做什么

Director 可以决定：

- 哪些 Script Section 最终保留
- 每个阶段需要几个 EditSlot
- Slot 时长预算
- 视觉意图
- pacing
- source policy
- music alignment policy
- continuity intent
- transition intent
- ShotRequirement coverage allocation

Director 可以说：

> 这里需要一个快速的木工动作特写。

## Director 不可以说

> 用 asset_17，从 13.2 秒剪到 14.1 秒。

那已经越权进入 Resolver / EDL。

---

# 23. ShotResolver

## Ownership

负责：

`ResolutionDecision`

## Input

```text
EditSlot
AssetCatalogSnapshot
ShotIndex
ShotAnalysis
already_used_context
continuity_context
```

## Output

```text
ResolutionDecision
```

---

# 24. ShotResolver Interface

```text
resolve(slot_ref, context)
    → ResolutionDecision
```

可内部使用：

```text
retrieve_candidates()
check_eligibility()
rank_candidates()
inspect_candidate()
expand_neighbors()
select_source_window()
validate_selection()
```

这是我们吸收 CutClaw：

**semantic retrieval → fine trimming → review → commit**

思想的位置。

但重新实现。

---

# 25. Resolver 权限边界

Resolver 可以决定：

- Shot
- source window
- alternatives
- ranking
- fallback
- unresolved

Resolver **不能修改**：

- EditSlot purpose
- EditPlan pacing
- Script
- ShootingPlan
- BeatMap

如果 Resolver 发现：

> 这个 Slot 根本无法满足

应该返回：

```text
decision_type = unresolved
```

而不是自己把 Slot 改掉。

上层 Application 决定是否：

- remote fallback
- request reshoot
- ask Director replan
- manual intervention

---

# 26. Resolver 与公网素材

正确关系：

```text
Resolver
   ↓
发现 local insufficient
   ↓
检查 source_policy
   ↓
MaterialSearchUseCase
   ↓
MaterialProvider
   ↓
MediaSource
   ↓
AssetIngest
   ↓
ShotDetector
   ↓
Understanding
   ↓
AssetCatalog 更新
   ↓
Resolver retry
```

禁止：

```text
Resolver
 ↓
Pexels URL
 ↓
EDL
```

---

# 27. EDLBuilder

## Ownership

**唯一拥有 EDL 创建权。**

## Input

```text
EditPlanRef
ResolutionDecision[]
BeatMapRef?
Voiceover / Subtitle Artifacts
OutputSpec
```

## Output

```text
EDL
```

---

# 28. EDLBuilder 负责

- timeline allocation
- timeline_in / timeline_out
- source mapping
- track construction
- source audio
- BGM placement
- voiceover
- subtitle track
- transitions
- playback rate
- crop/transform instruction
- deterministic timeline validation

---

# 29. EDLBuilder 不负责

EDLBuilder 不重新：

- 写 Script
- 搜索 Shot
- 调 Pexels
- 判断画面“好不好看”
- 选择故事结构

如果 ResolutionDecision 不够：

返回 build failure。

不能自己去寻找素材。

---

# 30. TimelineAllocator

属于：

`editing/edl`

内部策略模块。

可以负责：

```text
EditSlot target duration
+
BeatMap anchors
+
Narration duration
+
ResolutionDecision source window
↓
timeline positions
```

这是 FireRed `PlanTimeline` 被重写后真正应该落的位置。

FireRed 的 Timeline 逻辑不作为领域契约直接继承。

---

# 31. EDLValidator

属于：

`editing/edl`

负责 deterministic constraints：

- source range valid
- timeline overlap
- missing assets
- negative duration
- unsupported transform
- track validity
- duration constraint

它可以返回：

```text
ValidationResult
```

但：

**ReviewReport 的领域对象仍由 ReviewService 创建。**

---

# 32. Renderer

## Ownership

负责：

`RenderArtifact`

不拥有 EDL。

## Interface

```text
render(edl_ref, output_spec)
    → RenderArtifact
```

## Renderer 可以

- FFmpeg
- MoviePy
- hardware codec
- proxy
- cache
- encode fallback

## Renderer 禁止

- 改 source_in/out
- 替换 Shot
- 调整 narrative timing
- 删除 Segment
- 自动选择 BGM
- 改写字幕内容

如果 EDL 不可执行：

**fail loudly**

而不是偷偷“修好”。

---

# 33. Renderer Backend Contract

未来：

```text
Renderer
   │
   ├─ FFmpegRenderer
   └─ MoviePyRenderer
```

系统核心依赖：

```text
Renderer Interface
```

不依赖 MoviePy。

v0.1 推荐：

> **FFmpeg 为长期主 Backend。**

MoviePy 可以保留作为部分高层效果实现或兼容能力。

---

# 34. ReviewService

## Ownership

唯一负责：

`ReviewReport`

## Interface

```text
review_candidate(...)
    → ReviewReport

review_edl(edl_ref)
    → ReviewReport

review_render(render_artifact_ref)
    → ReviewReport
```

---

# 35. Review 模块内部可以包含

```text
DeterministicChecks
VisionReviewer
AudioReviewer
NarrativeReviewer
PolicyReviewer
```

不同 Reviewer 的结果最终聚合为：

`ReviewReport`

---

# 36. Review 权限边界

ReviewService：

**只能评价。**

不能直接：

```text
EDL.segment[5].source_out = ...
```

正确流程：

```text
ReviewReport
   ↓
suggested_action
   ↓
Application
   ↓
Director / Resolver / EDLBuilder
   ↓
new revision
```

---

# 37. Storage Ownership

Storage 模块包含：

```text
ProjectRepository
BriefRepository
ScriptPlanRepository
ShootingPlanRepository
AssetRepository
ShotRepository
BeatMapRepository
EditPlanRepository
EDLRepository
ReviewRepository
ArtifactStore
```

## Repository 的职责

- save
- load
- revision lookup
- list
- snapshot
- transaction
- integrity

## Repository 禁止

- 自动修改对象语义
- 生成脚本
- 排 Shot
- 分析音乐
- 重排 EDL

Storage 不是业务层。

---

# 38. ArtifactStore

Artifact 是：

运行过程中产生的可追溯文件。

例如：

- VLM raw output
- thumbnails
- proxy video
- waveform
- subtitle
- frame samples
- render output
- debug report

Artifact：

**不是 Domain Entity。**

不要把二者混为一谈。

---

# 39. Adapter Layer

包括：

```text
CLI
API
Desktop UI
MCP
Agent Skills
```

它们都只能调用：

**Application Use Cases**

禁止：

```text
MCP
 ↓
直接 EDLRepository.save()
```

必须：

```text
MCP
 ↓
Application
 ↓
EDLBuilder
 ↓
Repository
```

---

# 40. Agent Ownership

v0.1.2 特别冻结：

# **Agent 不拥有任何 Domain Entity。**

Agent 是：

> reasoning implementation.

不是：

> domain owner.

Agent 可以生成：

```text
ScriptPlanProposal
ShootingPlanProposal
EditPlanProposal
CandidatePreference
ReviewProposal
```

但所有 Proposal 都要：

```text
Schema
→ Validator
→ Domain Owner
→ Commit
```

---

# 41. Provider Layer

Provider 统一遵循：

> Capability Port → Provider Adapter

例如：

```text
LLMPort
├─ OpenAIAdapter
├─ GeminiAdapter
├─ DeepSeekAdapter
└─ LocalModelAdapter
```

```text
MaterialProvider
├─ Pexels
├─ Pixabay
└─ Coverr
```

```text
SpeechProvider
├─ Whisper
├─ Cloud ASR
└─ ...
```

以后换模型：

Domain 不变。

Application 理论上也不变。

---

# 42. Interface Matrix

| 模块 | 输入 | 输出 | Domain Write |
|---|---|---|---|
| BriefService | User Input | Brief | Brief |
| ScriptPlanner | Brief | ScriptPlanProposal | ScriptPlan |
| ShootingPlanner | ScriptPlan | ShootingPlanProposal | ShootingPlan |
| MaterialProvider | Query | RemoteCandidate | 无 |
| AssetIngest | MediaSource | Asset | Asset |
| ShotDetector | Asset | BoundaryProposal | 无 |
| ShotCatalog | BoundaryProposal | Shot | Shot |
| Understanding | Shot | ShotAnalysis | Analysis revision |
| ShotIndex | Shot+Analysis | Candidates | 无 |
| BeatAnalysis | Audio Asset | BeatMap | BeatMap |
| Director | Creative Context | EditPlanProposal | EditPlan |
| ShotResolver | EditSlot+Catalog | ResolutionDecision | Decision Artifact |
| EDLBuilder | Plan+Decisions | EDL | EDL |
| Renderer | EDL | RenderArtifact | 无核心 Domain |
| ReviewService | Target | ReviewReport | ReviewReport |
| Storage | Domain Object | Persisted Object | 无语义写权 |
| Pipeline | Workflow | Execution State | 无内容写权 |

---

# 43. Allowed Dependency Matrix

## Domain

允许：

```text
stdlib
shared/domain types
```

禁止全部外部业务层。

---

## Application

允许：

```text
Domain
Ports
```

禁止直接：

```text
requests
Pexels SDK
ffmpeg subprocess
OpenAI SDK
```

---

## Capabilities

允许：

```text
Domain
Application Ports
internal algorithms
```

---

## Infrastructure

允许：

```text
Ports
external libraries
OS / FS / network
```

---

## Adapters

允许：

```text
Application Use Cases
```

不直接访问内部实现。

---

# 44. Dependency Direction

正式冻结：

```text
Adapters
    ↓
Application
    ↓
Domain

Infrastructure
    ↑
Ports
    ↑
Application
```

即 Dependency Inversion。

领域层永远处于中心。

---

# 45. 禁止依赖

### Domain → LLM

禁止。

### Domain → FFmpeg

禁止。

### Director → Pexels

禁止。

### Renderer → ShotResolver

禁止。

### ShotDetector → ScriptPlan

原则上禁止。

镜头边界是素材事实，

不应该因为脚本不同就变。

### BeatAnalysis → EditPlan

禁止。

音乐分析不知道导演策略。

### Provider → EDL

禁止。

### UI → Database

禁止。

---

# 46. Workflow Use Cases

第一版 Application 建议只暴露这些核心 Use Case：

```text
CreateProject
CreateBrief
GenerateScriptPlan
GenerateShootingPlan

IngestAssets
AnalyzeAssets
CheckCoverage

SelectMusic
AnalyzeMusic

GenerateEditPlan
ResolveEditPlan
BuildEDL

RenderEDL
ReviewEDL
ReviewRender

ApplyUserRevision
```

不构建万能：

```text
do_everything()
```

---

# 47. 默认 Workflow

```text
Create Brief
     ↓
Generate ScriptPlan
     ↓
Generate ShootingPlan
     ↓
[USER SHOOTS]
     ↓
Ingest Assets
     ↓
Detect Shots
     ↓
Understand Assets
     ↓
Coverage Check
     ↓
Select / Import Music
     ↓
Build BeatMap
     ↓
Director → EditPlan
     ↓
Resolver
     ↓
EDLBuilder
     ↓
EDL Review
     ↓
Renderer
     ↓
Render Review
```

---

# 48. Workflow 可以暂停

系统必须允许在任何正式 Artifact 后暂停：

```text
Brief ✓
ScriptPlan ✓
ShootingPlan ✓
Asset Analysis ✓
EditPlan ✓
EDL ✓
Render ✓
```

因为这是个人创作工具，

不是必须：

> 按一次按钮然后等待最终 MP4。

用户可以在任何层级进入修改。

---

# 49. Natural Language Re-edit Contract

例如用户说：

> 前三秒再狠一点。

正确流程：

```text
Natural Language
      ↓
Revision Interpreter
      ↓
EditPlan patch proposal
      ↓
Director validation
      ↓
EditPlan@2
      ↓
Resolve affected slots
      ↓
EDL@2
      ↓
Render
```

而不是：

```text
Prompt
 ↓
FFmpeg 随便重新剪
```

---

# 50. Incremental Recompute Contract

这是未来性能的核心。

如果用户只修改：

### Subtitle wording

不应该重新：

- Detect Shots
- Understand footage
- Analyze BeatMap
- Resolve unrelated clips

---

如果更换 BGM：

应该重新：

- BeatMap
- Beat-sensitive EditPlan部分
- timeline allocation
- EDL
- Render

但：

Asset Understanding 不变。

---

如果增加新素材：

应该：

- ingest new Asset
- detect its Shots
- understand new Shots
- update Catalog
- optionally rerun unresolved / weak Slots

而不是重新分析所有老素材。

---

# 51. Module-Level Staleness Ownership

谁负责宣布 stale：

| 变化 | Stale Manager |
|---|---|
| Brief revision | Application Dependency Graph |
| ScriptPlan revision | Application |
| Asset deletion | AssetCatalogService |
| Shot boundary revision | ShotCatalog |
| Analysis revision | UnderstandingService 发 change signal |
| BeatMap revision | BeatAnalysisService |
| EditPlan revision | Director |
| EDL revision | EDLBuilder |
| Render replacement | Renderer |

真正传播 stale 状态：

> Application 层统一负责。

模块只报告“我变了”。

---

# 52. Open-source Engineering Map v0.1.2

## FireRed-OpenStoryline

### 落入 Application / Pipeline

借鉴：

- Node Registry
- NodeMeta
- dependency graph
- Artifact
- MCP orchestration

### 判断

**思想继承，实现重构。**

不直接让原 BaseNode 成为核心。

---

## FireRed SplitShots

### 落入

```text
media/shot_detection
```

### 判断

**高价值可复用候选。**

可基于 Apache-2.0 代码适配。

但输入输出必须转换成我们的：

```text
AssetRef
→ ShotBoundaryProposal[]
```

---

## FireRed UnderstandClips

### 落入

```text
media/understanding
```

### 判断

**重写。**

保留 VLM 分析经验，

不继承逐 Clip 即时调用作为最终架构。

---

## FireRed SelectBGM

### 拆成

```text
music/selection
music/beat_analysis
```

### 判断

BGM 推荐：

**部分继承。**

Beat analysis：

**吸收后重写为 BeatMap。**

---

## FireRed PlanTimeline

### 落入

```text
editing/edl/timeline_allocator
```

### 判断

**重写。**

不继承其现有 Timeline Contract。

---

## FireRed RenderVideo

### 落入

```text
render/backends/
```

### 判断

**选择性复用。**

---

# 53. MoneyPrinterTurbo

## Material Service

### 落入

```text
providers/material/
```

吸收：

- Pexels
- Pixabay
- Coverr
- API key rotation
- cache
- TLS
- secret redaction
- provenance
- retry
- concurrency control

### 判断

**工程经验重点继承，接口重构。**

---

## task.py

### 判断

**舍弃架构。**

不进入核心设计。

其中可吸收：

- stage failure
- resumability
- progress

进入：

```text
application/workflow/
```

---

# 54. CutClaw

不落入依赖树。

它的思想映射为：

```text
Screenwriter
    ↓
Director

shot_plan
    ↓
EditPlan

EditorCore
    ↓
ShotResolver

shot_point
    ↓
ResolutionDecision

Reviewer
    ↓
ReviewService
```

### 判断

**100% 独立重实现。**

---

# 55. BeatSync Engine

落入思想参考：

```text
music/beat_analysis
```

用于帮助实现：

`BeatMap`

不直接进入：

EDL / Timeline ownership。

---

# 56. 第一版仓库模块边界

建仓时建议采用：

```text
src/
│
├─ domain/
│  ├─ common/
│  ├─ brief/
│  ├─ script/
│  ├─ shooting/
│  ├─ asset/
│  ├─ shot/
│  ├─ music/
│  ├─ edit/
│  ├─ edl/
│  └─ review/
│
├─ application/
│  ├─ use_cases/
│  ├─ workflow/
│  ├─ ports/
│  └─ revision/
│
├─ planning/
│  ├─ script/
│  └─ shooting/
│
├─ media/
│  ├─ ingest/
│  ├─ shot_detection/
│  ├─ understanding/
│  └─ indexing/
│
├─ music/
│  ├─ selection/
│  └─ beat_analysis/
│
├─ editing/
│  ├─ director/
│  ├─ resolver/
│  ├─ edl/
│  └─ review/
│
├─ providers/
│  ├─ llm/
│  ├─ material/
│  ├─ speech/
│  └─ vision/
│
├─ render/
│  ├─ renderer/
│  └─ backends/
│
├─ storage/
│  ├─ repositories/
│  ├─ project/
│  ├─ asset/
│  └─ artifact/
│
└─ adapters/
   ├─ cli/
   ├─ api/
   ├─ desktop/
   └─ mcp/
```

---

# 57. 第一版仓库明确“不建立”的东西

为了避免过度设计，v0.1 初始仓库暂不建立：

- 微服务
- 消息队列
- Kubernetes
- 多租户
- 用户账户系统
- 云端协作
- 多人实时编辑
- 分布式 Asset Store
- Plugin Marketplace
- 自定义 DSL
- 自研数据库
- 自研视频 codec
- 自研 Timeline UI Engine

它首先是：

> **Single-user local-first editing system.**

未来真的需要时再扩展。

---

# 58. 第一版也不需要九个独立服务进程

这里的：

`ScriptPlanner`

`Director`

`Resolver`

等是：

**模块职责**

不是：

九个 Docker Container。

第一版完全可以是：

```text
one Python application
+
clear internal module boundaries
```

甚至应优先这样做。

架构清晰 ≠ 部署复杂。

---

# 59. Testing Ownership Matrix

每个模块必须拥有自己的 contract test。

## Domain

测试：

- schema
- invariants
- revision refs

---

## ShotDetector

测试：

```text
Asset
→ boundaries
```

不测试 LLM。

---

## Understanding

测试：

```text
Shot
→ ShotAnalysis
```

---

## Director

测试：

```text
Creative Context
→ valid EditPlan
```

---

## Resolver

重点测试：

- hard constraint
- eligibility
- ranking
- no eligible candidate
- remote fallback
- reused Shot constraint
- source window validity

---

## EDLBuilder

重点测试：

- deterministic output
- timeline overlap
- range correctness
- beat tolerance
- narration timing

---

## Renderer

测试：

```text
known EDL
→ expected media artifact
```

Renderer 测试不允许重新调用 Director。

---

# 60. 最关键的 Ownership Chain

系统最重要的责任链可以最终简化为：

```text
BriefService
      ↓
ScriptPlanner
      ↓
ShootingPlanner
      ↓
AssetIngest
      ↓
ShotDetector
      ↓
Understanding
      ↓
BeatAnalysis
      ↓
Director
      ↓
ShotResolver
      ↓
EDLBuilder
      ↓
Renderer
      ↓
ReviewService
```

但这不是一条不可跳过的巨型函数。

每一阶段都产生：

**独立、持久、可 revision 的 Artifact / Domain Object。**

---

# 61. 四层核心语义最终对应到模块

## Requirement

```text
ShootingPlanner
     ↓
ShotRequirement
```

---

## Fact

```text
AssetIngest
ShotDetector
Understanding
BeatAnalysis
     ↓
Asset / Shot / BeatMap
```

---

## Editorial Decision

```text
Director
ShotResolver
     ↓
EditPlan / ResolutionDecision
```

---

## Execution Decision

```text
EDLBuilder
     ↓
EDL
```

Renderer：

只执行。

Reviewer：

只评估。

这是系统最根本的职责分离。

---

# 62. 建仓前最终 Invariants

Architecture Contract v0.1.2 正式冻结：

1. **只有 Domain Owner 能创建对应对象的新 revision。**
2. **Storage 没有领域决策权。**
3. **Pipeline 没有创作权。**
4. **Agent 没有 Domain ownership。**
5. **Provider 不产生正式 Asset。**
6. **ShotDetector 只决定 Shot boundary。**
7. **Understanding 不允许改变 Shot identity。**
8. **BeatAnalysis 不允许产生剪辑决定。**
9. **Director 不允许冻结 source timestamp。**
10. **Resolver 不允许修改 Director intent。**
11. **EDLBuilder 是唯一 Timeline authority producer。**
12. **Renderer 不允许修改 EDL。**
13. **Review 不允许直接修改被审对象。**
14. **所有外部输入在进入 Domain 前必须通过 Adapter/Validation。**
15. **所有 AI 输出都只是 Proposal，验证后才能 Commit。**
16. **所有远程媒体必须经过 Asset Ingest。**
17. **所有剪辑素材必须能够追溯到 Asset。**
18. **所有 EDL 决策必须能够追溯到 EditPlan / ResolutionDecision。**
19. **修改只重新计算受影响的下游模块。**
20. **架构模块边界不得为了方便调用外部 SDK 而反向污染 Domain。**

---

# 63. Architecture Contract v0.1.x 收口

经过：

### v0.1

我们回答了：

> 系统里有哪些核心对象？

---

### v0.1.1

我们回答了：

> 它们之间如何引用、匹配和演化？

---

### v0.1.2

我们回答了：

> 谁拥有它们、谁可以修改、模块如何协作？

因此建仓之前真正需要冻结的三层契约已经完成：

```text
DOMAIN
   ↓
RELATION
   ↓
OWNERSHIP
```

系统的长期核心因此不再取决于某个开源项目的目录结构。

FireRed、MoneyPrinterTurbo、CutClaw、BeatSync Engine 都已经被降到正确的位置：

> **它们贡献实现、经验和思想，而不定义我们的系统本体。**

---

# 64. Repository Readiness Decision

Architecture Contract v0.1.2 完成后：

**架构条件已经满足正式建仓要求。**

下一阶段不再继续增加 Architecture Contract 版本。

后续只有在真实编码发现契约矛盾时，才通过 ADR / Contract Amendment 修改。

下一阶段应该进入：

# Repository Bootstrap v0.1

只建立：

- repo skeleton
- package boundaries
- Domain schemas
- Port interfaces
- basic repository abstraction
- test skeleton
- lint / typecheck / CI
- upstream LICENSE / NOTICE attribution
- Architecture Contract 文档

**暂不实现 AI 剪辑功能。**

先把我们已经冻结的架构真正变成一个无法轻易走歪的代码骨架。