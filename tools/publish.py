#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客快速发布脚本 - Windows + PyCharm 版
支持 Typora 图片文件夹结构（.assets 文件夹）

使用方法:
    python publish.py "D:\\教程\\Moviepilot手动刮削教程.md"

图片文件夹结构:
    D:\\教程\\
        ├── Moviepilot手动刮削教程.md
        └── Moviepilot手动刮削教程.assets\\
                ├── image-1.png
                └── image-2.png

依赖安装:
    pip install requests
"""

import os
import sys
import base64
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

import requests

# ============ 配置区域（请修改为你自己的） ============
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # 替换为你的 GitHub Personal Access Token
GITHUB_REPO = "nasplayer/my-blog"    # 你的 GitHub 仓库
GITHUB_BRANCH = "main"               # 分支名
BLOG_URL = "https://nasplayer.de5.net"  # 你的博客地址
# ============ 配置结束 ============

# GitHub API 基础 URL
API_BASE = "https://api.github.com"


def get_headers():
    """获取 GitHub API 请求头"""
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def upload_to_github(path, content, message):
    """上传文件到 GitHub"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"
    
    # 检查文件是否存在，获取 sha
    params = {"ref": GITHUB_BRANCH}
    resp = requests.get(url, headers=get_headers(), params=params)
    
    data = {
        "message": message,
        "branch": GITHUB_BRANCH,
        "content": content,
    }
    
    if resp.status_code == 200:
        # 文件存在，更新
        data["sha"] = resp.json()["sha"]
    
    resp = requests.put(url, headers=get_headers(), json=data)
    
    if resp.status_code in [200, 201]:
        print(f"  ✅ 已上传: {path}")
        return True
    else:
        print(f"  ❌ 上传失败: {path}")
        print(f"     错误: {resp.text}")
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


def find_assets_folder(md_file_path):
    """查找 .assets 文件夹"""
    md_path = Path(md_file_path)
    md_dir = md_path.parent
    md_name = md_path.stem  # 文件名不带扩展名
    
    # 可能的 .assets 文件夹名称
    possible_names = [
        f"{md_name}.assets",  # Moviepilot手动刮削教程.assets
        f"{md_name}.assets",  # 同上
    ]
    
    for name in possible_names:
        assets_path = md_dir / name
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
    """发布文章"""
    md_path = Path(md_file_path)
    
    if not md_path.exists():
        print(f"❌ 文件不存在: {md_file_path}")
        return False
    
    print(f"\n📝 处理文章: {md_path.name}")
    print("=" * 50)
    
    # 读取文件内容
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析 front matter 获取标题
    title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = md_path.stem
    
    print(f"📌 标题: {title}")
    
    # 生成 slug
    slug = generate_slug(title)
    print(f"🔗 Slug: {slug}")
    
    # 修复内容
    content = fix_markdown_content(content)
    
    # 查找 .assets 文件夹
    assets_folder = find_assets_folder(md_file_path)
    uploaded_images = {}
    
    if assets_folder:
        print(f"\n📂 找到图片文件夹: {assets_folder.name}")
        print("📤 上传图片...")
        uploaded_images = upload_images_from_assets(assets_folder)
        
        if uploaded_images:
            print(f"   已上传 {len(uploaded_images)} 张图片")
            
            # 修正图片路径
            content = fix_image_paths(content, assets_folder, uploaded_images)
        else:
            print("   无图片需要上传")
    else:
        print("\n📂 未找到 .assets 文件夹（可能文章无图片）")
    
    # 上传文章
    print("\n📤 上传文章...")
    github_path = f"content/posts/{slug}.md"
    content_base64 = base64.b64encode(content.encode('utf-8')).decode()
    
    if upload_to_github(github_path, content_base64, f"发布文章: {title}"):
        print("\n" + "=" * 50)
        print("🎉 发布成功!")
        print(f"📖 文章地址: {BLOG_URL}/{slug}/")
        print(f"⚙️  管理后台: {BLOG_URL}/admin/")
        return True
    
    return False


def main():
    if len(sys.argv) < 2:
        print("=" * 50)
        print("博客快速发布脚本")
        print("=" * 50)
        print("\n使用方法:")
        print("  python publish.py <markdown文件路径>")
        print("\n示例:")
        print('  python publish.py "D:\\\\教程\\\\Moviepilot手动刮削教程.md"')
        print("\n图片文件夹结构（Typora 默认）:")
        print("  D:\\教程\\")
        print("      ├── Moviepilot手动刮削教程.md")
        print("      └── Moviepilot手动刮削教程.assets\\")
        print("              ├── image-1.png")
        print("              └── image-2.png")
        print("\n首次使用请先修改脚本顶部的配置:")
        print("  - GITHUB_TOKEN: 你的 GitHub Personal Access Token")
        print("  - GITHUB_REPO: 你的 GitHub 仓库")
        print("  - BLOG_URL: 你的博客地址")
        print("\n依赖安装:")
        print("  pip install requests")
        sys.exit(1)
    
    md_file = sys.argv[1]
    publish_article(md_file)


if __name__ == "__main__":
    main()
