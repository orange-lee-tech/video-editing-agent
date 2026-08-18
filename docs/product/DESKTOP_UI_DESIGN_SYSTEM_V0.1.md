# Desktop UI Design System v0.1

**状态：** ACTIVE PRODUCT DESIGN GUIDANCE  
**日期：** 2026-08-19  
**范围：** Windows 普通用户产品壳层（当前 Tk/Ttk launcher 及其后续封装）  
**从属关系：** 本文件不得覆盖 Product Constitution、Architecture Contract、CAP/ADR 或 canonical editing authority。

---

# 1. 为什么现在需要一套 UI 设计系统

当前 Stage-A GUI 已经证明“普通人能打开、能填、能跑”，但真实截图暴露出明显的工程工具感：

- 几乎所有输入行横向铺满整个窗口；
- 标题、输入、帮助、状态、结果之间视觉层级弱；
- placeholder 承担过多“必填/可选 + 示例”说明，导致每一行视觉噪声相似；
- Primary CTA 与导出/设置等 Secondary Action 权重接近；
- 大块结果区在任务前是一整片空白；
- API 设置仍以厂商实现为中心，而不是以用户理解的能力角色为中心；
- 产品已有复杂后端，但门面仍像“内部调试工具”。

UI 美化的目标不是增加装饰，而是：

> **让用户更快理解当前在做什么、下一步点哪里、系统正在做什么、结果在哪里、出了问题怎么处理。**

---

# 2. 技术策略：Stage A 不迁 UI 框架

## 2.1 当前建议

继续使用 Python 标准 `tkinter.ttk` 作为当前稳定壳层，在其上建立本地：

- design tokens；
- `ttk.Style`；
- 布局 helper；
- 可复用 card/section/status/action 组件；
- 图标与 Canvas 微型视觉元素。

理由：Python 官方 ttk 的基本设计就是把控件行为与外观分离，适合在不改变业务行为的情况下重做视觉层级。

官方参考：

- https://docs.python.org/3/library/tkinter.ttk.html

## 2.2 参考但暂不直接引入的项目

### ttkbootstrap

值得学习：

- semantic colors；
- primary / success / info / warning / danger；
- light/dark theme family；
- theme-level 一致性。

参考：

- https://ttkbootstrap.readthedocs.io/en/latest/themes.html
- https://ttkbootstrap.readthedocs.io/en/latest/user-guide/feature-guides/theming.html

当前不直接加入依赖的原因：先验证本地 ttk style 是否足够，不为“换皮”增加新的 runtime/package surface。

### CustomTkinter

值得学习：

- 统一间距/圆角/色板；
- light/dark/system appearance；
- DPI/scaling 意识。

但其官方 Windows packaging 指南需要额外处理主题/字体等 data files，并历史上推荐 PyInstaller `--onedir` 路径。当前 Packaging 尚未闭环，不应仅为视觉好看提前扩大打包复杂度。

参考：

- https://customtkinter.tomschimansky.com/documentation/packaging/

**结论：** 学设计语言，不在 Stage-A gate 中做框架迁移。

---

# 3. 设计关键词

产品视觉应表达：

- **导演台，而不是 IDE**；
- **稳定，而不是炫技**；
- **有 AI，但不做“赛博 AI 发光面板”**；
- **短视频生产工具，而不是传统 NLE 的密集时间线**；
- **高信息效率，而不是堆卡片**。

建议风格：

`Clean Desktop + Editorial Workspace + restrained pixel accent`

像素元素只用于：

- 产品图标；
- Splash；
- 少量状态/分隔装饰；

不把整个产品做成游戏 UI。

---

# 4. Design Tokens

## 4.1 字体

Windows 优先：

- 中文正文：`Microsoft YaHei UI` / 系统默认 UI fallback；
- 英文/数字：`Segoe UI`；
- 等宽技术细节：`Cascadia Mono` / fallback monospace。

原则：

- 不在当前阶段打包第三方字体；
- 避免许可证和字体资源定位额外负担；
- 技术诊断与普通结果在字体上可区分，但不能影响可读性。

## 4.2 字号层级

建议基线：

- App title / major section：18–20 px equivalent；
- Section title：14–16；
- Body / label：12–13；
- Secondary help / meta：10–11；
- 技术详情：10–11 monospace。

不要通过大量粗体制造层级。

## 4.3 间距

统一 4-point rhythm：

`4 / 8 / 12 / 16 / 24 / 32`

优先语义：

- 控件内部：8；
- 同组字段：8–12；
- section：16–24；
- 页面主区域：24–32。

## 4.4 颜色

第一阶段只做 Light Theme。

建议语义 token，而不是把颜色散落在代码中：

- `surface.app`
- `surface.card`
- `surface.input`
- `text.primary`
- `text.secondary`
- `border.subtle`
- `accent.primary`
- `status.success`
- `status.warning`
- `status.error`
- `status.info`

色值由 theme module 统一提供；业务逻辑不得硬编码 RGB。

Dark Theme 可在 token 稳定后追加，不需要现在复制两套布局。

## 4.5 状态不能只靠颜色

所有重要状态同时使用：

- 文字；
- icon/符号；
- 必要时颜色。

例如：

`✓ 已就绪` / `! 需要配置` / `× 运行失败`

避免只用“绿色/红色小圆点”。

---

# 5. 主窗口信息架构

建议从当前“两页大表单 + 大空白结果框”改成明确的五区结构。

```text
┌─────────────────────────────────────────────────────┐
│ Brand / Project     Runtime/API status   Settings   │  Header
├──────────────┬──────────────────────────────────────┤
│ 拍摄规划      │  Workflow title + concise description│
│ 自动剪辑      │                                      │
│              │  [Input sections/cards]               │
│              │                                      │
│              │  [Primary action + runtime status]    │
│              │                                      │
│              │  [Result / Run log]                   │
├──────────────┴──────────────────────────────────────┤
│ Stage · ETA · Provider wait · safe status           │  Status bar
└─────────────────────────────────────────────────────┘
```

如果当前 Tk 布局不适合左侧导航，可继续顶部两个 workflow tabs，但 Header / Content / Status / Result 四层必须清楚。

---

# 6. Header

Header 只保留真正全局的动作：

左侧：

- 像素产品标记；
- `视频剪辑智能体`；
- 当前项目名/未选择项目。

右侧：

- API/能力状态（例如 `2/2 能力已配置`，不是只写 API）；
- `诊断`；
- `设置`；
- 语言。

避免：

- 把一排次要按钮全塞进 Header；
- 显示 model class/error class；
- 用 vendor logo 作为能力状态。

---

# 7. Planning 页面重排

将输入拆成语义 section，而不是十行等权输入。

## 7.1 项目

- 项目目录；
- 视频标题。

## 7.2 创作目标

- 视频目标；
- 目标受众；
- 发布平台；
- 核心信息。

## 7.3 商业事实与限制

- 已确认事实；
- 明确禁止内容/品牌约束（未来已有字段时暴露）；

“已确认事实”旁边应有短 help：

> 只有你已经确认的产品事实才放这里；留空也可以。

不要把完整说明塞在 placeholder 里。

## 7.4 参考

- Reference URL/share text；
- 本地参考视频；
- 已选择 reference 摘要。

## 7.5 拍摄条件

- 设备；
- 拍摄备注/约束。

## 7.6 主行动

页面只保留一个明显 Primary CTA：

`生成拍摄方案`

Secondary：

- 保存配置；
- 清空/新建；
- 导出结果。

---

# 8. Editing 页面重排

## 8.1 项目与成片目标

复用 Brief 字段，但不要视觉上复制一整张 Planning 表单；共同字段使用同一 component/style。

## 8.2 素材

普通 UI 保持单一机制：`素材文件`。

选完后不在 Entry 里展示一整串路径，改成 Summary：

```text
已选择 7 个视频
总大小：1.8 GB（本地可快速计算）
查看文件…
```

如果能够低成本获得 duration，则可以在本地 probe 后显示；不要为了摘要额外调用云 API。

必须保留：

- exact user-selected paths；
- 可查看列表；
- 不自动扫描同目录其他文件。

## 8.3 输出

- MP4 位置；
- 若目标已存在，运行前明确确认覆盖/改名；
- 后续可加入“打开输出目录”。

## 8.4 Combined

当前 `使用本次会话的拍摄规划结果` 应表达为明确的可选 context：

> 使用刚刚生成的 Script/Shooting Plan 帮助编辑

并解释：不勾选也能 Editing-only。

## 8.5 主行动

唯一 Primary CTA：

`开始自动剪辑`

运行中：

- 按钮 disabled；
- 状态栏显示 stage/ETA；
- 真正支持 safe cancel 以后才显示 Cancel。

---

# 9. Result Surface

当前巨大空白 Text 在任务开始前信息价值很低。

建议切成两个概念：

## 9.1 结果

普通人优先看到：

- Planning：ScriptPlan / ShootingPlan 摘要与可导出文本；
- Editing：成片路径、Review 结果、时长、素材数量、关键诊断。

## 9.2 运行记录

折叠/Tab 显示：

- stage transitions；
- provider wait；
- local tool status；
- bounded technical diagnostics。

Primary message 不显示 Python exception class。

结果区常用动作：

- `导出 TXT`；
- `复制结果`；
- `打开输出目录`（Editing 完成后）；
- `查看技术详情`。

只有在真实能力存在时才显示动作。

---

# 10. Status Bar / Runtime Feedback

底部或主 CTA 附近长期存在一个小型 runtime strip：

```text
● 理解素材   |   预计 00:42 完成   |   视觉：Gemini 3.6 Flash
```

Provider 等待时：

```text
! 视觉服务要求等待约 38 秒，任务仍在继续
```

原则：

- 不显示假百分比；
- ETA 可以变化；
- provider/model 只作为次级诊断，不是 workflow 主语；
- 429 最终失败要告诉用户下一步，不让界面像死机。

---

# 11. API / Capability Settings 重构原则

当前“思考指挥 = DeepSeek；视觉理解 = Gemini/OpenAI”的 UI 只适合作为早期实现，不是最终产品结构。

设置页应该首先展示**能力角色**：

## 11.1 Reasoning / Direction

用途：

- Script Planning；
- Shooting Planning；
- proposal review；
- Editing Director。

配置结构：

- Provider Profile；
- Protocol/Adapter；
- Base URL（适用于 compatible/custom provider）；
- Model；
- Credential reference；
- Capability test。

## 11.2 Vision Understanding

用途：

- reference analysis；
- user footage semantic understanding。

配置同样按 provider profile 选择。

## 11.3 未来能力

Speech / Embedding / Music 等如果进入普通用户设置，应沿用同一模式，而不是每个厂商做一块独立 UI。

**硬规则：**

`Capability Role → Provider Binding → Adapter/Protocol → Model`

而不是：

`厂家 → 产品能力`

---

# 12. Buttons / Action Hierarchy

## Primary

每个页面同时最多一个：

- 生成拍摄方案；
- 开始自动剪辑。

## Secondary

- 选择文件；
- 导出；
- 保存/读取 profile；
- 打开目录；
- 诊断。

## Tertiary / Menu

- 删除 profile；
- 技术详情；
- 清空表单；
- 高级设置。

不要让“导出”和“开始自动剪辑”看起来一样重要。

---

# 13. 建议新增的基础效率功能

以下能力可进入普通 UI backlog，但必须有真实实现才能出现：

1. **打开输出目录** — Editing 完成后；
2. **复制结果** — Planning/Editing 文本结果；
3. **最近项目** — 只保存项目路径与非 secret 元数据；
4. **诊断 / Doctor** — 把 Environment Doctor 转成可读 summary；
5. **打开 Profiles 目录**；
6. **输出已存在时确认/自动建议新文件名**；
7. **查看已选素材列表**；
8. **Safe Cancel** — 只有 orchestration/FFmpeg/provider lifecycle 真正支持取消后再暴露；
9. **Retry failed stage** — 只有 artifact/stage resumability 足够明确后实现。

明确不做：

- 没有 adapter 的 `公共素材`；
- 没有 research provider 的 `类似方案`；
- 假装联网搜索的 checkbox；
- “AI 自动优化一切”这类无可检查语义的按钮。

---

# 14. 窗口与可访问性

必须验证：

- 100% / 125% / 150% Windows scaling；
- 最小窗口尺寸；
- 1366×768 老笔记本仍可用；
- 最大化和普通窗口都不产生字段溢出；
- Tab 顺序符合视觉顺序；
- Enter/Space 不会误触高风险动作；
- 中英文切换不会导致按钮被裁切；
- 错误、成功状态不只靠颜色；
- 输出区域键盘可复制/滚动。

---

# 15. Splash

当前 Splash 已实现 dependency-free 像素标记 + real milestone progress。

保留原则：

- 很短也没关系，不人为 sleep；
- progress 只对应真实 startup milestone；
- 不能因为“动画更好看”而延长启动；
- 未来正式 App Icon 可复用产品像素标记，但资源必须进入 packaging manifest。

---

# 16. 实施顺序

在当前本地 UX stabilization commit + CI 被接受之前，**不要远程改同一批 Tk 源文件**。

接受后下一批 UI work 建议只做一轮 coherent shell polish：

1. 抽 `ui_theme.py` / design tokens；
2. 抽可复用 Section / Status / Action helpers；
3. 重排 Planning / Editing；
4. 重构 API Settings 为 capability-role presentation（Provider Neutral binding 的后端另按架构计划推进）；
5. 加 output overwrite confirmation / open-folder / copy-result / Doctor entry 等低风险真实功能；
6. focused tests + full quality gate + Windows manual Human UI smoke。

**不在这一轮修改 Resolver / EDL / Renderer / Review ownership。**
