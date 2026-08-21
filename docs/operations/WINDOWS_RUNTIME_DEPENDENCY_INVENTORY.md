# Windows Runtime Dependency Inventory

**状态：** ACTIVE PACKAGING INPUT  
**更新日期：** 2026-08-22  
**目的：** 把“开发机上曾经装过什么”变成可审计的 runtime/component 清单，为 Windows `onedir`、release manifest、license review 和 clean-machine-ish smoke 提供输入。  
**权威边界：** 本文件不批准重分发任何二进制/模型；分发许可仍以 Upstream Ledger、ADR、LICENSE_STATUS 和正式 release review 为准。

---

# 1. 分类规则

- **CORE-NOW** — 当前普通 Stage-A 产品路径实际需要。
- **RETAINED-1.0-GATE** — 1.0 明确保留，但仍需发行组件闭包或最终 Human Gate。
- **OPTIONAL/ADVANCED** — 历史已验证或未来增强能力，不应无条件进入 first bundle。
- **DEV/PROBE** — 开发/验证专用，不属于客户 runtime contract。
- **REMOTE** — 云能力不随包分发，但 adapter/config/secret/network diagnostics 属于 runtime。

一个依赖出现在仓库、开发环境或历史 probe 中，不代表它自动成为正式 release BOM。

---

# 2. Python 3.12 + Tcl/Tk

**状态： CORE-NOW**

`pyproject.toml` 要求 Python `>=3.12`；普通桌面壳层使用 stdlib `tkinter` / `ttk`。

Packaging 要求：

- frozen app 自带 private Python runtime；
- Tcl/Tk DLL/data正确收集；
- 普通用户不安装 Python/uv；
- 中文 IME/Unicode path、100/125/150% scaling smoke；
- stdlib `sqlite3`, `urllib`, `json`, `hashlib`, `pathlib`, `tempfile`, `subprocess`, `wave` 等随 frozen runtime 正常可用。

当前 provider adapters 大量使用 stdlib HTTP，因此不需要为了打包引入 vendor SDK 大框架。

---

# 3. FFmpeg / ffprobe

**状态： CORE-NOW**

当前用途已经覆盖：

- media probe；
- frame extraction；
- render；
- source audio / BGM decode、mix、execution；
- subtitle ASS execution；
- 部分本地媒体辅助。

PR #13 增加了 approved repository-local `.tools/ffmpeg-8.1/...` lookup fallback，使开发机普通路径不必手工配置 PATH。

**这不是发行 contract。** `.tools` 属于默认 attention-excluded 开发环境，不能被 installer/onedir 当成资源根。

Packaging 必须建立独立 resource/runtime locator，并从明确 packaging manifest 放入 approved FFmpeg/ffprobe component。

ADR-001 release hard gate继续要求：

- exact version/build configuration；
- external libraries；
- hashes/source provenance；
- notices；
- LGPL/GPL/codec/legal review。

禁止从未知下载站拿一个“能跑”的 exe 直接打包。

---

# 4. TransNetV2 shot detection

**状态： CORE-NOW**  
**reviewed runtime path：** `transnetv2-pytorch==1.0.5`

运行时涉及：

- `numpy`；
- `torch`；
- `transnetv2_pytorch`；
- reviewed weights `transnetv2-pytorch-weights.pth`。

Stage-A 普通 Windows baseline优先 CPU-only。

Packaging 必须闭环：

- exact CPU dependency set；
- Torch/native DLL；
- weights provenance/hash/license；
- hidden imports/native collection；
- clean-machine model load；
- startup/RAM现实表现。

不要因为开发机有 GPU 就 bundle CUDA。

---

# 5. Cloud reasoning / visual providers

**状态： REMOTE / CORE-NOW**

## Reasoning / Direction

当前 concrete provider是 DeepSeek HTTP adapter。

## Visual Understanding

当前 concrete providers是 Gemini / OpenAI image-frame adapters。

当前产品事实：它们不是 provider-neutral remote-video/native-video observation providers。因此 remote reference URL 已从普通 1.0 GUI 隐藏，`ReferenceObservation` 方向延期到 2.0。

Packaging rule：

- bundle adapter code，不 bundle API key；
- protected credential仍是 user-scoped；
- profile不落 plaintext secret；
- Doctor/default startup不偷偷烧 API quota；
- provider failure/quota明确诊断，不静默换厂；
- remote-reference Bilibili/Douyin/Xiaohongshu observation不是 first package dependency。

---

# 6. SQLite / Project Workspace persistence

**状态： CORE-NOW**

使用 stdlib `sqlite3`，当前 project-local核心包括：

- schema versioning/migrations；
- revisioned repositories；
- transactional write/rollback；
- `project.sqlite3`；
- content-addressed artifacts等现有 project-owned state。

Packaging 前的 Workspace/UX wave进一步规定：

> 用户选择的 `Project Workspace` 是 project-specific writable root；安装目录默认只读。

逻辑上可承载：

```text
project.sqlite3
artifacts/
cache/
work/       # drafts/autosave/bounded undo-redo/session scratch
logs/
provider_audio/
outputs/
```

不要把 canonical Domain state为了目录好看复制成第二份 JSON authority。

Packaging smoke还需要关注中文路径、OneDrive/移动盘/lock行为，以及 same-project multi-instance 的产品语义。

---

# 7. Music / BeatMap / Audio Editorial / public BGM

**状态： CORE-NOW**

旧结论“尚未进入普通 Editing ProductFlow”已经过时。

PR #11 与真实 no-speech Human Gate已经证明 ordinary path 可完成：

```text
rights-safe public music discovery/acquisition
→ BeatMap
→ Audio Editorial
→ canonical EDL
→ FFmpeg execution
→ final MP4
```

用户真人确认 source audio存在、BGM存在且自然。

当前实现包含：

- deterministic `WaveEnergyBeatAnalysisService`；
- source-audio mix；
- Openverse/Wikimedia discovery/acquisition；
- rights verification/provenance；
- local rights-attested music path。

Packaging 需要网络 timeout/proxy/diagnostic继续成立，但不要把固定音乐素材塞进 bundle来绕过 rights/provider logic。

---

# 8. Subtitle execution + speech recognition

## Structured subtitle execution

**状态： CORE-NOW**

旧结论“完整普通 ProductFlow 尚未接入”已经过时。

当前已有：

- trusted `SpeechTranscript` evidence；
- deterministic cue compilation；
- typed basic subtitle styles；
- canonical EDL codec；
- FFmpeg/ASS execution；
- explicit subtitle stage diagnostics。

Stage-A no-speech真人链已证明：没有可信 speech evidence 时可以 `SKIPPED/NO_SPEECH`，不得伪造字幕，也不得因此让整个 Editing失败。

## faster-whisper speech runtime

**状态： RETAINED-1.0-GATE**  
**optional extra：** `speech-runtime = faster-whisper==1.2.1`

已冻结/历史使用的基础语义包括：

- CPU/int8优先；
- local/pinned model；
- 不允许缺模型时偷偷在线下载；
- grounded speech存在而字幕能力被要求时，runtime/model unavailable必须准确 fail closed。

Packaging 未决项：

- CTranslate2/native DLL closure；
- approved model exact revision/hash/license/size；
- first bundle直接包含，还是明确的受控 component安装路径；
- CPU速度/RAM；
- Doctor/component状态；
- clean-machine single-speaker Human Gate。

最终 1.0必须在目标发行配置上证明：

`clear single speaker → original speech preserved → trusted basic subtitles → source audio + BGM → final MP4`

---

# 9. Speech synthesis and advanced audio separation

## `SpeechSynthesisPort`

**状态： 2.0 SEAM ONLY**

1.0普通 UI不应暴露无 backend 的 synthetic voice成功路径。不要因为 port存在就把任何 TTS runtime塞进 first bundle。

## `AudioSeparationPort`

**状态： 2.0 SEAM ONLY**

高级 speech/ambience separation、stem persistence与advanced mixing延期。First 1.0 package不需要为此增加模型/runtime。

---

# 10. Silero VAD

**状态： OPTIONAL/ADVANCED**

历史固定证据包括 Silero VAD 6.2.1、ONNX model、numpy + onnxruntime路径。

不要把历史 R0.8 evidence 自动解释成 first bundle hard dependency。只有当前 ordinary 1.0 dependency audit证明必须时才进入 BOM。

若未来加入：记录 model hash/license/runtime DLL并做 frozen probe。

---

# 11. Sentence Transformers / multilingual E5

**状态： OPTIONAL/ADVANCED**

历史 R0.8/R0.9 用于 hybrid semantic retrieval。

First package是否需要 dense retrieval必须由当前 ordinary Resolver path dependency audit回答；不能因为“以前用过”就默认把大模型/transformers依赖打进去，也不能无证据宣称永久不需要。

---

# 12. Spatial / MediaPipe recovery

**状态： base spatial semantics RETAINED；recovery provider OPTIONAL/ADVANCED**

R0.11 SpatialComposer/Reframe execution是已验证产品能力的一部分。

但 MediaPipe recovery candidate使用的 external EfficientDet Lite0 model仍有：

`RELEASE_LICENSE_PENDING`

因此：

- base spatial capability ≠ 必须 bundle该 recovery model；
- license未闭环前不进入默认商业 bundle；
- optional component缺失时保持明确 baseline/fallback。

---

# 13. Remote reference acquisition fallback

**状态： DEV/ENGINEERING FALLBACK；普通 1.0 UI 不暴露**

PR #13保留：

- bounded Direct HTTPS acquisition；
- Bilibili public metadata/acquisition adapter；
- HTTPS/SSRF/DNS/public-IP/IP-pinning/redirect/MIME/size/timeout/provenance等保护。

真实 BV曾达到 acquisition → ffprobe → video-only ingest → TransNet 7 shots。

但产品已经决定：参考 URL真正目标是未来 provider-neutral AI observation，而不是默认下载并做剪辑级解析。

因此：

- 不把 Bilibili remote URL作为 first package Product Gate；
- 不增加 Douyin/Xiaohongshu adapter；
- 相关 provider-specific fallback code随主包存在可以接受，但其网络路径不是普通1.0启动/Planning的mandatory dependency；
- 2.0重新启用时再建立 `ReferenceObservationPort` 与 provider capability contract。

---

# 14. Preview runtime

**状态： OPTIONAL/PRODUCT UX — release choice未冻结**

历史有 GStreamer/VLC/libmpv candidate与真实 benchmark。

Packaging rule：

- 不把多个大型 preview runtime全塞进 first bundle；
- preview failure不得破坏 canonical render output；
- 若选择一个 production route，再单独记录 exact build/plugin/license与 frozen load probe。

---

# 15. UI framework + brand resources

**Tk/Ttk： CORE-NOW**

First package继续 stock ttk，当前没有必要仅为视觉升级引入新 UI runtime。

Packaging前 Workspace/UX wave还需要确定：

- 主界面统一配置入口；
- form-level Clear/Undo/Redo；
- vertical accordion；
- canonical brand asset。

当前 Canvas pixel-camera只是临时生成 mark，不应被 packaging永久冻结。优先恢复已被用户认可的 feather asset；找不到就保留 Human Gate，不凭记忆重画。

Canonical icon一旦确定，应通过 resource locator供 splash/window/taskbar/exe/installer按平台格式使用。

---

# 16. First Windows `onedir` 候选 mandatory BOM

在 Workspace/UX consolidation后，从**实际普通1.0路径**重新生成最终 BOM。

当前候选最小集合：

```text
Python 3.12 private runtime + Tcl/Tk
video-editing-agent package
approved FFmpeg / ffprobe component
TransNetV2 CPU runtime + reviewed weights
stdlib SQLite/HTTPS
current cloud provider adapter code
public-music / source-audio / EDL / subtitle execution code
approved speech runtime + model/component strategy
canonical UI resources + licenses/notices/version manifest
```

`Silero/E5/MediaPipe recovery/preview runtime`等必须根据真实 dependency audit和license状态决定，不自动进入。

这仍是候选，不是最终 release BOM。

---

# 17. Fresh-machine dependency smoke matrix

| Case | Expected |
|---|---|
| 无 Python | App启动 |
| 无 uv | App启动 |
| 无开发 repo | App启动 |
| PATH无 ffmpeg | packaged runtime locator找到 approved FFmpeg/ffprobe |
| 不存在开发 `.tools` | App不依赖它 |
| 新 Project Workspace | 能创建/打开，writable state不进入 install dir |
| 中文用户名/路径 | project/profile/output可读写 |
| 125%/150% DPI | UI无关键裁切 |
| TransNet weights缺失 | Doctor明确 capability unavailable，不隐式下载 |
| speech component缺失 | Doctor/UI准确说明；no-speech无关路径不被误杀 |
| clear speech + approved speech component | basic trusted subtitle路径可执行 |
| Provider secret缺失 | 设置面提示，不崩溃 |
| Provider 429 | 明确 quota/wait UX，不换厂 |
| public music网络不可用 | 清楚诊断/合法失败，不伪造 rights |
| optional recovery model缺失 | 明确降级，不阻断无关路径 |
| output已存在 | 显式确认/另存，不静默覆盖 |
| Review non-PASS | candidate不发布到 final path |
| 删除/卸载 bundle | 用户 Project Workspace / Profiles不被删除 |

---

# 18. 下一步

1. 完成 `STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`；
2. 从该 accepted ordinary UI/ProductFlow重新审计 import/runtime dependency，生成最终 mandatory/optional BOM；
3. 建立 thin desktop bootstrap + frozen/dev resource/runtime locator；
4. pin first bundler，checked-in onedir spec/config；
5. 生成 release/component/license manifest；
6. Windows clean-machine-ish onedir probe；
7. 运行 retained Planning、no-speech Editing、single-speaker subtitle Human Gate；
8. 只有 package + license + Product/Human Gate都通过后再选择 installer/onefile/update路线并考虑 Stage-A 100%。
