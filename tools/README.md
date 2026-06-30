# 博客快速发布工具

无需本地 Git，直接通过 GitHub API 发布文章。

**功能特点：**
- ✅ 支持 Typora 图片文件夹结构（.assets 文件夹）
- ✅ 支持单文件和文件夹批量上传
- ✅ 自动添加 front matter（title、date）
- ✅ 直接在 PyCharm 中运行

---

## 下载

**下载地址**: https://github.com/nasplayer/my-blog/tree/main/tools

下载 `publish.py` 文件即可。

---

## 安装依赖

```bash
pip install requests
```

---

## 配置

打开 `publish.py`，修改第 25-31 行：

```python
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # 替换为你的 GitHub Token
GITHUB_REPO = "nasplayer/my-blog"    # 你的 GitHub 仓库
GITHUB_BRANCH = "main"               # 分支名
BLOG_URL = "https://nasplayer.de5.net"  # 你的博客地址

# 默认上传文件夹（直接运行时使用）
DEFAULT_FOLDER = r"C:\drive\pen的项目\Moviepilot教程"
```

### 如何获取 GitHub Token

1. 打开 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 勾选 `repo` 权限
4. 生成并复制 Token

---

## 使用方法

### 方式一：PyCharm 直接运行

1. 用 PyCharm 打开 `publish.py`
2. 修改配置（见上方）
3. 点击运行按钮 ▶️ 或右键 -> Run 'publish'
4. 自动上传 `DEFAULT_FOLDER` 里的所有 MD 文件

### 方式二：命令行运行

```bash
# 上传默认文件夹所有 MD 文件
python publish.py

# 上传单个文件
python publish.py "C:\drive\pen的项目\Moviepilot教程\Moviepilot手动刮削教程.md"

# 上传指定文件夹所有 MD 文件
python publish.py "C:\drive\pen的项目\Moviepilot教程"
```

---

## 文件夹结构

支持 Typora 的 `.assets` 图片文件夹：

```
C:\drive\pen的项目\Moviepilot教程\
    ├── Moviepilot手动刮削教程.md
    ├── Moviepilot手动刮削教程.assets\
    │       ├── image-1.png
    │       └── image-2.png
    ├── Moviepilot用户认证教程.md
    └── Moviepilot用户认证教程.assets\
            └── screenshot.png
```

---

## 自动添加 Front Matter

脚本会自动添加/更新 front matter：

```markdown
---
title: Moviepilot手动刮削教程
date: 2026-06-30
draft: false
---

# 原文章内容...
```

- **title**: 文件名（不含扩展名）
- **date**: 文件修改时间

---

## 运行示例

```
==================================================
📝 博客快速发布工具
==================================================
📂 使用默认文件夹: C:\drive\pen的项目\Moviepilot教程

==================================================
📚 批量发布: C:\drive\pen的项目\Moviepilot教程
   找到 3 个 MD 文件
==================================================

📝 处理文章: Moviepilot手动刮削教程.md
--------------------------------------------------
📌 标题: Moviepilot手动刮削教程
🔗 Slug: moviepilot
📂 找到图片文件夹: Moviepilot手动刮削教程.assets
📤 上传图片...
  ✅ 已上传: static/images/image-1.png
  ✅ 已上传: static/images/image-2.png
   已上传 2 张图片
📤 上传文章...
  ✅ 已上传: content/posts/moviepilot.md
✅ 发布成功: https://nasplayer.de5.net/moviepilot/

📝 处理文章: Moviepilot用户认证教程.md
--------------------------------------------------
📌 标题: Moviepilot用户认证教程
🔗 Slug: moviepilot
📂 未找到 .assets 文件夹
📤 上传文章...
  ✅ 已上传: content/posts/moviepilot.md
✅ 发布成功: https://nasplayer.de5.net/moviepilot/

==================================================
🎉 发布完成: 3/3 篇文章
📖 博客地址: https://nasplayer.de5.net
⚙️  管理后台: https://nasplayer.de5.net/admin/
==================================================
```

---

## 注意事项

1. MD 文件使用 UTF-8 编码
2. 发布后等待 1-2 分钟让 Cloudflare Pages 部署
3. 图片文件名建议用英文和数字
4. `.assets` 文件夹要和 MD 文件在同一目录
