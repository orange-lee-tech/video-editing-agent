# Windows Desktop Packaging Readiness

**状态：** PREPARATION ACTIVE — package not yet release-approved  
**日期：** 2026-08-19  
**目标：** 从“开发机上 `uv run ...` 能启动”演进到“普通 Windows 用户无需安装 Python/uv 即可安装、诊断、运行和卸载”。  
**Roadmap 对应：** R0.14 Environment Doctor + Windows Packaging + Security Reliability。

---

# 1. 当前判断

**现在还不应该宣布已经可以发布正式安装包。**

原因不是 Tkinter 不能封装，而是完整产品还包含：

- Python 3.12 runtime；
- Tk/Tcl runtime；
- FFmpeg / ffprobe；
- TransNetV2 Python runtime + weights；
- optional MediaPipe / model artifact；
- provider adapters；
- SQLite/project schema；
- profiles / Windows protected credentials；
- future preview backend；
- license/notices/build profile。

其中多项运行/分发边界尚未经过 fresh Windows package probe。

因此当前策略：

> **先把可复现的 Windows `onedir` 包作为第一个 packaging Engineering Probe；通过以后再比较 `onefile`、installer/MSIX 等发行形态。**

---

# 2. 为什么先 `onedir`

PyInstaller 官方文档说明：

- 它可以把 Python 应用及依赖打包，使用户无需单独安装 Python；
- Windows bundle 必须在 Windows 上构建，PyInstaller 不是跨平台编译器；
- `--onedir` 是标准 one-folder bundle；
- `--onefile` 运行时涉及额外解包行为；
- data/binary 资源可通过 spec / `--add-data` / `--add-binary` 管理。

官方参考：

- https://pyinstaller.org/en/stable/
- https://pyinstaller.org/en/stable/usage.html

`onedir` 对本项目当前更适合做第一步，因为：

- FFmpeg、模型、NOTICE、Tcl/Tk、optional native runtime 更容易检查；
- 资源缺失时更容易诊断；
- hash / provenance / license manifest 更清楚；
- 不必同时调试 onefile 临时解包、杀毒软件扫描和大体积启动延迟。

**这不是最终 UI/商业发行形式决定。** 它只是最低风险的第一条可分发证明路径。

---

# 3. 当前阻塞项

## P0-1 `pyproject.toml` 没有普通 runtime dependency 闭包

当前项目 `dependencies = []`，真实 Windows launcher 常用：

`uv run --with "transnetv2-pytorch==1.0.5" video-editing-agent launch`

这对开发/Probe 可以接受，对普通用户发行不可接受。

Packaging 必须明确：

- 哪些 Python 包是 mandatory；
- 哪些是 optional component；
- exact versions / hashes；
- model files 从哪里来；
- 是否随包分发；
- 如果不随包分发，首次启动如何安全获取/验证。

## P0-2 FFmpeg distribution gate

ADR-001 已明确：

- exact version；
- configuration；
- external libraries；
- hashes；
- build recipe；
- notices；
- codec/legal review。

**禁止**为了“打包方便”随便从某网站抓一个 ffmpeg.exe 塞进去。

## P0-3 TransNetV2 runtime / weights

目前 shot detection 是产品重要机械能力。

发行前必须记录：

- package exact version；
- model weights exact provenance/hash/license；
- CPU runtime size/startup；
- PyInstaller hidden imports/native deps；
- 在无开发环境机器上的 load smoke。

## P0-4 R0.11 optional recovery model

R0.11 closure 已记录 EfficientDet Lite0 外部模型为：

`RELEASE_LICENSE_PENDING`

在条款未闭环前：

- 不默认 bundle；
- 不把它变成安装包 hard dependency；
- 如果该能力是 optional，package readiness 必须能在它缺失时清楚降级。

## P0-5 Preview backend 仍需最终发行选择

GStreamer / libVLC / approved libmpv 等 candidate 的实际 Windows distribution package/plugin license 需要按最终选择审核。

不要为了 packaging 把多个大型 preview runtime 全塞进去。

---

# 4. 建议的发行目录语义

第一阶段 `onedir` 目标：

```text
VideoEditingAgent/
  VideoEditingAgent.exe
  runtime/              # private Python/Tk/native runtime as bundler requires
  tools/
    ffmpeg.exe
    ffprobe.exe
  models/
    transnetv2/...       # only if redistribution approved
  licenses/
    THIRD_PARTY_NOTICES.txt
    ...
  resources/
    app icon / deterministic UI assets
  version.json
```

**注意：** 这是 distribution layout，不是 Domain/project layout。

安装目录应默认视为只读。

---

# 5. 用户数据位置

不要把可写数据放安装目录。

建议 Windows 用户目录：

## Documents

用户主动管理的：

- Profiles（现有）：`%USERPROFILE%\Documents\Video Editing Agent\Profiles`

## LocalAppData

机器/程序管理的：

- cache；
- timing history；
- sanitized logs；
- component metadata；
- updater state；
- crash marker；
- temporary derived resources。

例如：

`%LOCALAPPDATA%\Video Editing Agent\...`

## 项目目录

只存项目本身的：

- SQLite；
- canonical artifacts；
- derived evidence；
- explicit outputs；

不能把 global secret/profile 塞进 project。

---

# 6. Secret 与封装

Windows packaging 后仍保持：

- API key 不写入 executable旁 TXT/JSON；
- profile 只保存 opaque reference；
- secret 使用 user-scoped Windows protection；
- 日志不打印 key；
- crash report 不包含 key；
- installer/update 不迁移出 plaintext secret。

必须测试：

- 同一 Windows user 可读取；
- 另一 Windows user 不可读取；
- profile 删除时 credential lifecycle 正常；
- 升级版本后已有 profile 仍可读取或提供明确迁移。

---

# 7. Packaging entrypoint

当前 CLI entrypoint 是：

`video_editing_agent.adapters.cli.entrypoint:main`

正式 desktop bundle 应增加一个极薄的 GUI bootstrap entrypoint，例如：

```text
video_editing_agent.adapters.desktop.bootstrap
```

它只负责：

- frozen resource path；
- logging/crash boundary；
- Environment Doctor lightweight startup；
- launch product shell。

不要让 PyInstaller spec 直接知道 Domain/Resolver 细节。

开发 CLI 保留，GUI bootstrap 与 CLI 共用 product composition。

---

# 8. Resource Locator

封装前必须把资源定位从“假设 cwd/repo”迁成明确 helper：

- development mode；
- frozen bundle mode；
- user writable data；
- optional externally installed component。

所有图标/模型/license/templates 通过 resource locator 获取。

不要在业务代码中散落：

`Path(__file__).parents[...]`

或：

`C:\Users\...`

---

# 9. 第一个 Packaging Engineering Probe

## 构建机

Windows 11/10 x64，clean-ish environment。

## Build

第一步只证明：

- PyInstaller exact pinned version；
- `--onedir`；
- `--windowed`；
- deterministic spec checked into repo；
- build manifest/hash output；
- no real API secrets。

## Smoke machine / VM

目标机器**不安装**：

- Python；
- uv；
- repository source tree。

至少验证：

1. EXE 双击启动；
2. Splash/main UI；
3. 中文路径/用户名；
4. Profiles 路径；
5. DPAPI round trip；
6. Doctor 能找到 bundled ffmpeg/ffprobe；
7. TransNet runtime loads；
8. 选择本地 MP4；
9. 不调用云 API 的本地 smoke；
10. 使用 fixture provider 的完整机械 test；
11. 正常退出无残留 worker；
12. uninstall/delete bundle 后用户项目和 Profiles 不被删除。

真实 API Product Probe 另行显式执行，不能在 installer smoke 中偷偷烧额度。

---

# 10. 下一层：Installer

`onedir` Engineering Probe 通过后，再评估：

- Inno Setup / WiX；
- MSIX；
- 其他 Windows installer/update route。

评估维度：

- 安装/卸载；
- code signing；
- Windows SmartScreen；
- per-user vs per-machine；
- auto-update；
- rollback；
- component download；
- notices；
- file association（如果未来需要）。

不要现在就锁 installer 技术。

---

# 11. `onefile` 何时才值得试

只有当：

- onedir 依赖闭包稳定；
- model/native resource loading 全部通过；
- 启动时间可接受；
- 临时解包/杀软行为经过验证；
- update/repair 不因单文件巨大而恶化；

才对 `onefile` 做对照 benchmark。

“只有一个 exe”不是产品质量指标。

---

# 12. Release Manifest

未来每个 release 至少生成：

```text
app version / git SHA
Python runtime version
PyInstaller/Nuitka version
FFmpeg/ffprobe version + config + SHA256
TransNet runtime + weights revision/hash/license
optional model revisions/hashes/licenses
preview backend exact build
third-party notices
build date / build host profile
```

用户不一定需要看全部，但工程上必须能追溯。

---

# 13. CI / Workflow 准备

正式 packaging workflow 建议：

```text
normal Quality Gate
  ↓
Windows package build
  ↓
package static inspection
  ↓
artifact upload
  ↓
Windows package smoke
  ↓
manual/release approval
```

不要让 package workflow 自动发布未签名、未 license-approved 的 executable。

---

# 14. 当前可立即做、但不碰本地未提交 UI 的准备工作

- [x] 记录 packaging readiness 与阻塞项；
- [ ] 盘点 mandatory/optional runtime dependency closure；
- [ ] 新增 `packaging/` 目录规范；
- [ ] 选择并 pin 第一个 PyInstaller 版本；
- [ ] 写 desktop bootstrap/resource locator；
- [ ] 生成 first onedir spec；
- [ ] Windows clean-machine probe；
- [ ] license manifest；
- [ ] 再决定 installer/onefile。

这些工作属于未来 coherent packaging batch；当前 Stage-A Editing Product/Human Gate 不因此被宣布完成。
