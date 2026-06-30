# 博客快速发布工具

无需本地 Git 环境，直接通过 GitHub API 发布文章。

## 下载

从 GitHub 下载整个 `tools` 文件夹，或只下载 `publish.py` 文件。

## 安装依赖

```bash
pip install requests
```

## 配置

打开 `publish.py`，修改顶部的配置：

```python
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # 替换为你的 GitHub Personal Access Token
GITHUB_REPO = "nasplayer/my-blog"    # 你的 GitHub 仓库
GITHUB_BRANCH = "main"               # 分支名
BLOG_URL = "https://nasplayer.de5.net"  # 你的博客地址
```

### 如何获取 GitHub Token

1. 打开 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 勾选 `repo` 权限
4. 生成并复制 Token

## 使用方法

```bash
python publish.py "D:\我的文档\教程.md"
```

## 功能说明

| 功能 | 说明 |
|------|------|
| ✅ 自动修复日期格式 | `2026-06-30T15:01:00.000Z` → `2026-06-30` |
| ✅ 自动修复标题转义 | `\# 标题` → `# 标题` |
| ✅ 自动上传图片 | 复制到 `static/images/` 并修正路径 |
| ✅ 自动提交推送 | 通过 GitHub API 提交 |

## 图片路径说明

MD 文件中的图片路径支持：

| 格式 | 示例 |
|------|------|
| 相对路径 | `./images/xxx.png` |
| 相对路径 | `images/xxx.png` |
| 同目录 | `xxx.png` |
| HTML 标签 | `<img src="xxx.png">` |

## 注意事项

1. MD 文件使用 UTF-8 编码
2. 发布后等待 1-2 分钟让 Cloudflare Pages 部署
3. 图片文件名不要有特殊字符和中文

## 示例

假设你有以下目录结构：

```
D:\教程\
  ├── MoviePilot使用教程.md
  └── images\
        ├── screenshot1.png
        └── screenshot2.png
```

MD 文件内容：

```markdown
---
title: MoviePilot使用教程
date: 2026-06-30
---

# MoviePilot使用教程

## 安装步骤

![截图1](images/screenshot1.png)

## 配置说明

![截图2](images/screenshot2.png)
```

运行命令：

```bash
python publish.py "D:\教程\MoviePilot使用教程.md"
```

脚本会自动：
1. 上传 `screenshot1.png` 和 `screenshot2.png` 到 GitHub
2. 修正 MD 文件中的图片路径
3. 上传 MD 文件到 GitHub
4. Cloudflare Pages 自动部署
