# Windows Runtime Dependency Inventory

**状态：** ACTIVE PACKAGING INPUT  
**日期：** 2026-08-19  
**目的：** 把“开发机上曾经装过什么”变成可审计的 runtime/component 清单，为 Windows `onedir`、installer、license manifest 和 fresh-machine smoke 提供输入。  
**权威边界：** 本文件不批准重分发任何二进制/模型；分发许可仍以 Upstream Ledger、ADR、LICENSE_STATUS、正式 release review 为准。

---

# 1. 分类规则

每个组件标成：

- **CORE-NOW** — 当前普通 Stage-A ProductFlow 已实际需要；
- **CORE-GATE-INTEGRATION** — 冻结 Stage-A Gate 要求，但普通 ProductFlow 还在集成修复中；
- **OPTIONAL/ADVANCED** — 已验证能力或恢复路径，但不应无条件塞进第一个安装包；
- **DEV/PROBE** — 只用于测试/开发，不属于客户 runtime；
- **REMOTE** — 云 API，不随应用打包，但 adapter/config/secret handling 属于 runtime。

一个库出现在仓库里，不代表它自动成为正式 installer dependency。

---

# 2. 当前最小普通 GUI/runtime 闭包

## Python 3.12 + Tcl/Tk

**状态：** CORE-NOW  
**证据：** `pyproject.toml` 要求 Python `>=3.12`；Environment Doctor 当前 Windows baseline 也检查运行 Python >=3.12；产品壳层是 `tkinter` / `ttk`。

Packaging 要求：

- frozen app 自带 private Python runtime；
- Tcl/Tk DLL/data 正确被 bundler 收集；
- 普通用户不安装 Python；
- 100/125/150% scaling smoke；
- 中文 IME/Unicode path smoke。

## Python stdlib

当前大量稳定基础直接使用 stdlib：

- `sqlite3` — project persistence；
- `urllib` — DeepSeek/Gemini 等 HTTP adapter；
- `json/base64/hashlib/pathlib/tempfile/subprocess` 等；
- `wave` — 当前 deterministic BeatMap baseline；
- `tkinter` — GUI。

**价值：** 当前 Provider adapters 并不需要 vendor SDK 才能运行，Provider-neutral 改造不必引入大型 SDK 框架。

---

# 3. FFmpeg / ffprobe

**状态：** CORE-NOW + CORE-GATE-INTEGRATION  
**用途：**

- media probe；
- frame extraction；
- render；
- audio decode/mix；
- subtitle execution；
- 部分 preview/runtime 辅助。

当前 Environment Doctor 通过 PATH/locator 找到 `ffmpeg` / `ffprobe` 并实际执行 `-version`。

Packaging 必须从“环境 PATH”迁成 product-approved bundled/runtime locator。

## Release hard gate

ADR-001 已明确：

- exact version；
- build configuration；
- external libraries；
- hashes；
- reproducible build recipe/source provenance；
- notices；
- LGPL/GPL/codec/legal review。

**禁止：** 从未知下载站拿一个能跑的 `ffmpeg.exe` 直接塞进安装包。

---

# 4. TransNetV2 shot detection

**状态：** CORE-NOW  
**当前 reviewed runtime path：** `transnetv2-pytorch==1.0.5`  
**代码模块：** `media/shot_detection/transnet_runtime.py`

代码运行时动态导入：

- `numpy`；
- `torch`；
- `transnetv2_pytorch`。

默认 weights：

`transnetv2-pytorch-weights.pth`

由 package-owned path 自动解析，也允许显式 weights path。

## Packaging 风险

- Torch/native DLL 体积；
- CPU-only vs CUDA package 选择；
- weights 许可证/provenance/hash；
- PyInstaller hidden import/native DLL 收集；
- Windows Defender 对大体积 ML bundle 的启动/扫描；
- model load time / RAM。

## 当前发行方向

Stage-A Windows 普通用户 baseline 应优先 **CPU-only**。不要因为开发机有 GPU 就把 CUDA runtime 变成强依赖。

---

# 5. Cloud Reasoning / Vision providers

**状态：** REMOTE / CORE-NOW

## Reasoning / Direction

当前 concrete implementation：DeepSeek HTTP Chat adapter。

`deepseek_chat.py` 使用 Python stdlib `urllib`，不依赖 DeepSeek SDK。

当前产品层仍把 role 锁定到 DeepSeek；这是 `PROVIDER_NEUTRAL_PRODUCT_BINDING_PLAN.md` 要修的商用架构债。

## Vision Understanding

当前 concrete implementations：Gemini / OpenAI。

Gemini adapter同样用 stdlib HTTP/JSON/base64。

## Packaging rule

- 不 bundle API key；
- 不把 vendor credential 写进 app config plaintext；
- ProviderProfile 只存 opaque credential ref；
- app executable 可以 bundle adapter code，secret 仍在 user-scoped protected store；
- live capability test 必须用户主动触发，默认 Doctor 不偷偷烧 quota。

---

# 6. SQLite project database

**状态：** CORE-NOW

使用 Python stdlib sqlite3，无独立 server。

当前稳定资产：

- schema versioning/migrations；
- foreign keys；
- transactional write + rollback；
- project-local `project.sqlite3`。

Packaging 重点不是“带一个 SQLite 安装程序”，而是：

- frozen Python 的 SQLite DLL/module 完整；
- 安装目录只读不影响 project DB；
- UNC/OneDrive/移动盘/杀软 lock 行为要 probe；
- same-project multi-instance 要形成产品语义。

---

# 7. Music / BeatMap / Audio Editorial

**状态：** CORE-GATE-INTEGRATION

当前 deterministic BeatMap baseline `WaveEnergyBeatAnalysisService` 使用 stdlib `wave` + PCM16 RMS/peak logic，本身不引入 librosa/torch 等依赖。

R0.10 MusicSelection / AudioEditorial 已有真实 Product/Human Gate 证据，但普通 Editing ProductFlow 尚未接入，这是当前 gate blocker 的一部分。

Public music acquisition已有 Openverse/Wikimedia provider seams，但普通 Stage-A Gate 可以继续以用户本地/rights-attested music 作为安全 baseline；不要为了打包或“一键”偷偷把公网音乐变成无权利检查的默认素材。

Packaging 后需要：

- FFmpeg audio execution；
- local music path/rights metadata；
- acquisition network feature若启用则独立做 timeout/proxy/cache/license smoke。

---

# 8. Subtitle / Speech Recognition

## Subtitle execution

**状态：** CORE-GATE-INTEGRATION

canonical EDL/Renderer 已有 structured subtitle cue + ASS execution路径。完整普通 ProductFlow 尚需接入 Stage-A subtitle expression floor。

## faster-whisper

**状态：** OPTIONAL/ADVANCED → 可能成为 Stage-A subtitle/speech source，需在 integration design 中明确  
**代码要求：** `faster-whisper==1.2.1`  
**默认模型：** `Systran/faster-whisper-base`  
**固定 revision：** `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`  
**默认 device/compute：** `cpu` / `int8`  
**默认：** `local_files_only=True`

代码明确不允许缺模型时悄悄在线下载。

Packaging 未决：

- CTranslate2/native DLL closure；
- model weights size/license/hash；
- 是否第一个安装包默认包含；
- CPU benchmark；
- 如果不包含，component installation UX。

在 Stage-A integration repair 中先回答：自动 Subtitle 是否必须依赖 ASR，还是已有 speech evidence/用户无对白样本可以形成合法 baseline。不要在未决定产品语义前把 Whisper 无条件塞进发行包。

---

# 9. Silero VAD

**状态：** OPTIONAL/ADVANCED

代码固定证据：

- Silero VAD version：`6.2.1`；
- upstream commit：`7e30209a3e901f9842f81b225f3e93d8199902b1`；
- ONNX model repo path：`src/silero_vad/data/silero_vad.onnx`；
- recorded Git blob SHA：`80c5592ef1f4c9ede3e357bbd02eb863358a6a9d`；
- runtime：`numpy` + `onnxruntime` major 1；
- audio decode：FFmpeg。

不要把 torch-based silero package 与当前轻量 ONNX adapter混为同一个分发方案。

Packaging 需要 model file hash/license/runtime DLL probe。

---

# 10. Sentence Transformers / multilingual E5

**状态：** OPTIONAL/ADVANCED

代码 adapter 对本地 sentence-transformers runtime/version/model有显式约束；历史 R0.8/R0.9 用于 hybrid semantic retrieval 证据。

当前 ordinary ProductFlow 不能因为 Packaging 简化就宣称“已经完全不需要”，也不能在没有 gate-path dependency audit 前默认塞进 installer。

后续 integration dependency closure 要回答：

- ordinary Stage-A Resolver 是否必须启用 dense retrieval；
- 若 lexical/VisualUnderstanding path 是当前最小 gate baseline，advanced dense retrieval是否做 optional component；
- model weights/license/size/offline behavior。

---

# 11. Spatial / MediaPipe recovery

**状态：** CORE-GATE-INTEGRATION（base spatial semantics） + OPTIONAL/ADVANCED（某 recovery provider）

R0.11 SpatialComposer / ReframeDecision 是 Stage-A integration 要复用的已验证能力。

但 MediaPipe recovery candidate 的 external EfficientDet Lite0 model仍有：

`RELEASE_LICENSE_PENDING`

因此：

- Spatial capability ≠ 必须 bundle 该 recovery model；
- 第一个发行 probe 应能在该 optional component 缺失时保持明确 baseline/fallback；
- license 未闭环前不进入默认商业 bundle。

---

# 12. Preview runtime

**状态：** OPTIONAL/PRODUCT UX — release choice尚未冻结

Environment Doctor 当前专门识别 approved private GStreamer runtime；历史还有 VLC/libmpv 等 benchmark/候选。

Packaging 规则：

- 不把多个大型 preview runtime 全打进第一个 bundle；
- 选择一个正式 production route 后记录 exact build/plugin set/license；
- preview failure 不得破坏 canonical render output；
- frozen-app mode重跑 runtime load probe。

---

# 13. UI framework依赖

**当前：** stdlib Tk/Ttk。  
**建议：** first package probe继续保持，不新增 ttkbootstrap/CustomTkinter runtime。

原因不是这些库“不好”，而是当前 stock ttk 已足以实现 design tokens / semantic style / hierarchy，而新增 UI 库会同时扩大：

- dependency closure；
- theme/font/data-file manifest；
- frozen resource path；
- DPI regressions；
- license/upgrade surface。

等现有 ProductFlow gate + packaging seam稳定后，再用 Human Gate 判断是否值得迁移。

---

# 14. 第一个 Windows `onedir` dependency closure 建议

在当前 gate repair完成后，第一个可执行 packaging probe建议只追求**完整普通用户主路径**，而不是把研究阶段所有 optional provider一次塞进去。

候选最小集合：

```text
Python 3.12 private runtime + Tcl/Tk
video-editing-agent package
FFmpeg / ffprobe approved build
TransNetV2 reviewed CPU runtime + reviewed weights
stdlib SQLite/HTTPS
current configured cloud provider adapters
Stage-A integrated Music/Audio/Spatial/Subtitle/Graphics/transition execution dependencies
licenses/notices/version manifest
```

然后根据实际 Gate path补入必须的 speech/embedding/spatial recovery component。

**不要在 dependency audit 完成前把上面这段当作最终 release BOM。**

---

# 15. Fresh-machine dependency smoke矩阵

第一个安装/onedir artifact至少做：

| Case | Expected |
|---|---|
| 无 Python | App启动 |
| 无 uv | App启动 |
| PATH无 ffmpeg | bundled locator仍找到 approved ffmpeg/ffprobe |
| 无开发 repo | App启动并能建新 project |
| 中文 Windows 用户名/路径 | 打开/写入/渲染正常 |
| 125%/150% DPI | UI不裁切 |
| TransNet weights缺失 | Doctor清楚失败，不隐式下载 |
| Provider secret缺失 | 设置面提示，不崩溃 |
| Provider 429 | 显式 quota/wait UX，不换厂 |
| optional recovery model缺失 | 明确 capability降级，不阻断无关路径 |
| output已存在 | 产品层显式确认/另存，不静默覆盖 |
| Review non-PASS | candidate不发布到 final path |

---

# 16. 下一步

1. 当前本地 UX candidate先完整 gate + commit/rebase/push；
2. 完成 Stage-A Editing integration/publication repair；
3. 由实际 ordinary gate path生成**最终 mandatory runtime list**；
4. 再建立 pinned PyInstaller spec / resource locator / release manifest；
5. Windows clean VM做 `onedir` probe；
6. 只有 probe + license gate通过后再选择 installer/onefile/update技术。
