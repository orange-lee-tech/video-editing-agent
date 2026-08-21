# Windows Desktop Packaging Readiness

**状态：** PREPARATION ACTIVE — package not yet release-approved  
**更新：** 2026-08-22  
**目标：** 从“开发机上 `uv run ...` 能启动”演进到“普通 Windows 用户无需安装 Python/uv/仓库即可启动、诊断和运行”。  
**当前 Work Order：** `R0.12-STAGE-A-FINAL-CLOSURE-002` / Wave D（在 Project Workspace + UX consolidation 之后）

---

# 1. 当前判断

**现在仍不能宣布可发布正式安装包。**

这不是 Tkinter 能不能被 PyInstaller 打包的问题，而是完整普通用户路径还需要一个明确、可追溯、可替换的 runtime/resource closure。

当前 first-proof 目标保持：

> **Windows `onedir` Engineering Probe first；稳定后再比较 `onefile` / installer / MSIX。**

`onedir` 更适合第一步，因为 FFmpeg、模型、Tcl/Tk、NOTICE、native DLL、resource locator 和 license manifest 都更容易检查与诊断。

---

# 2. Packaging 前置门：先完成 Project Workspace + UX consolidation

Packaging 不应冻结当前仍偏开发型的路径/交互。

下一波规范：

`docs/operations/STAGE_A_WORKSPACE_UX_CONSOLIDATION.md`

Packaging 开工前至少要稳定：

- 一个 top-level `Project Workspace` 供 Planning/Editing 共用；
- project-specific cache/work/autosave/undo-redo/log/output 归位；
- 默认输出路径语义；
- global profile / project-local state 的边界；
- 主窗口配置入口；
- canonical brand resource 来源。

这不是“先美化再打包”，而是在安装包形成前先确定**哪些数据可写、写到哪里、哪些资源属于程序**。

---

# 3. 当前必须闭环的 runtime/component

## 3.1 Python 3.12 + Tcl/Tk

**CORE-NOW**

- frozen app 自带 private Python runtime；
- Tk/Tcl DLL/data 完整；
- 普通用户不安装 Python；
- 中文路径/IME/DPI smoke。

## 3.2 FFmpeg / ffprobe

**CORE-NOW**

用途已包括 media probe、frame extraction、render、audio mix、subtitle execution 等。

PR #13 加入的 repository-local `.tools/ffmpeg-8.1/...` locator 只是**开发 fallback**，不是 packaging contract。

正式 bundle 必须由独立 resource/runtime locator 找到 approved component，而不是依赖：

- PATH；
- repo root；
- `.tools`；
- `Path(__file__).parents[...]` 的开发目录假设。

Release hard gate继续遵守 ADR-001：exact version/build config/hash/source provenance/notices/license review。

## 3.3 TransNetV2 CPU runtime + reviewed weights

**CORE-NOW**

当前 reviewed runtime path：`transnetv2-pytorch==1.0.5`。

Packaging 要解决：

- CPU-only dependency closure；
- Torch/native DLL；
- weights provenance/hash/license；
- frozen hidden imports；
- clean-machine model-load smoke。

不要把 CUDA 变成普通用户 hard dependency。

## 3.4 Speech runtime / basic trusted subtitles

**RETAINED 1.0 GATE**

`pyproject.toml` 已有 pinned optional extra：

`speech-runtime = faster-whisper==1.2.1`

Stage-A 已证明：

- no-speech 不应因 ASR 缺失而失败；
- grounded speech + required subtitles + speech capability unavailable 必须准确 fail closed。

最终 Packaging 前必须明确二选一的正式 component strategy：

1. 第一个 1.0 bundle 默认包含批准的 speech runtime + pinned local model；或
2. speech component 是受控可安装组件，但 ordinary Doctor/UX 能明确安装状态且最终 single-speaker Human Gate 在目标发行配置上 PASS。

不能继续依赖开发机“刚好装过”。

## 3.5 Cloud provider adapters

**REMOTE / CORE-NOW**

Adapter code可 bundle；API key不可 bundle。

- DeepSeek reasoning/direction；
- Gemini/OpenAI image-frame understanding；
- stdlib HTTP 为主，不要求 vendor SDK。

Remote reference URL/video-native observation已延后至 2.0，不是 first package dependency。

## 3.6 Public music

**CORE-NOW NETWORK CAPABILITY**

Ordinary Editing 已真实通过 rights-safe public BGM Human Gate。

Packaging 需保留：

- Openverse/Wikimedia provider/acquisition code；
- timeout/proxy/network diagnostics；
- rights verification/provenance；
- fail-closed behavior。

不要把音乐素材静态塞进安装包来规避网络/rights 逻辑。

---

# 4. 明确不应无条件塞进 first bundle

## MediaPipe recovery / EfficientDet Lite0

`RELEASE_LICENSE_PENDING`。

在 license 未闭环前：

- 不默认 bundle；
- 不成为普通路径 hard dependency；
- optional capability缺失时必须明确降级。

## Advanced VAD / embeddings / recovery providers

Silero VAD、multilingual E5 等历史上有真实能力证据，但 first release 是否 mandatory 应由**当前 ordinary Stage-A path dependency audit**决定，而不是“仓库里有就打进去”。

## Preview runtime

GStreamer/VLC/libmpv 等历史候选不能全塞进 first bundle。

若 Stage-A ordinary UI不依赖 external preview runtime完成核心结果，则先保持非 hard dependency；未来选定 production preview route 后再做 exact build/plugin/license closure。

---

# 5. Distribution layout 与 Project Workspace 必须分开

建议 first onedir 语义：

```text
VideoEditingAgent/
├─ VideoEditingAgent.exe
├─ runtime/             # bundler/private Python/Tk/native runtime
├─ tools/               # approved FFmpeg/ffprobe etc.
├─ models/              # only redistribution-approved bundled models
├─ resources/           # canonical icon/UI resources
├─ licenses/
└─ version.json
```

安装目录默认只读。

用户项目不放这里。

---

# 6. Writable-data ownership

## Project Workspace — project-specific

用户在主界面第一步选择/打开的 Project Workspace 应成为一个视频工作的 project-local writable root。

逻辑上允许包含：

```text
<Project Workspace>/
├─ project.sqlite3
├─ artifacts/
├─ cache/
├─ work/                # drafts/autosave/bounded undo-redo/session scratch
├─ logs/
├─ provider_audio/
└─ outputs/
   ├─ preview/
   └─ final/
```

不要为了目录好看而复制 canonical Domain 数据；现有 revisioned SQLite/artifact ownership继续有效。

## Documents — user-level reusable config

例如现有：

`%USERPROFILE%\Documents\Video Editing Agent\Profiles`

API profile仍只保存 non-secret metadata / protected credential reference。

## LocalAppData — machine/app-level state

只放不属于单一 project 的程序管理数据，例如：

- component metadata；
- updater state；
- crash marker；
- machine cache；
- sanitized global diagnostics。

项目-specific工作缓存不要无理由散落回 LocalAppData。

---

# 7. Secret 与封装

Packaging 后继续保持：

- API key 不写 executable旁 TXT/JSON；
- profile 不保存 plaintext key；
- secret 使用 user-scoped Windows protection；
- visible log/export/crash report不打印 key；
- 删除 profile 时 protected credential lifecycle正常；
- upgrade 后旧 profile可读或有明确迁移。

必须测试同一 Windows user round trip，并确认另一 Windows user不能直接复用受保护密钥。

---

# 8. Thin desktop bootstrap

正式 bundle应有极薄 desktop bootstrap，只负责：

```text
frozen/development mode detection
→ resource locator
→ writable-root/user-profile locator
→ logging/crash boundary
→ lightweight capability/Doctor startup
→ ordinary product shell
```

Bootstrap/PyInstaller spec不得知道 Resolver/EDL/editorial business rules。

CLI 与 desktop共用 product composition，不做第二套应用架构。

---

# 9. Resource / runtime locator

Packaging Wave必须建立一个清晰 owner，区分：

- development resource；
- frozen install resource；
- project writable data；
- user profile data；
- optional externally installed component。

图标、模型、FFmpeg、licenses/templates都通过该 owner解析。

禁止在普通业务代码继续扩散：

- repo-relative `.tools` assumptions；
- current-working-directory assumptions；
- machine-specific absolute paths。

---

# 10. First onedir Engineering Probe

## Build

要求：

- Windows x64构建；
- exact pinned bundler version；
- checked-in deterministic spec/config；
- `--onedir` + windowed desktop entry；
- build/release manifest；
- no real API secrets；
- package artifact不从 `.private`/`.tools`/`.venv`/developer cache“整目录复制”。

`.tools` 可以作为开发 evidence/source locator，但正式 component必须通过明确 packaging manifest进入 bundle。

## Clean-machine-ish smoke

目标环境不安装：

- Python；
- uv；
- repository checkout。

至少验证：

1. EXE双击启动；
2. Splash/main window；
3. 中文用户名/路径；
4. Project Workspace创建/打开；
5. project-specific writable data不进入 install dir；
6. Profiles + DPAPI round trip；
7. Doctor找到 bundled FFmpeg/ffprobe；
8. TransNet CPU runtime + reviewed weights load；
9. speech component状态准确可诊断；
10. 本地 MP4 ingest/shot-detection smoke；
11. fixture provider完整机械 path；
12. 正常退出无残留 worker；
13. 删除/卸载 bundle不删除用户 Projects/Profiles。

真实付费/有额度的 API Product Probe另行显式执行，不在 installer smoke中偷偷消耗。

---

# 11. Release manifest

每个候选 release至少可追溯：

```text
app version / git SHA
Python runtime
bundler version
FFmpeg/ffprobe version + config + SHA256
TransNet runtime + weights revision/hash/license
speech runtime + model/component status
optional models/components + license state
canonical icon/resource revision
third-party notices
build date / build profile
```

---

# 12. CI / release sequence

建议：

```text
normal Quality Gate
→ Windows onedir build
→ static package inspection
→ artifact upload
→ clean-machine-ish smoke
→ Product/Human Gate
→ manual release approval
```

不要自动发布未签名、未 license-approved、未 Product Gate 的 executable。

---

# 13. Installer / onefile

只有 `onedir` dependency/resource/writable-data closure稳定后，再比较：

- Inno Setup / WiX；
- MSIX；
- onefile；
- signing/SmartScreen；
- update/rollback。

“只有一个 exe”不是产品质量指标。

---

# 14. 当前行动顺序

- [x] repository attention/document governance；
- [x] ordinary remote-reference URL从 1.0 隐藏并明确 2.0 home；
- [ ] Project Workspace + UX consolidation；
- [ ] 从真实 ordinary 1.0 path生成 mandatory/optional runtime BOM；
- [ ] thin desktop bootstrap + resource/runtime locator；
- [ ] pin first bundler + checked-in onedir spec；
- [ ] package build manifest/license manifest；
- [ ] Windows clean-machine-ish probe；
- [ ] retained Planning/Editing/speech Product/Human Gate；
- [ ] 再决定 installer/onefile/update route。

Stage-A 不能因为生成了一个 EXE 就自动变成 100%。
