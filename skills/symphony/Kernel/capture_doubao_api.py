# -*- coding: utf-8 -*-
"""
豆包API流量捕获脚本
使用Playwright CDP连接浏览器，捕获豆包对话的API请求
"""
import asyncio
import json
import sys
from playwright.async_api import async_playwright

DOUBAO_URL = "https://www.doubao.com/chat/"
COOKIE_PATH = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/doubao_cookies.json"

async def load_cookies(context):
    """加载保存的cookies"""
    import os
    if os.path.exists(COOKIE_PATH):
        try:
            with open(COOKIE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 转换cookies格式以适配Playwright
                cookies = []
                for c in data:
                    cookie = {
                        'name': c['name'],
                        'value': c['value'],
                        'domain': c['domain'],
                        'path': c['path'],
                    }
                    if c.get('expires', -1) > 0:
                        cookie['expires'] = c['expires']
                    if c.get('httpOnly'):
                        cookie['httpOnly'] = c['httpOnly']
                    if c.get('secure'):
                        cookie['secure'] = c['secure']
                    cookies.append(cookie)
                await context.add_cookies(cookies)
                print(f"Loaded {len(cookies)} cookies")
        except Exception as e:
            print(f"Failed to load cookies: {e}")

async def capture_api_calls():
    """捕获豆包API调用"""
    api_calls = []
    
    async with async_playwright() as p:
        # 启动 Chromium（使用已有浏览器用户数据??        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--user-data-dir=C:\\Users\\Administrator\\.openclaw\\browser\\openclaw\\user-data'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        
        # 加载cookies
        await load_cookies(context)
        
        page = await context.new_page()
        
        # 捕获所有网络请??        def handle_request(request):
            url = request.url
            # 只关注API相关请求
            if 'doubao.com' in url or 'bytedance' in url or 'byted.org' in url:
                api_calls.append({
                    'url': url,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'post_data': request.post_data
                })
                print(f"[REQUEST] {request.method} {url[:100]}")
        
        def handle_response(response):
            url = response.url
            if 'doubao.com' in url or 'bytedance' in url or 'byted.org' in url:
                status = response.status
                print(f"[RESPONSE] {status} {url[:100]}")
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 访问豆包
        print(f"Navigating to {DOUBAO_URL}...")
        await page.goto(DOUBAO_URL, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        print("Page loaded")
        
        # 等待用户登录状??        await asyncio.sleep(2)
        
        # 找到输入框并发送消??        print("\n等待输入框就??..")
        try:
            input_box = await page.wait_for_selector(
                'textarea[placeholder*="发消??], textarea[placeholder*="技??]',
                timeout=10000
            )
            
            test_message = "你好，测试API捕获"
            await input_box.fill(test_message)
            print(f"Sent message: {test_message}")
            
            # 按Enter发??            await page.keyboard.press("Enter")
            print("Message sent, waiting for response...")
            
            # 等待响应
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Error interacting with page: {e}")
        
        # 保存捕获的API调用
        output_file = "doubao_api_capture.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(api_calls, f, ensure_ascii=False, indent=2)
        print(f"\nCaptured {len(api_calls)} API calls, saved to {output_file}")
        
        # 显示关键API端点
        print("\n=== Key API Endpoints ===")
        seen_urls = set()
        for call in api_calls:
            url = call['url']
            # 简化URL显示
            if '?' in url:
                base_url = url.split('?')[0]
            else:
                base_url = url
            if base_url not in seen_urls and ('api' in url.lower() or 'v1' in url.lower() or 'chat' in url.lower()):
                seen_urls.add(base_url)
                print(f"  {call['method']} {base_url}")
        
        await browser.close()
    
    return api_calls

if __name__ == "__main__":
    print("=" * 60)
    print("豆包API流量捕获工具")
    print("=" * 60)
    asyncio.run(capture_api_calls())
