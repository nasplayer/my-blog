#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理未使用的图片
检查 static/images/ 下的图片，删除没有被任何文章引用的图片
"""

import sys
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============ 导入统一配置 ============
try:
    from config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH
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

def get_file_content(path):
    """获取文件内容"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    resp = SESSION.get(url, headers=get_headers())
    if resp.status_code == 200:
        import base64
        content = base64.b64decode(resp.json()['content']).decode('utf-8', errors='ignore')
        return content
    return None

def get_dir_contents(path):
    """获取目录内容"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    resp = SESSION.get(url, headers=get_headers())
    if resp.status_code == 200:
        return resp.json()
    return []

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

def get_all_images():
    """获取所有图片（递归）"""
    images = []
    
    def scan_dir(path):
        items = get_dir_contents(path)
        for item in items:
            if item['type'] == 'dir':
                scan_dir(item['path'])
            elif item['type'] == 'file':
                ext = item['name'].lower()
                if ext.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp')):
                    images.append({
                        'name': item['name'],
                        'path': item['path'],
                        'sha': item['sha'],
                    })
    
    scan_dir('static/images')
    return images

def get_all_articles():
    """获取所有文章"""
    articles = []
    items = get_dir_contents('content/posts')
    for item in items:
        if item['type'] == 'file' and item['name'].endswith('.md'):
            articles.append(item['path'])
    return articles

def main():
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        print("❌ 请先修改 GITHUB_TOKEN")
        return
    
    print("=" * 50)
    print("🗑️ 清理未使用的图片")
    print("=" * 50)
    
    # 1. 获取所有图片
    print("\n📂 获取所有图片...")
    all_images = get_all_images()
    print(f"   找到 {len(all_images)} 张图片")
    
    # 2. 获取所有文章
    print("\n📝 获取所有文章...")
    articles = get_all_articles()
    print(f"   找到 {len(articles)} 篇文章")
    
    # 3. 检查每张图片是否被引用
    print("\n🔍 检查图片引用...")
    used_images = set()
    
    for article_path in articles:
        content = get_file_content(article_path)
        if content:
            # 匹配 Markdown 图片 ![alt](/images/xxx)
            matches = re.findall(r'!\[.*?\]\((/images/[^)]+)\)', content)
            for match in matches:
                # /images/xxx/yyy.png -> static/images/xxx/yyy.png
                img_path = 'static' + match
                used_images.add(img_path)
            
            # 匹配 HTML 图片 <img src="/images/xxx">
            matches = re.findall(r'<img[^>]+src=["\'](/images/[^"\']+)["\']', content)
            for match in matches:
                img_path = 'static' + match
                used_images.add(img_path)
    
    print(f"   被引用的图片: {len(used_images)} 张")
    
    # 4. 找出未使用的图片
    unused_images = []
    for img in all_images:
        if img['path'] not in used_images:
            unused_images.append(img)
    
    print(f"   未使用的图片: {len(unused_images)} 张")
    
    if not unused_images:
        print("\n✅ 没有未使用的图片，无需清理")
        return
    
    # 5. 显示未使用的图片
    print("\n📋 未使用的图片列表:")
    for img in unused_images[:10]:  # 只显示前10个
        print(f"   - {img['path']}")
    if len(unused_images) > 10:
        print(f"   ... 还有 {len(unused_images) - 10} 张")
    
    # 6. 确认删除
    confirm = input(f"\n⚠️ 确认删除这 {len(unused_images)} 张图片? (y/n): ")
    
    if confirm.lower() != 'y':
        print("❌ 取消删除")
        return
    
    # 7. 删除
    print("\n🗑️ 删除图片...")
    deleted = 0
    for img in unused_images:
        if delete_file(img['path'], img['sha'], f"删除未使用的图片 {img['name']}"):
            print(f"  ✅ {img['name']}")
            deleted += 1
        else:
            print(f"  ❌ {img['name']}")
    
    print(f"\n🎉 删除完成: {deleted}/{len(unused_images)}")

if __name__ == "__main__":
    main()
