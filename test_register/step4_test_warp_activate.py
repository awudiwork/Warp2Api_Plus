#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试步骤 4: 测试 Warp GraphQL 激活接口
验证能否使用 Firebase idToken 激活 Warp 账号
"""

import httpx
import asyncio
import json
import uuid
from datetime import datetime

# 配置
ID_TOKEN = "your_id_token_from_step3"  # 从 step3 获取的 idToken
PROXY_URL = "http://127.0.0.1:7890"  # 如果需要代理


async def test_warp_graphql_activate():
    """测试 Warp GraphQL 激活用户"""
    print("="*60)
    print("测试 4: Warp GraphQL GetOrCreateUser 接口")
    print("="*60)
    print(f"测试时间: {datetime.now()}")
    print()

    # 尝试从文件加载 token
    if ID_TOKEN == "your_id_token_from_step3":
        try:
            with open('test_register/tokens.json', 'r', encoding='utf-8') as f:
                tokens = json.load(f)
                id_token = tokens.get('idToken')
                print(f"✅ 从 tokens.json 加载 idToken")
        except:
            print("❌ 请先运行 step3 获取 idToken")
            print("或手动设置脚本中的 ID_TOKEN 变量")
            return False
    else:
        id_token = ID_TOKEN

    print(f"ID Token: {id_token[:50]}...")
    print()

    url = "https://app.warp.dev/graphql/v2"
    session_id = str(uuid.uuid4())

    # GraphQL Query
    query = """mutation GetOrCreateUser($input: GetOrCreateUserInput!, $requestContext: RequestContext!) {
  getOrCreateUser(requestContext: $requestContext, input: $input) {
    __typename
    ... on GetOrCreateUserOutput {
      uid
      isOnboarded
      anonymousUserInfo {
        anonymousUserType
        linkedAt
        __typename
      }
      workspaces {
        joinableTeams {
          teamUid
          numMembers
          name
          teamAcceptingInvites
          __typename
        }
        __typename
      }
      onboardingSurveyStatus
      firstLoginAt
      adminOf
      deletedAnonymousUser
      __typename
    }
    ... on UserFacingError {
      error {
        __typename
        message
        ... on TOSViolationError {
          message
          __typename
        }
      }
      __typename
    }
  }
}
"""

    payload = {
        "operationName": "GetOrCreateUser",
        "variables": {
            "input": {
                "sessionId": session_id,
            },
            "requestContext": {
                "clientContext": {},
                "osContext": {},
            }
        },
        "query": query
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {id_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "referer": "https://app.warp.dev/login"
    }

    print(f"请求 URL: {url}")
    print(f"Operation: GetOrCreateUser")
    print(f"Session ID: {session_id}")
    print()

    # 尝试直连
    try:
        print("尝试: 直连...")
        async with httpx.AsyncClient(
            timeout=30.0,
            verify=False,
            headers=headers
        ) as client:
            response = await client.post(
                url,
                params={"op": "GetOrCreateUser"},
                json=payload
            )

            print(f"状态码: {response.status_code}")
            print(f"响应体: {response.text}")
            print()

            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {}).get('getOrCreateUser', {})

                typename = result.get('__typename')
                print(f"响应类型: {typename}")

                if typename == "GetOrCreateUserOutput":
                    print("\n✅ Warp 账号激活成功!")
                    print("\n账号信息:")
                    print(f"  - UID: {result.get('uid')}")
                    print(f"  - 是否已引导: {result.get('isOnboarded')}")
                    print(f"  - 引导状态: {result.get('onboardingSurveyStatus')}")
                    print(f"  - 首次登录: {result.get('firstLoginAt')}")

                    anonymous_info = result.get('anonymousUserInfo')
                    if anonymous_info:
                        print(f"  - 匿名用户类型: {anonymous_info.get('anonymousUserType')}")

                    print("\n完整响应:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))

                    # 保存用户信息
                    with open('test_register/warp_user.json', 'w', encoding='utf-8') as f:
                        json.dump({
                            'uid': result.get('uid'),
                            'isOnboarded': result.get('isOnboarded'),
                            'session_id': session_id
                        }, f, indent=2)
                    print("\n✅ 用户信息已保存到 test_register/warp_user.json")

                    return True

                elif typename == "UserFacingError":
                    error = result.get('error', {})
                    print(f"\n❌ 激活失败: {error.get('message')}")
                    print(f"错误类型: {error.get('__typename')}")

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
                response = await client.post(
                    url,
                    params={"op": "GetOrCreateUser"},
                    json=payload
                )

                print(f"状态码: {response.status_code}")
                print(f"响应体: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    print("\n✅ 激活成功 (通过代理)!")
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
    print("#  Warp 注册测试 - 步骤 4: Warp GraphQL 激活  #")
    print("#"*60 + "\n")

    print("⚠️  请先完成 step3 获取 idToken\n")

    input("按 Enter 键开始测试...")

    asyncio.run(test_warp_graphql_activate())
