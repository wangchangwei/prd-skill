# PRD Writer Skill

AI Agent 技能：撰写产品需求文档(PRD) + 生成可交互原型。

## 功能

- 📋 从会议记录/需求描述提取结构化需求
- 📝 生成完整的 PRD 文档（Markdown 格式）
- 🎨 集成 UI-UX-Pro-Max 设计系统
- 🖥️ 生成单文件 HTML 可交互原型
- 🚀 支持 Cloudflare Pages 一键部署

## 安装

把 skill 克隆到 Claude Code 的 skills 目录：

```bash
# 全局（所有项目可用）
git clone https://github.com/wangchangwei/prd-skill.git ~/.claude/skills/prd-writer

# 或项目级（仅当前项目可用）
git clone https://github.com/wangchangwei/prd-skill.git <你的项目>/.claude/skills/prd-writer
```

> 其他客户端（Claude.ai 桌面端 / Cursor / 第三方 skill 管理器如 clawhub）有各自的 skills 目录，按各自文档放即可。

## 触发条件

当用户提到以下关键词时自动触发：
- "需求文档"、"PRD"、"产品需求"、"写需求"
- "原型"、"feature list"

## 目录结构

```
prd-writer/
├── SKILL.md                 # 技能主文件
├── references/              # 参考文档
│   ├── prd-template.md      # PRD 模板
│   ├── feature-list-template.md
│   ├── prototype-guide.md   # 原型生成指南
│   ├── quality-checklist.md # 质量检查清单
│   └── ...
└── scripts/                 # 可执行脚本
    └── ui-ux-pro-max/       # 设计系统搜索引擎
        ├── search.py        # 主入口
        └── data/            # 设计数据 CSV
```

## 使用示例

```
用户: 帮我写一个电商小程序的 PRD

Agent: [自动触发 prd-writer 技能]
       1. 采集需求（优先用 superpowers:brainstorming 做 Socratic 澄清）
       2. 生成 Feature List
       3. 生成 PRD 文档
       3.5 文档自审（两层：内联 spec self-review + reviewer subagent）
       4. 生成设计系统
       5. 生成 HTML 原型
```

> 阶段 1 的澄清与阶段 3.5 的自审优先调用 [superpowers](https://github.com/obra/superpowers) 的 brainstorming / requesting-code-review；未安装时自动降级到 `references/brainstorming-fallback.md` 与 `references/self-review-checklist.md` 内联模板。

## 📦 一键打包站点

PRD + 原型 + 质检报告等所有产物，可打包成**一个带顶部导航的单文件站点**：

```bash
python3 scripts/build_site.py <产物目录>
# 例如：python3 scripts/build_site.py ./my-project --title "我的项目"
```

生成 `site.html`，双击浏览器即可看：
- 顶部 tab 在 md 文档和可交互原型之间切换
- md 自动按数字前缀排序、左侧 ToC 自动生成
- mermaid / 代码高亮 / 表格全部支持
- 自包含、离线可用，可邮件传 / 上 Cloudflare Pages

## 设计系统搜索

```bash
# 生成完整设计系统推荐
python3 scripts/ui-ux-pro-max/search.py "SaaS dashboard" --design-system -p "项目名"

# 搜索配色方案
python3 scripts/ui-ux-pro-max/search.py "fintech" --domain color

# 搜索字体配对
python3 scripts/ui-ux-pro-max/search.py "modern elegant" --domain typography
```

## 部署到 Cloudflare Pages

原型生成后可一键部署到 Cloudflare Pages（国内可访问、免费、自动 HTTPS）。

### 1. 创建 API Token

访问 https://dash.cloudflare.com/profile/api-tokens → **Create Token** → **Custom Token**，配置以下权限：

| 权限 | 资源范围 | 是否必须 |
|------|---------|---------|
| `Cloudflare Pages:Edit` | Account | ✅ 必须 |
| `Account Settings:Read` | Account | ✅ 必须 |
| `Zone:Read` | All Zones | 自定义域名时需要 |
| `DNS:Edit` | 指定 Zone | 绑定域名时需要 |

同时在 Dashboard 右侧边栏复制你的 **Account ID**。

> 详细部署步骤见 [references/cloudflare-deploy.md](references/cloudflare-deploy.md)

## License

MIT

## 致谢

本项目 fork 自 [FinStep-AI/prd-writer-skill](https://github.com/FinStep-AI/prd-writer-skill)，感谢原作者搭建的 PRD 撰写 + 原型生成工作流与 UI-UX-Pro-Max 数据集。

本 fork 主要新增：
- 📦 `scripts/build_site.py` —— 把每次生成的所有 md + 原型聚合成一个带顶部导航的单文件站点（参见 [一键打包站点](#-一键打包站点) 段）
- 📝 文档同步：补全 `SKILL.md` 中的 domain / stack 全集，修正安装路径为 Claude Code 标准目录
