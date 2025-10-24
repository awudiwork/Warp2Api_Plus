#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试步骤 1: 测试 Firebase sendOobCode 接口
验证是否能成功发送邮箱验证链接
"""

import httpx
import asyncio
import json
from datetime import datetime

# 配置
FIREBASE_API_KEY = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
TEST_EMAIL = "test@example.com"  # 替换为你的测试邮箱
PROXY_URL = "http://127.0.0.1:7890"  # 如果需要代理


async def test_send_oob_code():
    """测试发送验证码"""
    print("="*60)
    print("测试 1: Firebase sendOobCode 接口")
    print("="*60)
    print(f"测试时间: {datetime.now()}")
    print(f"测试邮箱: {TEST_EMAIL}")
    print()

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"

    # 测试不同的 payload 配置
    test_cases = [
        {
            "name": "标准配置 (原有配置)",
            "payload": {
                "requestType": "EMAIL_SIGNIN",
                "email": TEST_EMAIL,
                "clientType": "CLIENT_TYPE_WEB",
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True
            }
        },
        {
            "name": "简化配置 (去掉 clientType)",
            "payload": {
                "requestType": "EMAIL_SIGNIN",
                "email": TEST_EMAIL,
                "continueUrl": "https://app.warp.dev/login",
                "canHandleCodeInApp": True
            }
        },
        {
            "name": "最简配置",
            "payload": {
                "requestType": "EMAIL_SIGNIN",
                "email": TEST_EMAIL,
                "continueUrl": "https://app.warp.dev/login"
            }
        },
    ]

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # 测试每个配置
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[测试 {i}/{len(test_cases)}] {test_case['name']}")
        print("-"*60)
        print(f"Payload: {json.dumps(test_case['payload'], indent=2)}")
        print()

        try:
            # 尝试不使用代理
            print("尝试: 直连...")
            async with httpx.AsyncClient(
                timeout=30.0,
                verify=False,
                headers=headers
            ) as client:
                response = await client.post(url, json=test_case['payload'])

                print(f"✅ 状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                print(f"响应体: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"\n✅ 成功! 邮件已发送到 {data.get('email', TEST_EMAIL)}")
                    print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    return True
                else:
                    print(f"\n❌ 失败: HTTP {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    except:
                        pass

        except Exception as e:
            print(f"❌ 异常: {type(e).__name__}: {e}")

        # 如果直连失败，尝试使用代理
        if PROXY_URL:
            try:
                print(f"\n尝试: 使用代理 {PROXY_URL}...")
                async with httpx.AsyncClient(
                    timeout=30.0,
                    verify=False,
                    proxies=PROXY_URL,
                    headers=headers
                ) as client:
                    response = await client.post(url, json=test_case['payload'])

                    print(f"✅ 状态码: {response.status_code}")
                    print(f"响应体: {response.text}")

                    if response.status_code == 200:
                        data = response.json()
                        print(f"\n✅ 成功! 邮件已发送到 {data.get('email', TEST_EMAIL)}")
                        return True

            except Exception as e:
                print(f"❌ 代理异常: {type(e).__name__}: {e}")

    print("\n" + "="*60)
    print("❌ 所有测试配置都失败了")
    print("="*60)
    return False


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("#  Warp 注册测试 - 步骤 1: Firebase sendOobCode  #")
    print("#"*60 + "\n")

    # 提示用户修改邮箱
    print("⚠️  请先修改脚本中的 TEST_EMAIL 为你的真实测试邮箱!")
    print("⚠️  如果需要代理，请设置 PROXY_URL\n")

    input("按 Enter 键开始测试...")

    asyncio.run(test_send_oob_code())
