#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试步骤 5: 测试获取 Warp JWT Token
验证能否使用 Firebase refreshToken 获取 Warp JWT
"""

import httpx
import asyncio
import json
import base64
from datetime import datetime

# 配置
FIREBASE_API_KEY = "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs"
REFRESH_TOKEN = "your_refresh_token_from_step3"  # 从 step3 获取的 refreshToken
PROXY_URL = "http://127.0.0.1:7890"  # 如果需要代理


async def test_get_warp_jwt():
    """测试获取 Warp JWT Token"""
    print("="*60)
    print("测试 5: 获取 Warp JWT Token")
    print("="*60)
    print(f"测试时间: {datetime.now()}")
    print()

    # 尝试从文件加载 token
    if REFRESH_TOKEN == "your_refresh_token_from_step3":
        try:
            with open('test_register/tokens.json', 'r', encoding='utf-8') as f:
                tokens = json.load(f)
                refresh_token = tokens.get('refreshToken')
                print(f"✅ 从 tokens.json 加载 refreshToken")
        except:
            print("❌ 请先运行 step3 获取 refreshToken")
            print("或手动设置脚本中的 REFRESH_TOKEN 变量")
            return False
    else:
        refresh_token = REFRESH_TOKEN

    print(f"Refresh Token: {refresh_token[:50]}...")
    print()

    url = f"https://app.warp.dev/proxy/token?key={FIREBASE_API_KEY}"

    # 构建请求体
    payload = f"grant_type=refresh_token&refresh_token={refresh_token}"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-warp-client-version": "v0.2025.08.06.08.12.stable_02",
        "x-warp-os-category": "Windows",
        "x-warp-os-name": "Windows",
        "x-warp-os-version": "11 (26100)",
        "accept": "*/*",
        "accept-encoding": "gzip, br",
    }

    print(f"请求 URL: {url}")
    print(f"Payload: grant_type=refresh_token&refresh_token={refresh_token[:20]}...")
    print()

    # 尝试直连
    try:
        print("尝试: 直连...")
        async with httpx.AsyncClient(
            timeout=30.0,
            verify=False,
            headers=headers
        ) as client:
            response = await client.post(url, content=payload.encode('utf-8'))

            print(f"状态码: {response.status_code}")
            print(f"响应体: {response.text}")
            print()

            if response.status_code == 200:
                data = response.json()
                print("✅ 获取 Warp JWT 成功!")
                print("\nToken 信息:")
                print(f"  - access_token (Warp JWT): {data.get('access_token')[:50]}...")
                print(f"  - expires_in: {data.get('expires_in')} 秒")
                print(f"  - token_type: {data.get('token_type')}")
                print(f"  - refresh_token: {data.get('refresh_token')[:50]}...")

                # 解析 JWT payload
                jwt_token = data.get('access_token', '')
                try:
                    parts = jwt_token.split('.')
                    if len(parts) == 3:
                        payload_b64 = parts[1]
                        padding = 4 - len(payload_b64) % 4
                        if padding != 4:
                            payload_b64 += '=' * padding
                        payload_bytes = base64.urlsafe_b64decode(payload_b64)
                        payload_data = json.loads(payload_bytes.decode('utf-8'))

                        print("\nJWT Payload:")
                        print(f"  - iss (发行者): {payload_data.get('iss')}")
                        print(f"  - aud (受众): {payload_data.get('aud')}")
                        print(f"  - user_id: {payload_data.get('user_id')}")
                        print(f"  - email: {payload_data.get('email')}")
                        print(f"  - exp (过期时间): {payload_data.get('exp')}")
                        print(f"  - iat (签发时间): {payload_data.get('iat')}")

                        # 计算剩余有效时间
                        import time
                        exp_time = payload_data.get('exp', 0)
                        current_time = time.time()
                        remaining = exp_time - current_time
                        print(f"  - 剩余有效时间: {remaining/60:.1f} 分钟")
                except Exception as e:
                    print(f"\n⚠️  解析 JWT 失败: {e}")

                print("\n完整响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                # 保存 JWT
                with open('test_register/warp_jwt.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'access_token': data.get('access_token'),
                        'refresh_token': data.get('refresh_token'),
                        'expires_in': data.get('expires_in')
                    }, f, indent=2)
                print("\n✅ JWT 已保存到 test_register/warp_jwt.json")

                # 更新 .env 文件
                print("\n💡 提示: 你可以将此 JWT 设置到 .env 文件中的 WARP_JWT 变量")

                return True

            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
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
                response = await client.post(url, content=payload.encode('utf-8'))

                print(f"状态码: {response.status_code}")
                print(f"响应体: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    print("\n✅ 获取成功 (通过代理)!")
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
    print("#  Warp 注册测试 - 步骤 5: 获取 Warp JWT  #")
    print("#"*60 + "\n")

    print("⚠️  请先完成 step3 获取 refreshToken\n")

    input("按 Enter 键开始测试...")

    asyncio.run(test_get_warp_jwt())
