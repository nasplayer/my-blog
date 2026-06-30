# 博客快速发布工具

无需本地 Git，直接通过 GitHub API 发布文章。

**功能特点：**
- ✅ 支持 Typora 图片文件夹结构（.assets 文件夹）
- ✅ 支持单文件和文件夹批量上传
- ✅ 自动添加 front matter（title、date）
- ✅ 支持文章加密（按标题关键词自动加密）
- ✅ 支持文章置顶、分类、标签
- ✅ **增量更新：只上传有变化的文件，跳过未修改的**
- ✅ 直接在 PyCharm 中运行

---

## 📥 下载

**下载地址**: https://github.com/nasplayer/my-blog/tree/main/tools

| 脚本 | 功能 |
|------|------|
| `config.py` | **统一配置文件（只需改这个）** |
| `publish.py` | 发布文章 |
| `delete_article.py` | 删除文章 |
| `clean_images.py` | 删除所有图片 |
| `clean_unused_images.py` | 删除未使用的图片 |

---

## 📦 安装依赖

```bash
pip install requests
```

---

## ⚙️ 配置

**只需修改一个文件：`config.py`**

### 1. 复制配置文件

```bash
# 下载后重命名
cp config.py config.py
```

### 2. 修改配置

打开 `config.py`，修改以下内容：

```python
# GitHub 配置
GITHUB_TOKEN = "你的GitHub Token"
GITHUB_REPO = "nasplayer/my-blog"
GITHUB_BRANCH = "main"

# 博客配置
BLOG_URL = "https://nasplayer.de5.net"

# 默认文件夹
DEFAULT_FOLDER = r"C:\drive\pen的项目\Moviepilot教程"
```

### 3. 其他配置（可选）

```python
# 加密配置
ENCRYPTED_POSTS = {
    "非公开": "你的密码",
}

# 置顶配置
PINNED_KEYWORDS = ["重要", "置顶"]

# 分类配置
CATEGORY_RULES = {
    "MoviePilot": "MoviePilot教程",
}

# 标签配置
TAG_RULES = {
    "MoviePilot": ["MoviePilot", "教程"],
}
```

### 4. 获取 GitHub Token

1. 打开 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 勾选 `repo` 权限
4. 生成并复制 Token

---

## 🚀 使用方法

### 方式一：PyCharm 直接运行

1. 用 PyCharm 打开 `publish.py`
2. 修改配置
3. 点击运行按钮 ▶️
4. 自动上传 `DEFAULT_FOLDER` 里的所有 MD 文件

### 方式二：命令行运行

```bash
# 上传默认文件夹所有 MD 文件
python publish.py

# 上传单个文件
python publish.py "C:\教程\Moviepilot教程.md"

# 上传指定文件夹所有 MD 文件
python publish.py "C:\教程"
```

---

## 📁 文件夹结构

支持 Typora 的 `.assets` 图片文件夹：

```
C:\教程\
    ├── Moviepilot教程.md
    └── Moviepilot教程.assets\
            ├── image-1.png
            └── image-2.png
```

---

## 🔐 文章加密

### 加密规则

| 文章标题 | 是否加密 |
|----------|----------|
| 包含"非公开" | ✅ 加密 |
| 其他文章 | ❌ 不加密 |

### 自定义加密规则

修改 `ENCRYPTED_POSTS` 配置：

```python
ENCRYPTED_POSTS = {
    "非公开": "密码1",
    "敏感": "密码2",
    "机密": "密码3",
}
```

### 所有文章加密

```python
ENCRYPTED_POSTS = {}
DEFAULT_PASSWORD = "统一密码"
```

---

## 🔄 更新文章

修改 MD 文件后重新运行脚本，会自动覆盖旧文章。

**注意**：如果文章标题改变，会创建新文章而不是更新旧文章。

---

## 🗑️ 删除文章

```bash
python delete_article.py
```

运行后会列出所有文章，输入编号或文件名删除。

删除文章时会同时删除相关图片。

---

## 🗑️ 清理图片

### 删除所有图片

```bash
python clean_images.py
```

### 删除未使用的图片

```bash
python clean_unused_images.py
```

自动检测哪些图片没有被任何文章引用，并删除。

---

## 📋 运行示例

### 首次发布

```
==================================================
📝 博客快速发布工具
==================================================

📂 使用默认文件夹: C:\drive\pen的项目\Moviepilot教程
==================================================
📚 批量发布: C:\drive\pen的项目\Moviepilot教程
   找到 3 个 MD 文件
==================================================

📝 处理文章: Moviepilot教程.md
--------------------------------------------------
📌 标题: Moviepilot教程
🔗 Slug: moviepilot教程
📂 找到图片文件夹: Moviepilot教程.assets
📤 上传图片...
  ✅ 已上传: static/images/moviepilot教程/image-1.png
  ✅ 已上传: static/images/moviepilot教程/image-2.png
   已上传 2 张图片
📤 上传文章...
  ✅ 已上传: content/posts/moviepilot教程.md
✅ 发布成功: https://nasplayer.de5.net/moviepilot教程/

==================================================
🎉 发布完成: 3/3 篇文章
==================================================
```

### 再次运行（增量更新）

```
==================================================
📝 博客快速发布工具
==================================================

📚 批量发布: C:\drive\pen的项目\Moviepilot教程
   找到 3 个 MD 文件
==================================================

📝 处理文章: Moviepilot教程.md
--------------------------------------------------
📌 标题: Moviepilot教程
📂 找到图片文件夹: Moviepilot教程.assets
📤 上传图片...
  ⏭️ 跳过（无变化）: image-1.png
  ⏭️ 跳过（无变化）: image-2.png
   无图片需要上传
⏭️ 文章无变化，跳过上传

📝 处理文章: 非公开设置教程.md
--------------------------------------------------
📌 标题: 非公开设置教程
🔐 加密文章，密码: ***
📤 上传文章...
  ✅ 已上传: content/posts/非公开设置教程.md
✅ 发布成功: https://nasplayer.de5.net/非公开设置教程/

==================================================
🎉 发布完成: 2/3 篇文章（1篇跳过）
==================================================
```

---

## ⚠️ 注意事项

1. MD 文件使用 UTF-8 编码
2. 发布后等待 1-2 分钟让 Cloudflare Pages 部署
3. 图片文件名建议用英文和数字
4. `.assets` 文件夹要和 MD 文件在同一目录
5. 加密是前端加密，不适合高度敏感内容
