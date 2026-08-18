# 桌面产品 UI / 工程参考审查 — 2026-08-19

**状态：** RESEARCH NOTE — non-normative  
**目的：** 研究成熟开源桌面产品/GUI 库中值得吸收的交互与工程做法，用来改善本项目的“产品门面”，但不把第三方 UI/框架变成 Domain authority。  
**结论先行：** Stage A 不迁 UI 框架；优先把优秀项目的**信息层级、语义样式、状态反馈、DPI/打包意识**吸收到现有 `tkinter.ttk` 壳层。

---

# 1. 研究对象与来源

全部优先使用项目官方仓库/官方文档：

## Python/Tk 体系

- Python `tkinter.ttk` 官方文档：
  https://docs.python.org/3/library/tkinter.ttk.html
- ttkbootstrap 官方仓库：
  https://github.com/israel-dryer/ttkbootstrap
- ttkbootstrap 官方文档：
  https://ttkbootstrap.readthedocs.io/en/latest/
- CustomTkinter 官方仓库：
  https://github.com/TomSchimansky/CustomTkinter
- CustomTkinter HighDPI/Scaling：
  https://github.com/TomSchimansky/CustomTkinter/wiki/Scaling
- CustomTkinter Packaging：
  https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging

## 视频桌面产品

- Kdenlive 官方 UI 手册：
  https://docs.kdenlive.org/en/user_interface.html
- Kdenlive Project Bin / asset management：
  https://docs.kdenlive.org/en/project_and_asset_management/project_bin/project_bin_use.html
- Kdenlive Monitor：
  https://docs.kdenlive.org/en/user_interface/monitors.html
- LosslessCut 官方仓库/README：
  https://github.com/mifi/lossless-cut

这些项目的许可证、技术栈、产品目标各不相同；本研究只吸收一般机制和设计思想，不复制图标、品牌视觉、未审计源码或产品布局。

---

# 2. `ttk` 本身其实已经支持“行为与外观分离”

Python 官方 ttk 的核心价值不是“默认 Windows 灰色控件”，而是 themed widget + Style 体系。

本项目当前可以在**不换框架**的情况下抽出：

```text
ThemeTokens
  ↓
ttk.Style
  ↓
semantic widget styles
  ├─ Primary.TButton
  ├─ Secondary.TButton
  ├─ Danger.TButton
  ├─ Section.TLabelframe
  ├─ Status.TLabel
  └─ Muted.TLabel
```

这比在每个 `Button(...)` 中散落颜色/字体/spacing 更可维护，也更适合未来替换 UI adapter。

**吸收：** Style/theme seam。  
**不吸收：** “所有原生控件都必须变成自绘 Canvas”。

---

# 3. ttkbootstrap：最值得学的是 semantic styling，不是 Bootstrap 外观

官方仓库展示的一个重要思想是：控件描述意图，例如：

```text
primary
success
info
warning
danger
outline
```

而不是业务代码自己选择 RGB。

对本项目的翻译：

```text
生成拍摄方案 / 开始自动剪辑 → Primary
选择文件 / 导出 / 设置       → Secondary
删除 Profile                 → Danger
任务成功                     → Success status
Provider wait                → Warning status
失败                         → Error/Danger status
```

这能直接解决当前截图里“所有按钮长得差不多重要”的问题。

ttkbootstrap 还把主题和 semantic colors 组织成稳定层，这说明我们完全可以先在 stock ttk 上做一个小型本地实现，而不必立即引入依赖。

**吸收：** semantic token / visual hierarchy。  
**暂不引入：** ttkbootstrap runtime dependency。

原因：当前 Stage-A ProductFlow integration、Packaging closure 比换主题库更重要；额外依赖会增加冻结打包面。

---

# 4. CustomTkinter：最值得学的是 DPI/scaling 与统一控件几何

CustomTkinter 官方实现/文档把：

- appearance mode；
- widget scaling；
- window scaling；
- font scaling；
- theme manager；
- drawing engine

当作框架一级问题。

这提醒我们：Windows 商用桌面 UI 不能只在开发机 100% scaling 下“看着没问题”。

本项目下一轮 UI Human Smoke 至少要包含：

- 100%；
- 125%；
- 150%；
- 1366×768；
- 当前用户高分辨率屏幕；
- 中文/English。

同时 CustomTkinter 的 Packaging 文档展示了一个现实代价：主题/字体等 data files 会直接扩大 PyInstaller packaging/resource 处理。

**吸收：** DPI/scaling 是产品质量，而不是“以后再说”。  
**避免：** 为了圆角/暗色主题，现在立刻引入一套需要额外 data-file packaging 的 UI framework。

---

# 5. Kdenlive：借鉴“工作区 + 状态栏 + 素材心智模型”，不复制 NLE

Kdenlive 官方 UI 把主界面明确拆成：

- Workspace；
- Menu Bar；
- Toolbars；
- Status Bar。

它还把源素材集中在 Project Bin，把 Clip Monitor 与 Project Monitor 区分。

我们的产品并不需要复制 Timeline/Monitor/Effect Stack，因为目标是“一键 AI 导演/剪辑”，不是让普通用户变成 NLE 操作员。

真正值得借鉴的是：

## 5.1 Workspace 有清楚的任务语义

本项目：

```text
Planning Workspace
Editing Workspace
```

而不是十几个等权 Tab。

## 5.2 素材应该被当成一个“集合”，而不是一串路径文本

Kdenlive Project Bin 强调项目素材集合。

本项目可以把：

`C:\a.mp4; C:\b.mp4; C:\c.mp4; ...`

变成：

```text
素材
已选择 7 个视频
1.8 GB
[查看文件] [重新选择]
```

但 exact selected paths 仍保存在 controller state，不自动扫描目录。

## 5.3 Status Bar 是长任务的低噪声常驻反馈

本项目很适合：

```text
理解素材  |  预计 00:42 完成  |  视觉服务等待 18s
```

这比把所有进度信息塞进大 Text 输出区更产品化。

---

# 6. LosslessCut：借鉴“围绕用户动作优化”，不要把 FFmpeg 暴露给用户

LosslessCut 的产品定位非常集中：快速完成视频/音频相关操作，FFmpeg 在背后承担 grunt work。

它给本项目的启发不是“也做 lossless cut”，而是：

> 后端再复杂，普通用户看到的仍应该是目标、素材、动作和结果。

本项目当前 UI 仍有不少“内部工程结构投影到用户面”的痕迹，例如 API provider、长 status log、路径字符串。

下一步 UI 应优先回答：

1. 我正在做拍摄规划还是自动剪辑？
2. 我选了什么素材？
3. 系统现在在哪一步？
4. 成功以后结果在哪里？
5. 失败以后我能做什么？

而不是展示内部模块数量。

---

# 7. 参考项目带来的功能排布原则

## 7.1 一个页面一个主 CTA

Planning：`生成拍摄方案`  
Editing：`开始自动剪辑`

其他动作降级为 Secondary / menu。

## 7.2 把“状态”从“结果”中拆开

```text
Status/Run
  stage / ETA / wait / diagnostic

Result
  ScriptPlan / ShootingPlan / final MP4 / Review outcome
```

不要让用户在几百行日志里找最终结果。

## 7.3 把素材输入从 Entry 升级为 summary component

- count；
- optional local size；
- view list；
- replace selection；
- no automatic unrelated scan。

## 7.4 设置以 capability 为一级信息

```text
思考与编导
视觉理解
```

Provider/Model 是其配置，不是产品角色。

## 7.5 技术细节分层

普通用户：

`视觉理解服务当前达到配额限制，请稍后重试。`

展开技术详情：

`provider/model/status/retry_after/quota_id`

不要把 Python exception class 当标题。

---

# 8. 明确不借鉴的东西

## 不复制成熟 NLE 的复杂 Timeline

Stage A 用户不需要多轨手工编辑器。

## 不引入“所有东西都能自定义”的 workspace docking

这会让产品重新变成专业工具，而不是自动化工具。

## 不复制第三方品牌视觉/图标

只学习 hierarchy/rhythm/mechanism。

## 不因为 UI 库漂亮就换框架

UI framework 迁移必须由：

- 明确产品能力缺口；
- packaging/maintainability evidence；
- Human Gate

驱动，而不是截图观感驱动。

## 不让 UI 直接拥有 Domain

无论未来 Tk、Qt、WebView、Tauri，frontend 都只映射 ProductFlow/application state。

---

# 9. 对当前截图的直接改造草图

## 现在

```text
菜单
[拍摄规划][自动剪辑]
项目目录 [........................................]
视频标题 [........................................]
视频目标 [........................................]
...
正在估算...
                                      [开始]
[导出]
--------------------------------------------------
巨大空白 Text
```

## 建议

```text
┌ 视频剪辑智能体 ─ 当前项目 ───────── 2/2能力已配置  设置 ┐
│                                                          │
│ [拍摄规划] [自动剪辑]                                    │
│                                                          │
│ 创作目标                                                 │
│ 标题        [通勤小水瓶_______________________]           │
│ 目标        [告诉上班族它方便携带_____________]           │
│ 受众        [上班族____]    平台 [抖音____]               │
│                                                          │
│ 商业事实与限制                                           │
│ 已确认事实  [容量350mL_________________________]           │
│             只填写已经确认的事实，留空也可以              │
│                                                          │
│ 参考与拍摄条件                                           │
│ [参考 URL] [选择本地参考]  手机 / 自然光                 │
│                                                          │
│                                   [生成拍摄方案]          │
│ ● 准备就绪 · 正在估算                                   │
│                                                          │
│ 结果                                          [复制][导出] │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ 尚未生成。完成后这里显示 Script/Shooting Plan。      │ │
│ └──────────────────────────────────────────────────────┘ │
│ [运行记录 ▾]                                            │
└──────────────────────────────────────────────────────────┘
```

Editing 同构，但“素材”变成 summary card，完成后 Result 首先显示 final MP4 + Review outcome + `打开输出目录`。

---

# 10. 最终研究结论

当前最优路线不是“找一个漂亮 UI 库重写”，而是：

1. 保留 stock Tk/ttk 与现有 Windows product adapter；
2. 把 ttkbootstrap 的 semantic styling 思想做成本地 design tokens；
3. 把 CustomTkinter 的 DPI/scaling 意识纳入 Human Smoke / packaging；
4. 吸收 Kdenlive 的 workspace / asset collection / status-bar 心智模型，但拒绝 NLE 复杂度；
5. 吸收 LosslessCut 的“目标动作优先、FFmpeg 隐于后台”产品表达；
6. 等 Stage-A Editing integration 与 Windows packaging seam 稳定后，再用证据判断是否需要迁 Qt/WebView/Tauri 等新 frontend adapter。

这条路线既能明显改善门面，又不会为了装修拆掉已经验证过的生产关系。
