#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试步骤 2: 测试邮件接收和验证链接提取
验证能否从邮箱中获取验证链接和 oobCode
"""

import asyncio
import re
from urllib.parse import urlparse, parse_qs
import html

# 配置
TEST_EMAIL = "test@example.com"  # 替换为你的测试邮箱
OUTLOOK_ACCESS_TOKEN = "your_access_token"  # 从 Outlook API 获取


async def test_extract_verification_link():
    """测试验证链接提取"""
    print("="*60)
    print("测试 2: 验证链接提取")
    print("="*60)
    print()

    # 模拟不同格式的邮件内容
    test_emails = [
        {
            "name": "标准 Firebase 邮件格式",
            "content": '''
            <html>
            <body>
                <a href="https://astral-field-294621.firebaseapp.com/__/auth/action?apiKey=AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs&amp;mode=signIn&amp;oobCode=ABC123XYZ456&amp;continueUrl=https://app.warp.dev/login&amp;lang=en">
                    Click here to sign in
                </a>
            </body>
            </html>
            '''
        },
        {
            "name": "新格式邮件 (如果 Warp 更改了)",
            "content": '''
            <html>
            <body>
                <a href="https://app.warp.dev/auth/verify?oobCode=TEST789ABC&apiKey=AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs">
                    Verify Email
                </a>
            </body>
            </html>
            '''
        },
    ]

    # 测试各种正则表达式
    patterns = [
        ("标准 Firebase 链接", r'href=["\'](https://[^"\']*firebaseapp\.com[^"\']*)["\']'),
        ("Warp 直接链接", r'href=["\'](https://app\.warp\.dev[^"\']*oobCode[^"\']*)["\']'),
        ("任何包含 oobCode 的链接", r'(https://[^\s<>]+\?.*oobCode=[^"\'\s<>]+)'),
        ("Auth Action 链接", r'https://[^"\'\s<>]*__/auth/action[^"\'\s<>]*'),
    ]

    print("测试链接提取正则表达式...\n")

    for email_case in test_emails:
        print(f"\n{'='*60}")
        print(f"测试邮件: {email_case['name']}")
        print(f"{'='*60}\n")

        found = False
        for pattern_name, pattern in patterns:
            print(f"尝试正则: {pattern_name}")
            print(f"  Pattern: {pattern}")

            matches = re.findall(pattern, email_case['content'], re.IGNORECASE)

            if matches:
                print(f"  ✅ 找到 {len(matches)} 个匹配")
                for i, match in enumerate(matches, 1):
                    # 清理链接
                    verification_link = html.unescape(match)
                    verification_link = verification_link.replace('&amp;', '&')

                    print(f"\n  匹配 {i}: {verification_link[:100]}...")

                    # 尝试提取 oobCode
                    parsed = urlparse(verification_link)
                    params = parse_qs(parsed.query)
                    oob_code = params.get('oobCode', [None])[0]

                    if oob_code:
                        print(f"  ✅ 成功提取 oobCode: {oob_code}")
                        print(f"  完整链接: {verification_link}")
                        found = True
                        break
                    else:
                        print(f"  ❌ 未找到 oobCode 参数")
            else:
                print(f"  ❌ 无匹配")

            if found:
                break

        if not found:
            print(f"\n❌ 该邮件格式无法提取验证链接")

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


async def test_microsoft_graph_api():
    """测试 Microsoft Graph API 获取邮件"""
    print("\n" + "="*60)
    print("测试 3: Microsoft Graph API")
    print("="*60)
    print()

    if OUTLOOK_ACCESS_TOKEN == "your_access_token":
        print("⚠️  请先设置 OUTLOOK_ACCESS_TOKEN")
        print("可以通过以下方式获取:")
        print("1. 使用 Outlook API 注册并获取 access_token")
        print("2. 或临时跳过此测试")
        return

    import httpx

    url = "https://graph.microsoft.com/v1.0/me/messages"
    headers = {
        'Authorization': f'Bearer {OUTLOOK_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'Prefer': 'outlook.body-content-type="html"'
    }

    params = {
        '$filter': "contains(subject, 'Warp')",
        '$top': 5,
        '$select': 'id,subject,from,body,receivedDateTime'
    }

    print(f"请求 URL: {url}")
    print(f"过滤条件: {params['$filter']}")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                messages = data.get('value', [])

                print(f"✅ 找到 {len(messages)} 封邮件\n")

                for i, message in enumerate(messages, 1):
                    print(f"邮件 {i}:")
                    print(f"  主题: {message.get('subject')}")
                    print(f"  发件人: {message.get('from', {}).get('emailAddress', {}).get('address')}")
                    print(f"  时间: {message.get('receivedDateTime')}")

                    # 尝试提取验证链接
                    body_content = message.get('body', {}).get('content', '')
                    if 'oobCode' in body_content or 'warp' in body_content.lower():
                        print(f"  ✅ 邮件可能包含验证链接")
                        print(f"  内容片段: {body_content[:200]}...")
                    print()

            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")

    except Exception as e:
        print(f"❌ 异常: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("#  Warp 注册测试 - 步骤 2: 邮件接收与链接提取  #")
    print("#"*60 + "\n")

    print("此测试将验证:")
    print("1. 验证链接提取的正则表达式是否正确")
    print("2. Microsoft Graph API 是否能正常获取邮件\n")

    input("按 Enter 键开始测试...")

    asyncio.run(test_extract_verification_link())
    asyncio.run(test_microsoft_graph_api())
