# Windows Desktop Packaging Readiness

**状态：** RELEASE DELIVERY ACTIVE — guided Setup.exe not yet Human-approved  
**更新日期：** 2026-08-26  
**目标：** 从已完成的 Windows onedir/runtime 工程证明，收口到普通用户可安装、可修复、可卸载的 1.0 `Setup.exe`。  
**当前 Work Order：** `R0.12-STAGE-A-FINAL-CLOSURE-002`

---

# 1. 当前判断

**运行时/onedir 工程基础已经证明，当前真正未闭环的是普通用户安装交付。**

已完成的工程事实包括：

- pinned CPython 3.12.13 + Tcl/Tk；
- approved FFmpeg/ffprobe；
- TransNetV2 CPU runtime + reviewed weights；
- previously proven faster-whisper speech runtime/model engineering payload；
- runtime manifest / NOTICE / static inspection / Doctor；
- packaged runtime probes；
- GUI launcher and external Project Workspace smoke；
- heavy Windows packaging workflow改为显式手动触发，不再作为每次修复的迭代运输方式。

旧的 ~769 MB 压缩 / ~1.88 GB 解压 onedir 是 engineering staging，不是普通 1.0 用户交付形态。

Product Owner 于 2026-08-26 明确将高级人声连续性/多语言旁白线推迟至 2.0，因此最终 1.0 默认安装包不应继续为了历史工程探针而携带 speech runtime/model。

---

# 2. Packaging 前最后 source freeze

在生成最终候选 staging tree 前，只允许完成与 1.0 直接相关的最后一组源码收口：

- Planning 输出质量提升且不削弱事实审查；
- 中文/英文真实素材已证明的 visual-first Editing 修复进入 accepted SHA；
- 配置导入改为 Form/Director 与 API/Provider 的直接独立动作；
- 隐藏 2.0 speech/translated-subtitle/TTS 与 remote-reference 未完成入口；
- provider-directed 429/RetryInfo 等等待行为做 bounded ordinary-user recovery；
- 完整 Quality Gate + CI。

不得以此为理由重新开启 2.0 音频分离、异语旁白或富 NLE 波次。

---

# 3. 1.0 runtime/component ownership

## 3.1 Core App / Planning

**CORE / REQUIRED**

- frozen application code；
- private CPython 3.12.13；
- Tcl/Tk；
- GUI/resources；
- Workspace/Profile/DPAPI integration；
- DeepSeek / Gemini / OpenAI adapter code（credentials never bundled）。

普通 Planning-only 用户不应被迫安装完整 Editing runtime。

## 3.2 Media Runtime — FFmpeg / ffprobe

**EDITING + LOCAL REFERENCE COMPONENT**

用途包括：

- probe/decode/frame extraction；
- render；
- music/basic audio execution；
- local-reference analysis path。

Release hard gate继续遵守 ADR-001：exact version/build config/hash/source provenance/notices/license review。

不修改 arbitrary system PATH，不依赖系统开发环境。

## 3.3 Scene Detection Runtime — TransNetV2 CPU + reviewed weights

**EDITING + LOCAL REFERENCE COMPONENT**

- `transnetv2-pytorch==1.0.5`；
- CPU Torch runtime；
- reviewed package-owned weights；
- no CUDA hard dependency。

## 3.4 Speech Runtime / model

**DEFERRED DEFAULT PAYLOAD — 2.0 ADVANCED AUDIO**

此前已经完成并保留以下工程证据：

- `faster-whisper==1.2.1`；
- CTranslate2/PyAV；
- pinned `Systran/faster-whisper-base` local model；
- CPU/int8/local-files-only runtime proof；
- approved LGPL FFmpeg DLL binding for PyAV。

这些工作不作废，但在 Product Owner 2026-08-26 的版本边界下，它们不再属于默认 1.0 installer payload，也不再是 Stage-A 100% blocker。

保留 lockfiles/provenance/seams，为 2.0 dual-track speech / translation / TTS 使用。1.0 不展示未完成 speech/translation/TTS 控件。

## 3.5 Cloud provider adapters

**REMOTE CODE / 1.0 REQUIRED WHERE CAPABILITY USED**

Adapter code可 bundle；API key不可 bundle。

- DeepSeek reasoning/direction；
- Gemini/OpenAI visual understanding；
- ordinary GUI owns provider configuration；
- retryable 429/408/5xx应有 bounded wait/retry UX；
- no silent provider fallback。

## 3.6 Public music

**1.0 NETWORK CAPABILITY**

保留：

- discovery/acquisition；
- rights verification/provenance；
- bounded fallback；
- timeout/proxy/network diagnostics。

不要静态塞一堆音乐进 installer 来绕过 rights contract。

---

# 4. 1.0 安装形态

首选候选：**Inno Setup 7.1**，前提是最终商业许可策略可接受。

Plan B：**NSIS Modern UI 2**。

Velopack 仅在后续明确选择 whole install/update/delta stack 时作为竞争方案，不与 Inno 默认叠加。WiX/Burn 仅在 prerequisite chaining 确实需要时考虑。

建议的 1.0 installer component semantics：

```text
VideoEditingAgent-Setup.exe
├─ Core App / Planning                     [required]
└─ Media Analysis + Automatic Editing      [optional, recommended]
   ├─ FFmpeg / ffprobe
   └─ TransNetV2 CPU + weights
```

高级 Speech Runtime 不进入默认 1.0 component tree。

Planning-only 用户可以只装 Core；需要本地参考视频分析或自动剪辑的用户安装 Editing component。

---

# 5. Setup.exe ordinary-user contract

Installer/maintenance flow至少需要：

- Windows 安装向导；
- license/agreement page where applicable；
- 清楚的安装目录；
- desktop shortcut checkbox；
- completion-page launch checkbox；
- same-AppId upgrade/repair path；
- Windows conventional uninstall；
- 对 application-owned component conflict 给出普通语言说明；
- destructive replacement/reconfiguration 前获得用户同意；
- 不任意修改系统 Python / FFmpeg / PATH；
- Project Workspaces、Profiles、original media 均位于 install tree 外，update/repair/uninstall 后保留。

---

# 6. Distribution layout 与 Project Workspace 分离

候选 staging tree 继续使用明确 application-owned layout，例如：

```text
VideoEditingAgent/
├─ VideoEditingAgent.exe
├─ _internal/
│  ├─ private Python/Tk runtime
│  ├─ resources/
│  ├─ licenses/
│  ├─ tools/                  # Editing component
│  └─ runtimes/transnet/      # Editing component
└─ ...
```

安装目录默认只读。

用户 Project Workspace 继续位于用户选择路径，不进入 application install tree。

Reusable Profiles 继续位于 user-level profile location，API secret 由 Windows user-scoped protection 持有。

---

# 7. Installer build chain

最终候选 sequence：

```text
accepted green source SHA
→ prepare only 1.0 required runtime payloads
→ PyInstaller onedir staging tree
→ static manifest/license inspection
→ build Setup.exe with established installer tool
→ install to clean-machine-ish target
→ ordinary launcher/Workspace/API/Planning/Editing smoke
→ upgrade-or-repair test
→ uninstall test
→ verify Projects/Profiles/originals preserved
→ Product/Human Gate
→ release approval
```

真实付费/有额度 API probe保持显式，不在 installer smoke里偷偷消耗。

---

# 8. Release manifest

最终候选至少记录：

```text
app version / git SHA
Python runtime
PyInstaller version
installer tool + version
FFmpeg/ffprobe version + config + SHA256
TransNet runtime + weights revision/hash/license
1.0 installed component set
third-party notices
build date / build profile
```

Speech runtime/model可以记录为 `deferred_not_shipped_1_0`，不应继续作为默认 package closure 条件。

---

# 9. Current action order

- [x] Project Workspace / UX foundation；
- [x] runtime inventory / manifest；
- [x] onedir engineering build foundation；
- [x] FFmpeg / TransNet / speech engineering payload proof；
- [x] heavy package workflow改为 explicit/manual；
- [ ] preserve + accept current focused Planning/Editing repair；
- [ ] final Planning quality + UI isolation + bounded provider wait patch；
- [ ] full Quality Gate + accepted green SHA；
- [ ] remove deferred speech payload from default 1.0 staging spec/manifest；
- [ ] build explicit 1.0 staging tree；
- [ ] build guided `Setup.exe`；
- [ ] install / repair-or-upgrade / uninstall smoke；
- [ ] final ordinary-user Human Gate；
- [ ] Stage-A 100% only when the gate is truthful。

我们现在已经越过“能不能打包”的问题。剩下的是**把 1.0 scope 冻结干净，并完成真正的 Windows 安装产品化**。
