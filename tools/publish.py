#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客快速发布脚本 - Windows + PyCharm 版
支持 Typora 图片文件夹结构（.assets 文件夹）
支持单文件和文件夹批量上传

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

# ============ 配置区域（请修改为你自己的） ============
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # 替换为你的 GitHub Personal Access Token
GITHUB_REPO = "nasplayer/my-blog"    # 你的 GitHub 仓库
GITHUB_BRANCH = "main"               # 分支名
BLOG_URL = "https://nasplayer.de5.net"  # 你的博客地址

# 默认上传文件夹（直接运行时使用）
DEFAULT_FOLDER = r"C:\drive\pen的项目\Moviepilot教程"

# 重试配置
MAX_RETRIES = 5  # 最大重试次数
RETRY_DELAY = 3  # 重试间隔（秒）
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


def add_front_matter(content, title, file_path):
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
    else:
        # 没有 front matter，添加
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        front_matter = f"""---
title: {title}
date: {mod_time.strftime('%Y-%m-%d')}
draft: false
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


def upload_images_from_assets(assets_folder):
    """上传 .assets 文件夹中的所有图片"""
    uploaded = {}  # {原文件名: GitHub路径}
    
    # 支持的图片格式
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'}
    
    for file_path in assets_folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            img_name = file_path.name
            github_path = f"static/images/{img_name}"
            
            with open(file_path, 'rb') as f:
                img_content = base64.b64encode(f.read()).decode()
            
            if upload_to_github(github_path, img_content, f"上传图片 {img_name}"):
                uploaded[img_name] = f"/images/{img_name}"
    
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
    
    # 添加/更新 front matter
    content = add_front_matter(content, title, md_path)
    
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
        uploaded_images = upload_images_from_assets(assets_folder)
        
        if uploaded_images:
            print(f"   已上传 {len(uploaded_images)} 张图片")
            
            # 修正图片路径
            content = fix_image_paths(content, assets_folder, uploaded_images)
        else:
            print("   无图片需要上传")
    else:
        print("📂 未找到 .assets 文件夹")
    
    # 上传文章
    print("📤 上传文章...")
    github_path = f"content/posts/{slug}.md"
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
