#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除文章脚本
删除文章同时删除相关图片
"""

import sys
import re
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============ 导入统一配置 ============
try:
    from config import (
        GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH,
        BLOG_URL, MAX_RETRIES, RETRY_DELAY
    )
except ImportError:
    print("❌ 请先创建 config.py 配置文件")
    sys.exit(1)

API_BASE = "https://api.github.com"

def create_session():
    session = requests.Session()
    retry_strategy = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session

SESSION = create_session()

def get_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

def get_dir_contents(path):
    """获取目录内容"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    resp = SESSION.get(url, headers=get_headers())
    if resp.status_code == 200:
        return resp.json()
    return []

def get_file_content(path):
    """获取文件内容"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    resp = SESSION.get(url, headers=get_headers())
    if resp.status_code == 200:
        import base64
        return base64.b64decode(resp.json()['content']).decode('utf-8', errors='ignore')
    return None

def delete_file(path, sha, message):
    """删除文件"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"
    data = {
        "message": message,
        "branch": GITHUB_BRANCH,
        "sha": sha,
    }
    resp = SESSION.delete(url, headers=get_headers(), json=data)
    return resp.status_code == 200

def list_articles():
    """列出所有文章"""
    print("=" * 50)
    print("📝 已发布的文章")
    print("=" * 50)
    
    articles = get_dir_contents('content/posts')
    md_files = [f for f in articles if f['name'].endswith('.md')]
    
    if not md_files:
        print("暂无文章")
        return []
    
    for i, f in enumerate(md_files, 1):
        # 获取文章标题
        content = get_file_content(f['path'])
        title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE) if content else None
        title = title_match.group(1).strip() if title_match else f['name']
        
        # 检查是否置顶
        is_pinned = 'pinned: true' in content if content else False
        pin_mark = "📌 " if is_pinned else "   "
        
        print(f"{pin_mark}{i}. {title}")
        print(f"      文件: {f['name']}")
    
    return md_files

def delete_article(slug):
    """删除文章和相关图片"""
    # 查找文章
    articles = get_dir_contents('content/posts')
    target = None
    
    for article in articles:
        if article['name'].endswith('.md'):
            # 检查文件名或slug
            if slug in article['name'] or slug in article['path']:
                target = article
                break
    
    if not target:
        print(f"❌ 未找到文章: {slug}")
        return False
    
    # 获取文章内容，提取图片
    content = get_file_content(target['path'])
    title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE) if content else None
    title = title_match.group(1).strip() if title_match else target['name']
    
    print(f"\n📝 文章: {title}")
    print(f"   文件: {target['path']}")
    
    # 提取图片路径
    images_to_delete = []
    if content:
        # 匹配 /images/xxx/yyy.png
        matches = re.findall(r'/images/([^\s\)]+)', content)
        for match in matches:
            img_path = f"static/images/{match}"
            images_to_delete.append(img_path)
    
    if images_to_delete:
        print(f"   图片: {len(images_to_delete)} 张")
        for img in images_to_delete:
            print(f"      - {img}")
    
    # 确认删除
    confirm = input(f"\n⚠️ 确认删除文章和 {len(images_to_delete)} 张图片? (y/n): ")
    
    if confirm.lower() != 'y':
        print("❌ 取消删除")
        return False
    
    # 删除图片
    deleted_images = 0
    for img_path in images_to_delete:
        img_info = get_dir_contents('/'.join(img_path.split('/')[:-1]))
        img_name = img_path.split('/')[-1]
        for img in img_info:
            if img['name'] == img_name:
                if delete_file(img['path'], img['sha'], f"删除图片 {img_name}"):
                    print(f"  ✅ 已删除图片: {img_name}")
                    deleted_images += 1
                break
    
    # 删除文章
    if delete_file(target['path'], target['sha'], f"删除文章: {title}"):
        print(f"  ✅ 已删除文章: {title}")
        print(f"\n🎉 删除完成: 文章 1 篇, 图片 {deleted_images} 张")
        return True
    
    return False

def main():
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        print("❌ 请先修改 GITHUB_TOKEN")
        return
    
    articles = list_articles()
    
    if not articles:
        return
    
    print("\n" + "=" * 50)
    print("输入文章编号或文件名删除文章")
    print("输入 'q' 退出")
    print("=" * 50)
    
    while True:
        user_input = input("\n请输入: ").strip()
        
        if user_input.lower() == 'q':
            break
        
        # 尝试按编号删除
        try:
            index = int(user_input)
            if 1 <= index <= len(articles):
                slug = articles[index - 1]['name'].replace('.md', '')
                delete_article(slug)
            else:
                print("❌ 编号无效")
        except ValueError:
            # 按文件名删除
            delete_article(user_input)

if __name__ == "__main__":
    main()
