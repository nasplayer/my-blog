#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理旧图片 - 删除 static/images/ 目录下所有图片
"""

import sys
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

def main():
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        print("❌ 请先修改 GITHUB_TOKEN")
        return
    
    print("📂 获取图片列表...")
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/static/images?ref={GITHUB_BRANCH}"
    resp = SESSION.get(url, headers=get_headers())
    
    if resp.status_code != 200:
        print(f"❌ 获取失败: {resp.text}")
        return
    
    files = resp.json()
    print(f"   找到 {len(files)} 个文件")
    
    # 过滤出图片文件
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'}
    images = [f for f in files if any(f['name'].endswith(ext) for ext in image_extensions)]
    
    print(f"   其中 {len(images)} 张图片")
    
    if not images:
        print("✅ 没有图片需要删除")
        return
    
    print("\n🗑️ 删除图片...")
    deleted = 0
    for img in images:
        if delete_file(img['path'], img['sha'], f"删除图片 {img['name']}"):
            print(f"  ✅ {img['name']}")
            deleted += 1
        else:
            print(f"  ❌ {img['name']}")
    
    print(f"\n🎉 删除完成: {deleted}/{len(images)}")

if __name__ == "__main__":
    main()
