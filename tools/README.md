# 博客快速发布工具

无需本地 Git 环境，直接通过 GitHub API 发布文章。

**支持 Typora 图片文件夹结构（.assets 文件夹）**

## 下载

从 GitHub 下载 `publish.py` 文件。

**下载地址**: https://github.com/nasplayer/my-blog/tree/main/tools

## 安装依赖

```bash
pip install requests
```

## 配置

打开 `publish.py`，修改第 24-27 行：

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
python publish.py "D:\教程\Moviepilot手动刮削教程.md"
```

## 图片文件夹结构

脚本自动识别 Typora 的 `.assets` 文件夹：

```
D:\教程\
    ├── Moviepilot手动刮削教程.md
    └── Moviepilot手动刮削教程.assets\
            ├── image-1.png
            └── image-2.png
```

脚本会：
1. 自动找到 `Moviepilot手动刮削教程.assets` 文件夹
2. 上传里面所有图片到 GitHub
3. 修正 MD 文件中的图片路径

## 功能说明

| 功能 | 说明 |
|------|------|
| ✅ 自动识别 .assets 文件夹 | 无需手动指定图片路径 |
| ✅ 自动修复日期格式 | `2026-06-30T15:01:00.000Z` → `2026-06-30` |
| ✅ 自动修复标题转义 | `\# 标题` → `# 标题` |
| ✅ 自动上传图片 | 复制到 `static/images/` 并修正路径 |
| ✅ 支持多种图片格式 | png, jpg, jpeg, gif, webp, svg, bmp |
| ✅ 自动提交推送 | 通过 GitHub API 提交 |

## 注意事项

1. MD 文件使用 UTF-8 编码
2. 发布后等待 1-2 分钟让 Cloudflare Pages 部署
3. 图片文件名不要有特殊字符和中文（建议用英文和数字）
4. `.assets` 文件夹要和 MD 文件在同一目录

## 完整示例

假设你有以下目录结构：

```
D:\教程\
    ├── Moviepilot手动刮削教程.md
    └── Moviepilot手动刮削教程.assets\
            ├── step1.png
            ├── step2.png
            └── step3.png
```

MD 文件内容：

```markdown
---
title: Moviepilot手动刮削教程
date: 2026-06-30
---

# Moviepilot手动刮削教程

## 第一步

![步骤1](Moviepilot手动刮削教程.assets/step1.png)

## 第二步

![步骤2](Moviepilot手动刮削教程.assets/step2.png)

## 第三步

<img src="Moviepilot手动刮削教程.assets/step3.png" alt="步骤3">
```

运行命令：

```bash
python publish.py "D:\教程\Moviepilot手动刮削教程.md"
```

输出：

```
📝 处理文章: Moviepilot手动刮削教程.md
==================================================
📌 标题: Moviepilot手动刮削教程
🔗 Slug: moviepilot

📂 找到图片文件夹: Moviepilot手动刮削教程.assets
📤 上传图片...
  ✅ 已上传: static/images/step1.png
  ✅ 已上传: static/images/step2.png
  ✅ 已上传: static/images/step3.png
   已上传 3 张图片

📤 上传文章...
  ✅ 已上传: content/posts/moviepilot.md

==================================================
🎉 发布成功!
📖 文章地址: https://nasplayer.de5.net/moviepilot/
⚙️  管理后台: https://nasplayer.de5.net/admin/
```
