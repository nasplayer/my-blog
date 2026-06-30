# -*- coding: utf-8 -*-
"""
博客工具统一配置
只需修改这个文件，其他脚本自动读取配置
"""

# ============ GitHub 配置 ============
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # 替换为你的 GitHub Token
GITHUB_REPO = "nasplayer/my-blog"
GITHUB_BRANCH = "main"

# ============ 博客配置 ============
BLOG_URL = "https://nasplayer.de5.net"

# ============ 默认文件夹 ============
# Windows 路径注意使用 r"" 或双反斜杠
DEFAULT_FOLDER = r"C:\drive\pen的项目\Moviepilot教程"

# ============ 加密文章配置 ============
# 格式: {"文章标题关键词": "密码"}
# 标题关键词会进行模糊匹配，包含该关键词的文章都会加密
ENCRYPTED_POSTS = {
    "非公开": "nasplayer",  # 标题包含"非公开"的文章，密码为 nasplayer
}

# 默认密码（如果文章需要加密但未在上面配置，则使用此密码）
# 设为 None 表示不使用默认密码
DEFAULT_PASSWORD = None

# ============ 置顶文章配置 ============
# 标题包含这些关键词的文章会自动置顶
PINNED_KEYWORDS = [
    # "重要",
    # "置顶",
]

# ============ 分类配置 ============
# 格式: {"标题关键词": "分类名"}
# 标题包含关键词的文章会自动归类
CATEGORY_RULES = {
    # "MoviePilot": "MoviePilot教程",
    # "NAS": "NAS教程",
}

# ============ 标签配置 ============
# 格式: {"标题关键词": ["标签1", "标签2"]}
# 标题包含关键词的文章会自动添加标签
TAG_RULES = {
    # "MoviePilot": ["MoviePilot", "教程"],
    # "认证": ["认证", "安全"],
}

# ============ 网络配置 ============
MAX_RETRIES = 5      # 最大重试次数
RETRY_DELAY = 2      # 重试间隔（秒）
