#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试步骤 3: 测试 signInWithEmailLink 接口
验证使用 oobCode 能否成功登录
"""

import httpx
import asyncio
import json
from datetime import datetime

# 配置
FIREBASE_API_KEY = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
TEST_EMAIL = "test@example.com"  # 替换为你的测试邮箱
OOB_CODE = "your_oob_code_from_email"  # 从邮件中提取的 oobCode
PROXY_URL = "http://127.0.0.1:7890"  # 如果需要代理


async def test_signin_with_email_link():
    """测试使用邮箱链接登录"""
    print("="*60)
    print("测试 3: Firebase signInWithEmailLink 接口")
    print("="*60)
    print(f"测试时间: {datetime.now()}")
    print(f"测试邮箱: {TEST_EMAIL}")
    print(f"OOB Code: {OOB_CODE[:20]}..." if len(OOB_CODE) > 20 else OOB_CODE)
    print()

    if OOB_CODE == "your_oob_code_from_email":
        print("❌ 请先从邮件中提取 oobCode 并设置到脚本中")
        print("\n提示: 运行 step1 和 step2 获取 oobCode")
        return False

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithEmailLink?key={FIREBASE_API_KEY}"

    payload = {
        "email": TEST_EMAIL,
        "oobCode": OOB_CODE
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*"
    }

    print(f"请求 URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()

    # 尝试直连
    try:
        print("尝试: 直连...")
        async with httpx.AsyncClient(
            timeout=30.0,
            verify=False,
            headers=headers
        ) as client:
            response = await client.post(url, json=payload)

            print(f"状态码: {response.status_code}")
            print(f"响应体: {response.text}")
            print()

            if response.status_code == 200:
                data = response.json()
                print("✅ 登录成功!")
                print("\n重要信息:")
                print(f"  - Email: {data.get('email')}")
                print(f"  - localId (Firebase UID): {data.get('localId')}")
                print(f"  - idToken: {data.get('idToken')[:50]}...")
                print(f"  - refreshToken: {data.get('refreshToken')[:50]}...")
                print(f"  - expiresIn: {data.get('expiresIn')} 秒")

                print("\n完整响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                # 保存 tokens 供下一步使用
                with open('test_register/tokens.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'email': data.get('email'),
                        'localId': data.get('localId'),
                        'idToken': data.get('idToken'),
                        'refreshToken': data.get('refreshToken')
                    }, f, indent=2)
                print("\n✅ Tokens 已保存到 test_register/tokens.json")

                return True
            else:
                print(f"❌ 登录失败: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")

                    # 分析常见错误
                    error_message = error_data.get('error', {}).get('message', '')
                    if 'EXPIRED' in error_message:
                        print("\n💡 提示: oobCode 已过期，请重新运行 step1 获取新的验证邮件")
                    elif 'INVALID' in error_message:
                        print("\n💡 提示: oobCode 无效，请检查是否复制完整")
                    elif 'EMAIL_NOT_FOUND' in error_message:
                        print("\n💡 提示: 邮箱未找到，请确认邮箱地址正确")
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
                response = await client.post(url, json=payload)

                print(f"状态码: {response.status_code}")
                print(f"响应体: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    print("\n✅ 登录成功 (通过代理)!")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    return True

        except Exception as e:
            print(f"❌ 代理异常: {type(e).__name__}: {e}")

    print("\n" + "="*60)
    print("❌ 测试失败")
    print("="*60)
    return False


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("#  Warp 注册测试 - 步骤 3: signInWithEmailLink  #")
    print("#"*60 + "\n")

    print("⚠️  请先完成 step1 和 step2，并设置:")
    print("   - TEST_EMAIL: 你的测试邮箱")
    print("   - OOB_CODE: 从邮件中提取的验证码\n")

    input("按 Enter 键开始测试...")

    asyncio.run(test_signin_with_email_link())
