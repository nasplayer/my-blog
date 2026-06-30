#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客快速发布脚本 - Windows + PyCharm 版
支持 Typora 图片文件夹结构（.assets 文件夹）
支持单文件和文件夹批量上传
支持文章加密

在 PyCharm 中运行:
    直接点击运行按钮，或右键 -> Run 'publish'

命令行运行:
    python publish.py                    # 上传默认文件夹所有 MD 文件
    python publish.py "xxx.md"           # 上传单个文件
    python publish.py "C:\\文件夹路径"    # 上传指定文件夹所有 MD 文件
"""

import os
import sys
import base64
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============ 导入统一配置 ============
try:
    from config import (
        GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH,
        BLOG_URL, DEFAULT_FOLDER,
        ENCRYPTED_POSTS, DEFAULT_PASSWORD,
        PINNED_KEYWORDS, CATEGORY_RULES, TAG_RULES,
        MAX_RETRIES, RETRY_DELAY
    )
except ImportError:
    print("❌ 请先创建 config.py 配置文件")
    print("   可以复制 config.py.example 并重命名为 config.py")
    sys.exit(1)

# ============ 配置结束 ============

# GitHub API 基础 URL
API_BASE = "https://api.github.com"

# 创建带重试的 session
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

SESSION = create_session()


def get_headers():
    """获取 GitHub API 请求头"""
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def get_remote_content(path):
    """获取远程文件内容"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"
    params = {"ref": GITHUB_BRANCH}
    resp = SESSION.get(url, headers=get_headers(), params=params, timeout=30)
    
    if resp.status_code == 200:
        import base64
        content = base64.b64decode(resp.json()['content']).decode('utf-8', errors='ignore')
        return content
    return None


def get_remote_binary_content(path):
    """获取远程二进制文件内容"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"
    params = {"ref": GITHUB_BRANCH}
    resp = SESSION.get(url, headers=get_headers(), params=params, timeout=30)
    
    if resp.status_code == 200:
        import base64
        content = base64.b64decode(resp.json()['content'])
        return content
    return None


def content_needs_update(local_content, remote_content):
    """比较内容是否需要更新"""
    if remote_content is None:
        return True  # 远程不存在
    
    # 标准化比较
    local_normalized = local_content.strip().replace('\r\n', '\n')
    remote_normalized = remote_content.strip().replace('\r\n', '\n')
    
    return local_normalized != remote_normalized


def upload_to_github(path, content, message):
    """上传文件到 GitHub（带重试）"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"
    
    for attempt in range(MAX_RETRIES):
        try:
            # 检查文件是否存在，获取 sha
            params = {"ref": GITHUB_BRANCH}
            resp = SESSION.get(url, headers=get_headers(), params=params, timeout=30)
            
            data = {
                "message": message,
                "branch": GITHUB_BRANCH,
                "content": content,
            }
            
            if resp.status_code == 200:
                # 文件存在，更新
                data["sha"] = resp.json()["sha"]
            
            resp = SESSION.put(url, headers=get_headers(), json=data, timeout=30)
            
            if resp.status_code in [200, 201]:
                print(f"  ✅ 已上传: {path}")
                return True
            else:
                print(f"  ❌ 上传失败: {path}")
                print(f"     错误: {resp.text}")
                return False
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  ⚠️ 网络错误，{RETRY_DELAY}秒后重试 ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ❌ 上传失败: {path}")
                print(f"     错误: {e}")
                return False
    
    return False


def get_password_for_title(title):
    """根据标题获取密码"""
    # 检查是否匹配加密文章配置
    for keyword, password in ENCRYPTED_POSTS.items():
        if keyword in title:
            return password
    
    # 使用默认密码
    return DEFAULT_PASSWORD


def get_category_for_title(title):
    """根据标题获取分类"""
    for keyword, category in CATEGORY_RULES.items():
        if keyword in title:
            return category
    return None


def get_tags_for_title(title):
    """根据标题获取标签"""
    tags = []
    for keyword, tag_list in TAG_RULES.items():
        if keyword in title:
            tags.extend(tag_list)
    return list(set(tags)) if tags else None  # 去重


def is_pinned(title):
    """检查文章是否需要置顶"""
    for keyword in PINNED_KEYWORDS:
        if keyword in title:
            return True
    return False


def fix_markdown_content(content):
    """修复 Markdown 内容"""
    # 1. 修复 \# 转义
    content = re.sub(r'\\#', '#', content)
    
    # 2. 修复日期格式 (2026-06-30T15:01:00.000Z -> 2026-06-30)
    content = re.sub(
        r'date:\s*\d{4}-\d{2}-\d{2}T[\d:.]+Z',
        lambda m: f"date: {datetime.now().strftime('%Y-%m-%d')}",
        content
    )
    
    return content


def add_front_matter(content, title, file_path, password=None, category=None, tags=None, pinned=False):
    """添加或更新 front matter"""
    # 检查是否已有 front matter
    if content.strip().startswith('---'):
        # 已有 front matter，更新 title 和 date
        # 更新 title
        content = re.sub(
            r'^title:\s*.*$',
            f'title: {title}',
            content,
            count=1,
            flags=re.MULTILINE
        )
        # 更新 date
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        content = re.sub(
            r'^date:\s*.*$',
            f"date: {mod_time.strftime('%Y-%m-%d')}",
            content,
            count=1,
            flags=re.MULTILINE
        )
        # 更新或添加 password
        if password:
            if re.search(r'^password:\s*.*$', content, re.MULTILINE):
                content = re.sub(
                    r'^password:\s*.*$',
                    f'password: "{password}"',
                    content,
                    count=1,
                    flags=re.MULTILINE
                )
            else:
                content = re.sub(
                    r'^---\n',
                    f'---\npassword: "{password}"\n',
                    content,
                    count=1
                )
        # 更新或添加 pinned
        if pinned:
            if re.search(r'^pinned:\s*.*$', content, re.MULTILINE):
                content = re.sub(
                    r'^pinned:\s*.*$',
                    'pinned: true',
                    content,
                    count=1,
                    flags=re.MULTILINE
                )
            else:
                content = re.sub(
                    r'^---\n',
                    f'---\npinned: true\n',
                    content,
                    count=1
                )
        # 更新或添加 categories
        if category:
            if re.search(r'^categories:\s*.*$', content, re.MULTILINE):
                content = re.sub(
                    r'^categories:\s*.*$',
                    f'categories: ["{category}"]',
                    content,
                    count=1,
                    flags=re.MULTILINE
                )
            else:
                content = re.sub(
                    r'^---\n',
                    f'---\ncategories: ["{category}"]\n',
                    content,
                    count=1
                )
        # 更新或添加 tags
        if tags:
            tags_str = ', '.join([f'"{t}"' for t in tags])
            if re.search(r'^tags:\s*.*$', content, re.MULTILINE):
                content = re.sub(
                    r'^tags:\s*.*$',
                    f'tags: [{tags_str}]',
                    content,
                    count=1,
                    flags=re.MULTILINE
                )
            else:
                content = re.sub(
                    r'^---\n',
                    f'---\ntags: [{tags_str}]\n',
                    content,
                    count=1
                )
    else:
        # 没有 front matter，添加
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        front_matter = f"""---
title: {title}
date: {mod_time.strftime('%Y-%m-%d')}
"""
        if pinned:
            front_matter += 'pinned: true\n'
        if password:
            front_matter += f'password: "{password}"\n'
        if category:
            front_matter += f'categories: ["{category}"]\n'
        if tags:
            tags_str = ', '.join([f'"{t}"' for t in tags])
            front_matter += f'tags: [{tags_str}]\n'
        
        front_matter += """draft: false
toc:
  ordered: false
---

"""
        content = front_matter + content
    
    return content


def find_assets_folder(md_file_path):
    """查找 .assets 文件夹"""
    md_path = Path(md_file_path)
    md_dir = md_path.parent
    md_name = md_path.stem  # 文件名不带扩展名
    
    # .assets 文件夹
    assets_path = md_dir / f"{md_name}.assets"
    
    if assets_path.exists() and assets_path.is_dir():
        return assets_path
    
    return None


def get_remote_file_info(path):
    """获取远程文件信息（大小和SHA）"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"
    params = {"ref": GITHUB_BRANCH}
    resp = SESSION.get(url, headers=get_headers(), params=params, timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        return {
            'size': data.get('size', 0),
            'sha': data.get('sha'),
        }
    return None


def upload_images_from_assets(assets_folder, slug):
    """上传 .assets 文件夹中的所有图片
    
    Args:
        assets_folder: .assets 文件夹路径
        slug: 文章的 slug，用作图片路径前缀，避免同名冲突
    
    Returns:
        dict: {原文件名: GitHub路径}
    """
    uploaded = {}  # {原文件名: GitHub路径}
    
    # 支持的图片格式
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'}
    
    for file_path in assets_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            img_name = file_path.name
            local_size = file_path.stat().st_size
            
            # 使用 slug 作为子文件夹，避免同名冲突
            github_path = f"static/images/{slug}/{img_name}"
            web_path = f"/images/{slug}/{img_name}"
            
            # 快速检查：先比较文件大小
            remote_info = get_remote_file_info(github_path)
            if remote_info and remote_info['size'] == local_size:
                # 大小相同，大概率没变，跳过
                print(f"  ⏭️ 跳过: {img_name}")
                uploaded[img_name] = web_path
                continue
            
            # 大小不同或远程不存在，需要上传
            with open(file_path, 'rb') as f:
                img_content = base64.b64encode(f.read()).decode()
            
            if upload_to_github(github_path, img_content, f"上传图片 {slug}/{img_name}"):
                uploaded[img_name] = web_path
    
    return uploaded


def fix_image_paths(content, assets_folder, uploaded_images):
    """修正 MD 文件中的图片路径"""
    
    # 匹配 Markdown 图片语法 ![alt](path)
    def replace_md_img(match):
        alt = match.group(1)
        img_path = match.group(2)
        
        if img_path.startswith('http'):
            return match.group(0)
        
        # URL 解码
        img_path = unquote(img_path)
        
        # 获取图片文件名
        img_name = Path(img_path).name
        
        # 如果图片已上传，替换路径
        if img_name in uploaded_images:
            return f'![{alt}]({uploaded_images[img_name]})'
        
        return match.group(0)
    
    # 匹配 HTML img 标签
    def replace_html_img(match):
        full_tag = match.group(0)
        img_path = match.group(1)
        
        if img_path.startswith('http'):
            return full_tag
        
        # URL 解码
        img_path = unquote(img_path)
        
        # 获取图片文件名
        img_name = Path(img_path).name
        
        # 如果图片已上传，替换为 Markdown 格式
        if img_name in uploaded_images:
            return f'![图片]({uploaded_images[img_name]})'
        
        return full_tag
    
    # 处理 Markdown 图片
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_md_img, content)
    
    # 处理 HTML 图片
    content = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', replace_html_img, content)
    
    return content


def generate_slug(title):
    """根据标题生成 URL slug"""
    # 移除特殊字符
    slug = re.sub(r'[^\w\s-]', '', title)
    # 替换空格为连字符
    slug = re.sub(r'\s+', '-', slug)
    # 转小写
    slug = slug.lower()
    return slug


def publish_article(md_file_path):
    """发布单篇文章"""
    md_path = Path(md_file_path)
    
    if not md_path.exists():
        print(f"❌ 文件不存在: {md_file_path}")
        return False
    
    print(f"\n📝 处理文章: {md_path.name}")
    print("-" * 50)
    
    # 读取文件内容
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取标题（文件名）
    title = md_path.stem
    print(f"📌 标题: {title}")
    
    # 检查是否需要加密
    password = get_password_for_title(title)
    if password:
        print(f"🔐 加密文章，密码: {password}")
    
    # 检查是否需要置顶
    pinned = is_pinned(title)
    if pinned:
        print("📌 置顶文章")
    
    # 获取分类
    category = get_category_for_title(title)
    if category:
        print(f"📂 分类: {category}")
    
    # 获取标签
    tags = get_tags_for_title(title)
    if tags:
        print(f"🏷️ 标签: {', '.join(tags)}")
    
    # 添加/更新 front matter
    content = add_front_matter(content, title, md_path, password, category, tags, pinned)
    
    # 生成 slug
    slug = generate_slug(title)
    print(f"🔗 Slug: {slug}")
    
    # 修复内容
    content = fix_markdown_content(content)
    
    # 查找 .assets 文件夹
    assets_folder = find_assets_folder(md_file_path)
    uploaded_images = {}
    
    if assets_folder:
        print(f"📂 找到图片文件夹: {assets_folder.name}")
        print("📤 上传图片...")
        # 传入 slug，图片会存到 static/images/{slug}/ 目录
        uploaded_images = upload_images_from_assets(assets_folder, slug)
        
        if uploaded_images:
            print(f"   已上传 {len(uploaded_images)} 张图片")
            
            # 修正图片路径
            content = fix_image_paths(content, assets_folder, uploaded_images)
        else:
            print("   无图片需要上传")
    else:
        print("📂 未找到 .assets 文件夹")
    
    # 上传文章
    github_path = f"content/posts/{slug}.md"
    
    # 快速检查：比较文件大小
    remote_info = get_remote_file_info(github_path)
    local_size = len(content.encode('utf-8'))
    
    if remote_info and remote_info['size'] == local_size:
        # 大小相同，再比较内容（防止碰巧大小相同）
        remote_content = get_remote_content(github_path)
        if not content_needs_update(content, remote_content):
            print("⏭️ 文章无变化，跳过上传")
            return True
    
    print("📤 上传文章...")
    content_base64 = base64.b64encode(content.encode('utf-8')).decode()
    
    if upload_to_github(github_path, content_base64, f"发布文章: {title}"):
        print(f"✅ 发布成功: {BLOG_URL}/{slug}/")
        return True
    
    return False


def publish_folder(folder_path):
    """批量发布文件夹中的所有 MD 文件"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ 文件夹不存在: {folder_path}")
        return
    
    # 查找所有 MD 文件
    md_files = list(folder.glob("*.md"))
    
    if not md_files:
        print(f"❌ 未找到 MD 文件: {folder_path}")
        return
    
    print("=" * 50)
    print(f"📚 批量发布: {folder_path}")
    print(f"   找到 {len(md_files)} 个 MD 文件")
    print("=" * 50)
    
    success_count = 0
    for md_file in md_files:
        if publish_article(md_file):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 发布完成: {success_count}/{len(md_files)} 篇文章")
    print(f"📖 博客地址: {BLOG_URL}")
    print(f"⚙️  管理后台: {BLOG_URL}/admin/")
    print("=" * 50)


def main():
    print("=" * 50)
    print("📝 博客快速发布工具")
    print("=" * 50)
    
    # 检查配置
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        print("\n❌ 请先修改脚本顶部的 GITHUB_TOKEN 配置！")
        print("   获取 Token: https://github.com/settings/tokens")
        return
    
    # 显示加密配置
    if ENCRYPTED_POSTS or DEFAULT_PASSWORD:
        print("\n🔐 加密文章配置:")
        for keyword, pwd in ENCRYPTED_POSTS.items():
            print(f"   标题含 \"{keyword}\" → 密码: {pwd}")
        if DEFAULT_PASSWORD:
            print(f"   默认密码: {DEFAULT_PASSWORD}")
    
    if len(sys.argv) < 2:
        # 无参数，使用默认文件夹
        print(f"\n📂 使用默认文件夹: {DEFAULT_FOLDER}")
        publish_folder(DEFAULT_FOLDER)
    else:
        arg = sys.argv[1]
        path = Path(arg)
        
        if path.is_file():
            # 单个文件
            publish_article(arg)
        elif path.is_dir():
            # 文件夹
            publish_folder(arg)
        else:
            print(f"❌ 路径不存在: {arg}")


if __name__ == "__main__":
    main()
