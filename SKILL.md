---
name: prd-writer
description: 撰写产品需求文档(PRD)并生成可交互原型。触发条件：用户提到"需求文档"、"PRD"、"产品需求"、"写需求"、"原型"、"feature list"等关键词。集成 UI-UX-Pro-Max 设计系统，支持 Cloudflare Pages 部署。
---

# PRD Writer

产品需求文档撰写 + 原型生成工作流。

## 工作流程

### 阶段1：需求采集（Socratic 澄清）

**优先调用** `Skill('superpowers:brainstorming')`：一次一个澄清问题（多选优先）→ 提 2-3 个产品方向带 trade-offs → 用户批准后再写结构化需求。

**降级 fallback**（未装 superpowers 时）：照 [references/brainstorming-fallback.md](references/brainstorming-fallback.md) 至少问 3 个澄清问题（核心用户与场景 / MVP 边界 / 关键约束）+ 提 2-3 方案，**等用户审批后**再继续。

确认完成后整理为结构化格式：

```
## 核心业务流程
- 🔴 P0 功能名称：功能描述

## 用户端功能  
- 🟡 P1 功能名称：功能描述

## 管理端功能
- 🟢 P2 功能名称：功能描述
```

优先级：🔴 P0（必须）/ 🟡 P1（重要）/ 🟢 P2（优化）

详细 prompt 模板见 [references/prompts.md](references/prompts.md)

### 阶段2：Feature List

按模块组织功能表格，使用 [references/feature-list-template.md](references/feature-list-template.md)

**完整性检查**：主动指出缺失环节（如有"加购物车"但没"购物车编辑"）

### 阶段3：PRD 文档

使用 [references/prd-template.md](references/prd-template.md) 生成完整 PRD。

### 阶段3.5：文档自审（双层 self-review）

PRD 主文与 feature list 写完后，**完成度 ≠ 完成**，做两层自审再进阶段 4。

**第一层 · 内联 spec self-review**（来自 brainstorming）逐项检查：
1. **Placeholder 扫描**：无 TBD / TODO / 空填空
2. **内部一致性**：feature_list 每行都在 PRD 5.x 节有对应；mermaid 节点都在功能列表里
3. **Scope 检查**：MVP 能在 1 个迭代落地；P0 都是真"上不了线就开不了门"的
4. **歧义检查**：每个"自动 / 智能 / 实时 / 快速"都有可量化定义

**第二层 · reviewer 第二视角**：
- 优先 `Skill('superpowers:requesting-code-review')` dispatch 一个 reviewer subagent，把本次产物（PRD.md + feature_list.md）作为 diff 给它审，重点检查：用户旅程闭环 / 异常路径完整性 / 文档可施工性。若该 reviewer 期望代码 diff，**显式告知产物是两份 md 文档**，并把 PRD.md 和 feature_list.md 的内容作为评审材料给它
- 降级 fallback：照 [references/self-review-checklist.md](references/self-review-checklist.md) 自己逐条走 14 项

反馈分级处理：
| 等级 | 处理 |
|------|------|
| Critical | 立即修，不进阶段 4 |
| Important | 进阶段 4 前修 |
| Minor | 记到"已知问题"，V1.1 修 |

### 阶段4：原型生成

#### Step 1: 生成设计系统

```bash
python3 scripts/ui-ux-pro-max/search.py "<产品类型> <风格>" --design-system -p "项目名"
```

示例：
```bash
python3 scripts/ui-ux-pro-max/search.py "travel mobile app" --design-system -p "旅行App"
python3 scripts/ui-ux-pro-max/search.py "SaaS dashboard" --design-system -p "分析平台"
```

#### Step 2: 按需获取详细设计数据

```bash
# 配色方案
python3 scripts/ui-ux-pro-max/search.py "modern elegant" --domain color

# 字体配对
python3 scripts/ui-ux-pro-max/search.py "professional" --domain typography

# UX 准则
python3 scripts/ui-ux-pro-max/search.py "mobile form" --domain ux

# 技术栈指南
python3 scripts/ui-ux-pro-max/search.py "responsive" --stack html-tailwind
```

可用 domain: `style`, `color`, `chart`, `landing`, `product`, `ux`, `typography`, `icons`, `react`, `web`
可用 stack: `html-tailwind`, `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

#### Step 3: 生成 HTML 原型

基于设计系统输出，生成单文件 HTML（Tailwind CSS + 原生 JS）。

技术规格见 [references/prototype-guide.md](references/prototype-guide.md)

### 阶段4.5：打包站点（推荐）

把当次生成的所有 md 文档 + 原型 html 聚合成一个**带顶部导航的单文件站点**，方便交付与分享：

```bash
python3 scripts/build_site.py <产物目录> --title "项目名称"
# 例如：python3 scripts/build_site.py . --title "咖啡馆点单"
```

产出 `site.html`：
- 顶部导航菜单：自动列出所有 md 文档（按数字前缀排序）+ "原型" 标签
- md 内容客户端渲染（marked + highlight + mermaid 全部 CDN，无构建依赖）
- 原型用 `<iframe srcdoc>` 内嵌，CSS/JS 完全隔离
- 单文件、自包含、离线可用、可邮件传 / 上 Cloudflare Pages

### 阶段5：部署（可选）

Cloudflare Pages 部署（国内可访问）：

```bash
# 把 site.html 上传，或部署整个产物目录
wrangler pages deploy . --project-name=your-project
```

详见 [references/cloudflare-deploy.md](references/cloudflare-deploy.md)

## 质量检查

> **何时做**：阶段 3.5 是"文档自审"（前置，确保 PRD 自洽再进原型）；本节是"产品/业务视角的事后回顾"（贯穿全流程或交付前一次性做），与阶段 3.5 互补不替换。

完成后以四角色审视，详见 [references/quality-checklist.md](references/quality-checklist.md)：

1. **技术负责人**：实现难度、性能、安全
2. **挑剔用户**：操作便捷性、流程合理性
3. **运营负责人**：数据分析、营销推广
4. **测试工程师**：异常场景、边界问题

## 输出文件

- `feature_list.md` - 功能清单
- `PRD.md` - 完整需求文档
- `design-system/` - 设计系统
- `prototype.html` - 可交互原型
- `site.html` - 聚合站点（阶段 4.5 生成）：md + 原型 + 顶部导航，单文件可分享

## 依赖与降级

| 依赖 | 用途 | 不可用时 |
|------|------|---------|
| `superpowers:brainstorming` | 阶段 1 Socratic 澄清 | 走 [references/brainstorming-fallback.md](references/brainstorming-fallback.md) 内联问卷 |
| `superpowers:requesting-code-review` | 阶段 3.5 第二视角 reviewer | 走 [references/self-review-checklist.md](references/self-review-checklist.md) 自审 |
| `python3` | 设计系统检索 / 聚合站点 | 必需（无降级）|
| `wrangler` CLI | 阶段 5 部署 | 可省（手工上传 site.html 到任意静态托管，详见 [references/cloudflare-deploy.md](references/cloudflare-deploy.md)）|
