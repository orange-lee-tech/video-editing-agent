# Architecture Contract v0.1.1
## Object Relations & Schema Matrix

**状态：Draft Baseline**  
**上游契约：Architecture Contract v0.1**  
**目标：冻结核心对象字段类别、引用方向、生命周期，以及 ShotRequirement → Shot → EditSlot → EDLSegment 的匹配契约。**

---

# 0. 字段分类标准

本契约统一使用：

- **R — Required**
  - 对象进入 `valid` 状态前必须存在。
  - 缺失意味着对象本身不完整。

- **O — Optional**
  - 合法缺省。
  - 缺失不得阻止对象持久化或进入下游。

- **D — Derived**
  - 由其他事实计算、分析或聚合得到。
  - 不应作为用户或 Agent 的原始权威输入。
  - 可以缓存，但必须能够从其来源重新生成。

## 0.1 一个字段只能有一个主语义

例如：

`Shot.duration`

属于 **D**：

```text
duration = source_end - source_start
```

不能同时允许：

Agent 输入 duration=4.2s

而：

source_start/source_end 实际得到 3.8s。

权威事实只有一份。

---

# 1. Core Entity Envelope

九个顶级领域对象统一拥有：

| 字段 | 类型 | 分类 | 说明 |
|---|---|---:|---|
| id | EntityId | R | 稳定身份 |
| revision | Integer | R | 从 1 开始 |
| schema_version | String | R | 如 `0.1.1` |
| status | Enum | R | draft / valid / stale / archived |
| created_at | Timestamp | R | 创建时间 |
| created_by | ActorRef | R | user / system / agent |
| derived_from | EntityRevisionRef[] | O | 明确上游来源 |
| metadata | Map | O | 非核心扩展信息 |

## 1.1 EntityRevisionRef

所有跨对象引用必须原则上锁定 revision：

```text
EntityRevisionRef
├─ entity_id
└─ revision
```

禁止核心对象只保存：

```text
script_id = "scp_123"
```

而不确定引用的是哪一版 ScriptPlan。

---

# 2. 对象关系总图

```text
Brief
  │ 1
  ▼
ScriptPlan
  │ 1
  ▼
ShootingPlan
  │
  └── ShotRequirement[*]
                 │
                 │ semantic requirement
                 ▼
            Shot Resolver
                 ▲
                 │
Asset 1 ────── * Shot
                 │
                 │ candidates
                 ▼
             EditPlan
               │
               └── EditSlot[*]
                        │
                        ▼
                       EDL
                        │
                        └── EDLSegment[*]
                                 │
                                 ▼
                               Render
                                 │
                                 ▼
                            ReviewReport

Audio Asset
     │
     ▼
   BeatMap
     │
     └──────────────► EditPlan
```

---

# 3. Brief Schema Matrix

## 3.1 Brief

| 字段 | 分类 | 说明 |
|---|---:|---|
| title | R | 项目/视频工作标题 |
| objective | R | 视频目的 |
| audience | R | 目标受众 |
| platform | R | 发布平台或 generic |
| target_duration | R | 目标时长范围 |
| aspect_ratio | R | 9:16 / 16:9 / 1:1 等 |
| core_message | R | 必须传递的核心信息 |
| language | R | 主要语言 |
| style_intent | O | 风格描述 |
| emotional_intent | O | 情绪目标 |
| call_to_action | O | CTA |
| references | O | 参考视频/文案/案例 |
| brand_constraints | O | 品牌约束 |
| prohibited_content | O | 禁止内容 |
| user_notes | O | 用户额外要求 |
| success_criteria | O | 成功标准 |
| normalized_constraints | D | 系统规范化后的约束 |

## 3.2 Brief 不允许引用

Brief 不得直接引用：

- Asset
- Shot
- BeatMap
- EditPlan
- EDL

Brief 是根意图。

---

# 4. ScriptPlan Schema Matrix

## 4.1 ScriptPlan

| 字段 | 分类 | 说明 |
|---|---:|---|
| brief_ref | R | 精确 Brief revision |
| title | R | 视频标题/工作标题 |
| target_duration | R | 脚本目标时长 |
| narrative_strategy | R | 总体叙事策略 |
| sections | R | NarrativeSection[] |
| language | R | 文案语言 |
| tone | O | 语言语气 |
| reference_style | O | 模仿/参考风格 |
| global_visual_intent | O | 总体视觉方向 |
| global_music_intent | O | 总体音乐方向 |
| estimated_duration | D | section 聚合 |
| coverage_report | D | 是否覆盖 Brief 核心信息 |

## 4.2 NarrativeSection

| 字段 | 分类 |
|---|---:|
| section_id | R |
| narrative_role | R |
| information_goal | R |
| narration | R |
| target_duration | R |
| visual_intent | R |
| pacing | O |
| emotion | O |
| subtitle_intent | O |
| transition_intent | O |
| importance | O |
| estimated_spoken_duration | D |

### narrative_role

v0.1.1 支持：

- hook
- setup
- development
- proof
- demonstration
- climax
- transition
- CTA
- outro
- custom

---

# 5. ShootingPlan Schema Matrix

## 5.1 ShootingPlan

| 字段 | 分类 |
|---|---:|
| script_plan_ref | R |
| requirements | R |
| production_notes | O |
| shooting_order | O |
| estimated_shooting_effort | D |
| required_coverage | D |
| optional_coverage | D |

---

# 6. ShotRequirement Schema Matrix

`ShotRequirement` 是本契约第一条核心匹配链的起点。

它表达：

> **我们需要什么镜头。**

而不是：

> 我们已经有哪个镜头。

## 6.1 ShotRequirement

| 字段 | 分类 | 说明 |
|---|---:|---|
| requirement_id | R | ShootingPlan 内稳定 ID |
| script_section_ref | R | 对应 NarrativeSection |
| purpose | R | 该镜头的叙事作用 |
| subject | R | 希望看到什么主体 |
| target_duration | R | 期望使用时长范围 |
| priority | R | required / preferred / optional |
| source_policy | R | 素材来源规则 |
| visual_intent | R | 视觉语义需求 |
| action | O | 主体动作 |
| environment | O | 场景 |
| framing | O | 景别 |
| camera_motion | O | 运镜 |
| orientation | O | 特殊画面方向 |
| dialogue_requirement | O | 是否要求对应对白 |
| audio_requirement | O | 是否要求现场声音 |
| continuity_hint | O | 与其他镜头的连续性关系 |
| positive_keywords | O | 正面搜索语义 |
| negative_keywords | O | 排除语义 |
| remote_search_queries | O | 公网素材检索建议 |
| fallback_policy | O | 不足时如何降级 |
| normalized_constraints | D | Resolver 使用的标准化约束 |

---

# 7. source_policy Contract

v0.1.1 冻结：

```text
captured_only
local_only
local_preferred
remote_allowed
remote_only
generated_allowed
```

含义：

### captured_only

只能使用用户本次或历史拍摄的原创素材。

### local_only

可使用用户本地已有素材，但禁止公网补充。

### local_preferred

先找本地；无法达到最低要求后允许公网。

### remote_allowed

本地和公网均可。

### remote_only

明确要求使用公网素材。

### generated_allowed

在其他允许来源不足时，可进入未来生成式素材链。

## 强约束

`source_policy` 属于 **Hard Constraint**。

Shot Resolver 不得自行违反。

---

# 8. Asset Schema Matrix

## 8.1 Asset

| 字段 | 分类 |
|---|---:|
| media_kind | R |
| origin | R |
| storage_ref | R |
| content_hash | R |
| byte_size | R |
| provenance | R |
| duration | D |
| width | D |
| height | D |
| fps | D |
| codec | D |
| audio_channels | D |
| sample_rate | D |
| imported_at | R |
| user_labels | O |
| collection_refs | O |

## 8.2 provenance

| 字段 | 分类 |
|---|---:|
| origin_type | R |
| provider | O |
| provider_asset_id | O |
| source_page | O |
| creator | O |
| retrieved_at | O |
| license_information | O |
| attribution | O |

本地拍摄 Asset：

```text
provider = null
origin_type = captured
```

完全合法。

---

# 9. Shot Schema Matrix

Shot 表达：

> **我们真实拥有的一个可剪辑素材区间。**

## 9.1 Shot Identity

| 字段 | 分类 |
|---|---:|
| asset_ref | R |
| source_start | R |
| source_end | R |
| duration | D |
| boundary_method | R |
| previous_shot_ref | O |
| next_shot_ref | O |
| scene_ref | O |

---

## 9.2 Shot Technical Understanding

| 字段 | 分类 |
|---|---:|
| resolution | D |
| blur_score | D |
| exposure_score | D |
| shake_score | D |
| noise_score | D |
| technical_quality_score | D |

---

## 9.3 Shot Semantic Understanding

| 字段 | 分类 |
|---|---:|
| caption | D |
| subjects | D |
| people | D |
| faces | D |
| objects | D |
| actions | D |
| environment | D |
| framing | D |
| camera_motion | D |
| keywords | D |
| topics | D |
| emotion | D |
| aesthetic_score | D |
| embedding_ref | D |

全部属于 Derived。

**Agent 不可以通过修改 Shot 来“要求”素材是什么。**

---

## 9.4 Shot Speech Understanding

| 字段 | 分类 |
|---|---:|
| transcript | D |
| speakers | D |
| speech_ranges | D |
| dialogue_quality | D |

---

# 10. BeatMap Schema Matrix

## 10.1 BeatMap

| 字段 | 分类 |
|---|---:|
| audio_asset_ref | R |
| duration | D |
| bpm | D |
| bpm_confidence | D |
| beats | D |
| downbeats | D |
| accents | D |
| phrase_anchors | D |
| sections | D |
| energy_curve | D |
| onset_curve | D |
| drops | D |
| build_ups | D |
| breakdowns | D |
| chorus_ranges | D |
| time_signature | O/D |

### 核心规则

BeatMap 中所有音乐分析字段均是：

**D — Derived**

因为它们描述的是被分析音乐的客观/模型分析结果。

---

# 11. EditPlan Schema Matrix

## 11.1 EditPlan

| 字段 | 分类 |
|---|---:|
| script_plan_ref | R |
| shooting_plan_ref | R |
| asset_catalog_snapshot_ref | R |
| slots | R |
| editorial_strategy | R |
| beatmap_ref | O |
| user_edit_instruction | O |
| target_duration | R |
| pacing_strategy | O |
| global_source_policy | O |
| continuity_strategy | O |
| resolved_coverage | D |
| unresolved_slots | D |

---

# 12. EditSlot Schema Matrix

EditSlot 表达：

> **导演决定这里需要放一个怎样的镜头。**

ShotRequirement 是生产阶段需求。

EditSlot 是剪辑阶段需求。

两者不能合并。

## 12.1 为什么必须分开

拍摄时：

> 我需要一段木工刨木头的特写。

剪辑时可能发现：

> Hook 位置实际上需要 0.8 秒极短动作镜头。

也可能同一个 ShotRequirement：

被剪成两个 EditSlot。

或者多个 ShotRequirement：

在剪辑时被一个素材镜头同时满足。

因此 cardinality 不是 1:1。

---

## 12.2 EditSlot

| 字段 | 分类 |
|---|---:|
| slot_id | R |
| script_section_ref | R |
| narrative_role | R |
| purpose | R |
| target_timeline_range | R |
| target_duration | R |
| desired_visual | R |
| source_policy | R |
| requirement_refs | O |
| pacing | O |
| selection_constraints | O |
| continuity_constraints | O |
| reuse_policy | O |
| music_alignment_policy | O |
| transition_intent | O |
| candidate_shot_refs | D |
| resolution_status | D |
| selected_shot_ref | D |
| resolution_score | D |

### 注意

`selected_shot_ref` 虽然最终会确定，

但仍属于 **D**：

因为它是 Shot Resolver 根据：

EditSlot + Shot Catalog

计算得到的 resolution。

不能让 EditPlan 作者直接把它当成原始事实。

如果用户明确手动指定：

应记录为 Resolver 的：

`manual_override`

而不是破坏数据语义。

---

# 13. EDL Schema Matrix

## 13.1 EDL

| 字段 | 分类 |
|---|---:|
| edit_plan_ref | R |
| tracks | R |
| timeline_duration | D |
| output_canvas | R |
| output_fps | R |
| audio_policy | R |
| validation_state | D |
| render_hints | O |

---

# 14. EDLSegment Schema Matrix

EDLSegment 表达：

> **实际执行哪一个媒体区间。**

| 字段 | 分类 |
|---|---:|
| segment_id | R |
| slot_ref | O |
| track | R |
| asset_ref | R |
| shot_ref | O |
| source_in | R |
| source_out | R |
| timeline_in | R |
| timeline_out | R |
| duration | D |
| playback_rate | R |
| crop | O |
| scale | O |
| position | O |
| opacity | O |
| audio_gain | O |
| transition_in | O |
| transition_out | O |
| effect_refs | O |
| subtitle_ref | O |

## 14.1 Source authority

如果 `shot_ref` 存在：

```text
shot.source_start
    ≤ source_in
    < source_out
    ≤ shot.source_end
```

必须成立。

---

# 15. ReviewReport Schema Matrix

## 15.1 ReviewReport

| 字段 | 分类 |
|---|---:|
| stage | R |
| target_ref | R |
| checks | R |
| passed | D |
| findings | D |
| metrics | D |
| suggested_actions | D |
| reviewer_type | R |
| reviewed_at | R |

stage：

- candidate
- edl
- render

---

# 16. 核心匹配链 Contract

现在正式冻结：

# ShotRequirement → Shot → EditSlot → EDLSegment

这不是简单的一条 1:1 映射。

实际关系是：

```text
ShotRequirement
      │
      │ production intent
      ▼
   Shot Catalog
      │
      │ matching / retrieval
      ▼
    EditSlot
      │
      │ resolution
      ▼
  EDLSegment
```

更准确的语义是：

```text
ShotRequirement ──┐
                  ├──► EditSlot
ScriptSection ────┘
                       │
                       │ asks for
                       ▼
                    Resolver
                       ▲
                       │
                      Shot
                       │
                       ▼
                  EDLSegment
```

---

# 17. ShotRequirement → Shot 匹配契约

这一步不是最终剪辑。

它回答：

> 现实素材库中，哪些 Shot 有资格满足这个需求？

---

## 17.1 两阶段匹配

必须分：

### Phase A — Eligibility Gate

处理 Hard Constraints。

不满足即：

```text
INELIGIBLE
```

不进入排名。

---

### Phase B — Candidate Ranking

只对 Eligible Shots 评分。

---

# 18. Hard Constraint Contract

v0.1.1 冻结以下约束必须支持硬过滤：

### Source

- origin
- source_policy

### Duration

Shot 必须提供：

足够的可使用 source duration。

### Media Kind

例如：

要求 video，

不能拿 image 替代，除非 fallback policy 明确允许。

### Dialogue

如果 requirement 明确要求某句对白，

必须存在对应 transcript range。

### Forbidden Content

不得违反 Brief / Requirement 的禁止条件。

### Mandatory Subject

如果要求特定人物/物体且该条件为 strict：

Shot 必须满足。

---

# 19. Soft Matching Dimensions

Eligible Shot 的匹配评分至少可以考虑：

```text
semantic_fit
visual_fit
action_fit
framing_fit
motion_fit
duration_fit
technical_quality
aesthetic_quality
dialogue_fit
continuity_fit
novelty
source_preference
```

## v0.1.1 不冻结具体权重

例如：

```text
semantic 0.35
quality 0.2
...
```

暂时**禁止写进领域契约**。

权重属于 Resolver Strategy。

以后可以替换算法而不改变领域对象。

---

# 20. Candidate Match Result

建议引入一个**非顶级持久化领域对象**：

`ShotMatch`

作为 Resolver 内部结构。

```text
ShotMatch
├─ requirement_ref
├─ shot_ref
├─ eligible
├─ rejection_reasons[]
├─ scores
│  ├─ semantic
│  ├─ visual
│  ├─ action
│  ├─ technical
│  └─ ...
├─ total_score
└─ evidence
```

它不是核心九对象之一。

但它让 Resolver 的决定可解释。

---

# 21. ShotRequirement 不直接生成 EDLSegment

禁止：

```text
ShotRequirement
     ↓
EDLSegment
```

因为中间缺失了：

**导演决策。**

必须经过：

`EditSlot`

---

# 22. ShotRequirement → EditSlot Contract

ScriptPlan + ShootingPlan 进入 Auto Edit 后，

Director 可以：

### 1 Requirement → 1 Slot

普通情况。

---

### 1 Requirement → N Slots

例如：

一个“制作过程”要求，

剪辑时拆成：

- 刨木
- 雕刻
- 打磨

三个节奏镜头。

---

### N Requirements → 1 Slot

例如一个 Shot 同时：

展示人物  
+ 展示产品  
+ 展示工作场景

可以合并成一个 EditSlot。

---

### Requirement → 0 Slot

如果：

- 它是 optional
- 剪辑结构不再需要
- 用户修改了最终叙事

完全合法。

但是：

如果 `priority = required`

而最终没有任何 Slot 承担它，

EditPlan 必须产生：

```text
coverage_violation
```

---

# 23. EditSlot → Shot Resolution Contract

Resolver 的输入：

```text
EditSlot
AssetCatalogSnapshot
ShotIndex
optional BeatMap context
already_selected_shots
continuity_context
```

输出：

```text
ResolutionDecision
```

---

# 24. ResolutionDecision

建议作为 Application 层正式数据结构：

```text
ResolutionDecision
├─ slot_ref
├─ selected_shot_ref
├─ selected_source_window
├─ match_score
├─ decision_type
├─ reasons
├─ alternatives[]
└─ warnings[]
```

decision_type：

- automatic
- manual_override
- remote_fallback
- generated_fallback
- unresolved

它不是顶级 Domain Entity。

但应该作为 Artifact 保存。

这样用户未来可以知道：

> AI 为什么选择了这个镜头？

---

# 25. selected_source_window Contract

非常重要：

Shot Resolver 不只是选 Shot，

还可以进一步决定：

```text
source_in
source_out
```

但必须位于：

Shot boundary 内。

因此：

```text
Shot
    ↓
ResolutionDecision
        selected_source_window
    ↓
EDLSegment
```

这吸收了 CutClaw：

`shot_plan → shot_point`

的核心思想，

但变成 typed contract。

---

# 26. EditSlot → EDLSegment Contract

通常：

```text
1 EditSlot
→
1 EDLSegment
```

但允许：

### 1 Slot → N Segments

例如一个节奏 Slot：

目标 3 秒，

可以用：

```text
Shot A 1s
Shot B 1s
Shot C 1s
```

---

### N Slots → 1 Segment

v0.1.1：

**禁止自动合并。**

每一个 EDLSegment 最多只绑定一个 `slot_ref`。

如果一个真实长镜头承担两个连续 Slot，

EDL 中仍应：

逻辑上拆成两个 Segment。

这样保持：

**叙事追溯性。**

---

# 27. EDL Segment Generation Rule

EDLSegment 必须由：

```text
EditSlot
+
ResolutionDecision
+
Timeline Allocation
```

共同生成。

不是单纯：

```text
Shot → EDLSegment
```

因为 Shot 不知道：

- 成片时间位置
- BGM
- Narration
- Transition
- Playback Rate
- Crop
- Timeline constraints

---

# 28. Music Alignment Contract

EditSlot 可以表达：

```text
music_alignment_policy
```

例如：

- none
- loose
- beat_preferred
- downbeat_preferred
- phrase_anchor
- drop_anchor
- section_boundary

还可以包含：

```text
tolerance_ms
```

例如：

```text
phrase_anchor
±250 ms
```

## 关键规则

BeatMap 提供：

```text
candidate musical anchors
```

EditSlot 决定：

```text
desired alignment
```

Timeline Allocator 最终决定：

```text
actual timeline position
```

因此职责关系是：

```text
BeatMap
   ↓ facts

EditPlan
   ↓ intention

EDL
   ↓ decision
```

---

# 29. Timeline Authority Contract

时间信息分三类。

## Source Time

属于：

Shot / EDL。

表示：

源媒体中的位置。

---

## Narrative Time

属于：

ScriptPlan / EditPlan。

表示：

预期阶段和预算。

---

## Timeline Time

最终权威只属于：

EDL。

只有 EDL 可以正式定义：

```text
timeline_in
timeline_out
```

---

# 30. Coverage Contract

ShootingPlan 必须能够生成：

`CoverageState`

用于描述真实素材是否满足拍摄要求。

对于每个 ShotRequirement：

```text
unmatched
weak
satisfied
overcovered
```

CoverageState 为 Derived。

例如：

```text
REQ-01
required
→ 0 eligible shots
→ unmatched

REQ-02
preferred
→ 1 mediocre shot
→ weak

REQ-03
required
→ 4 high-quality shots
→ satisfied
```

这可以直接产生：

> 还需要补拍什么？

---

# 31. Remote Material Fallback Contract

只有当：

```text
source_policy
```

允许远端素材时，

Resolver 才能调用 MaterialProvider。

逻辑：

```text
Local Shot Search
      │
      ├── sufficient
      │      ↓
      │    continue
      │
      └── insufficient
             │
             ▼
      Check source_policy
             │
             ├── remote forbidden
             │       ↓
             │    unresolved
             │
             └── remote allowed
                     ↓
              MaterialProvider
                     ↓
                  Asset
                     ↓
                Shot/Analysis
                     ↓
                 Resolver
```

公网素材不能绕过：

**Asset → Shot**

直接进入 EDL。

这是强不变量。

---

# 32. AssetCatalog Snapshot Contract

EditPlan 不应该引用：

> “当前文件夹里的素材。”

必须引用一个稳定的：

`AssetCatalogSnapshot`

它至少记录：

```text
snapshot_id
asset revisions
shot-analysis revisions
created_at
```

意义：

同一个 EditPlan 以后重新运行，

能够知道当时它看见的是哪套素材状态。

---

# 33. Staleness Matrix

| 上游改变 | 下游状态 |
|---|---|
| Brief | ScriptPlan stale |
| ScriptPlan | ShootingPlan / EditPlan stale |
| ShootingPlan | EditPlan stale |
| Asset 新增 | EditPlan 不自动 stale，但可标记 new_candidates_available |
| Asset 删除 | 引用它的 EDL stale |
| Shot boundary 改变 | 引用旧 Shot 的 Resolution / EDL stale |
| Shot semantic analysis 更新 | EditPlan 可标记 rerank_available |
| BeatMap 更新 | EditPlan/EDL 可标记 rhythm_replan_available |
| EditPlan 更新 | EDL stale |
| EDL 更新 | Render stale |
| Render 更新 | ReviewReport stale |

---

# 34. Required / Optional / Derived 总矩阵

| 对象 | R 核心 | O 扩展 | D 推导 |
|---|---|---|---|
| Brief | objective/audience/platform/duration/message | reference/style/brand | normalized constraints |
| ScriptPlan | brief_ref/sections/narrative | tone/music intent | duration/coverage |
| ShootingPlan | script_ref/requirements | notes/order | coverage |
| ShotRequirement | purpose/subject/duration/priority/source policy | framing/action/search | normalized constraints |
| Asset | kind/origin/storage/hash/provenance | labels | technical metadata |
| Shot | asset/time boundaries | neighbors/scene | all analysis |
| BeatMap | audio_ref | time signature | music analysis |
| EditPlan | refs/slots/strategy | beatmap/user instruction | coverage/unresolved |
| EditSlot | purpose/time budget/source policy | music/continuity/etc. | candidate/selected shot |
| EDL | plan_ref/tracks/output | hints | timeline duration/validation |
| EDLSegment | asset/source/timeline | effects/transform | duration |
| ReviewReport | stage/target/check set | — | findings/pass/metrics |

---

# 35. 禁止的 Shortcut

v0.1.1 正式禁止：

### ① ScriptPlan → Shot

脚本不能直接“选择文件”。

---

### ② ShootingPlan → EDL

拍摄计划不是剪辑方案。

---

### ③ ShotRequirement → EDLSegment

缺少导演层。

---

### ④ BeatMap → EDLSegment

音乐分析器没有剪辑权。

---

### ⑤ Shot → Timeline

素材不知道自己应该出现在成片什么位置。

---

### ⑥ Agent Text → Renderer

任何自然语言 Agent 输出都必须先经过 typed contract。

---

### ⑦ Remote URL → EDL

远程媒体必须先成为 Asset。

---

### ⑧ Renderer 修改 EDL

Renderer 不得自动改变导演决策。

---

# 36. ShotRequirement → Shot → EditSlot → EDLSegment 最终定义

四个对象分别代表四种完全不同的问题：

## ShotRequirement

> **我们需要什么？**

生产意图。

---

## Shot

> **我们实际上有什么？**

素材事实。

---

## EditSlot

> **最终故事的这个位置需要什么？**

导演决策。

---

## EDLSegment

> **最终到底用哪个媒体区间，放在哪里？**

执行决策。

---

因此整个匹配链正式冻结为：

```text
                PRODUCTION
                    │
                    ▼
            ShotRequirement
                    │
          defines desired footage
                    │
                    ▼
               Shot Index
                    ▲
                    │
                real footage
                    │
                   Shot
                    │
                    │ candidate evidence
                    ▼
                 Director
                    │
                    ▼
                EditSlot
                    │
                    │ resolve
                    ▼
              Shot Resolver
                    │
                    ▼
          ResolutionDecision
                    │
                    ▼
             EDLSegment
                    │
                    ▼
                Renderer
```

---

# 37. Contract v0.1.1 核心不变量

最终冻结以下十二条：

1. **Brief 是意图根。**
2. **ScriptPlan 描述故事，不描述素材文件。**
3. **ShootingPlan 描述应该拍什么，不描述最终剪什么。**
4. **ShotRequirement 是需求，不是候选素材。**
5. **Asset 是真实媒体身份。**
6. **Shot 是 Asset 上的真实可剪辑区间。**
7. **所有 Shot Understanding 都是 Derived。**
8. **BeatMap 只有音乐事实，没有剪辑权。**
9. **EditSlot 是导演需求，不是最终时间线。**
10. **Shot Resolver 负责把导演需求与真实素材连接起来。**
11. **EDL 是唯一最终 Timeline 权威。**
12. **Renderer 只能执行 EDL，不得进行创作决策。**

---

# 38. v0.1.1 的架构意义

至此系统里三个最危险的“万能对象”已经被彻底消灭：

不允许一个：

`Clip`

同时承担：

素材、镜头、剪辑计划、时间线。

不允许一个：

`Script`

同时承担：

旁白、拍摄计划、素材检索词、剪辑决策。

也不允许一个：

`Timeline`

同时承担：

音乐分析、导演意图、Agent 推理、渲染参数。

我们采用的是：

**需求、事实、决策、执行**

四层模型。

```text
Requirement
   ↓
Fact
   ↓
Editorial Decision
   ↓
Execution Decision
```

对应视频系统：

```text
ShotRequirement
   ↓
Shot
   ↓
EditSlot
   ↓
EDLSegment
```

这条链是 Architecture Contract v0.1.1 最重要的成果。