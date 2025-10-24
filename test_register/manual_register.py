#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warp 手动注册测试脚本 (调试版本)
支持手动输入邮箱和验证码进行注册
会详细输出每一步的请求和响应信息,用于诊断注册问题
"""

import httpx
import asyncio
import json
from datetime import datetime
import sys
import os
import traceback

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import config
    PROXY_URL = config.PROXY_URL if hasattr(config, 'PROXY_URL') else None
except:
    PROXY_URL = None

# 配置
FIREBASE_API_KEYS = [
    # "AIzaSyBdy3O3S9hrdayLJxJ7mriBR4qgUaUygAs",  # 已被封禁 - API_KEY_SERVICE_BLOCKED
    "AIzaSyCivQFOIFf-cOLpzu3c9xXHSSHzZ8aJzBM",  # 尝试第二个
    "AIzaSyDmRQDJq4m-Ui2Ia4kLCqjfwl7PjE0rPSo"   # 尝试第三个
]
DEBUG = True  # 调试模式,输出详细信息


def log_debug(message, data=None):
    """输出调试信息"""
    if DEBUG:
        print(f"\n[DEBUG] {message}")
        if data:
            if isinstance(data, (dict, list)):
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(data)


class ManualRegister:
    """手动注册助手(调试版本)"""

    def __init__(self):
        self.email = None
        self.oob_code = None
        self.tokens = {}
        self.api_key_index = 0

    def get_next_api_key(self):
        """获取下一个 Firebase API Key"""
        key = FIREBASE_API_KEYS[self.api_key_index]
        self.api_key_index = (self.api_key_index + 1) % len(FIREBASE_API_KEYS)
        return key

    def get_headers(self):
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9"
        }

    async def send_verification_email(self, email: str) -> bool:
        """发送验证邮件"""
        print("\n" + "="*60)
        print("步骤 1: 发送验证邮件")
        print("="*60)
        print(f"邮箱: {email}")
        print(f"时间: {datetime.now()}")
        print()

        api_key = self.get_next_api_key()
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"

        payload = {
            "requestType": "EMAIL_SIGNIN",
            "email": email,
            "clientType": "CLIENT_TYPE_WEB",
            "continueUrl": "https://app.warp.dev/login",
            "canHandleCodeInApp": True
        }

        log_debug("请求 URL", url)
        log_debug("请求 Headers", self.get_headers())
        log_debug("请求 Payload", payload)
        if PROXY_URL:
            log_debug("使用代理", PROXY_URL)

        try:
            print("正在发送验证邮件...")
            client_kwargs = {
                "timeout": 30.0,
                "verify": False,
                "headers": self.get_headers()
            }
            if PROXY_URL:
                client_kwargs["proxy"] = PROXY_URL

            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.post(url, json=payload)

                print(f"\n状态码: {response.status_code}")
                log_debug("响应 Headers", dict(response.headers))
                log_debug("响应内容", response.text)

                if response.status_code == 200:
                    data = response.json()
                    print(f"\n✅ 验证邮件已发送到: {data.get('email', email)}")
                    log_debug("完整响应数据", data)
                    print("\n请检查邮箱(包括垃圾邮件文件夹),查找 Warp 发来的验证邮件")
                    self.email = email
                    return True
                else:
                    print(f"\n❌ 发送失败: HTTP {response.status_code}")
                    print(f"响应: {response.text}")
                    try:
                        error_data = response.json()
                        log_debug("错误详情", error_data)
                    except:
                        pass
                    return False

        except Exception as e:
            print(f"\n❌ 异常: {type(e).__name__}: {e}")
            if DEBUG:
                traceback.print_exc()
            return False

    async def signin_with_code(self, oob_code: str) -> bool:
        """使用验证码登录"""
        print("\n" + "="*60)
        print("步骤 2: 使用验证码登录 (signInWithEmailLink)")
        print("="*60)
        print(f"邮箱: {self.email}")
        print(f"验证码: {oob_code[:20]}..." if len(oob_code) > 20 else oob_code)
        print()

        api_key = self.get_next_api_key()
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithEmailLink?key={api_key}"

        payload = {
            "email": self.email,
            "oobCode": oob_code
        }

        log_debug("请求 URL", url)
        log_debug("请求 Headers", self.get_headers())
        log_debug("请求 Payload", payload)

        try:
            print("正在验证登录...")
            client_kwargs = {
                "timeout": 30.0,
                "verify": False,
                "headers": self.get_headers()
            }
            if PROXY_URL:
                client_kwargs["proxy"] = PROXY_URL

            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.post(url, json=payload)

                print(f"\n状态码: {response.status_code}")
                log_debug("响应 Headers", dict(response.headers))
                log_debug("响应内容", response.text)

                if response.status_code == 200:
                    data = response.json()
                    print("\n✅ Firebase 登录成功!")
                    log_debug("完整响应数据", data)

                    print("\n获取到的凭证:")
                    print(f"  - Email: {data.get('email')}")
                    print(f"  - Local ID: {data.get('localId')}")
                    print(f"  - ID Token: {data.get('idToken')[:50]}...")
                    print(f"  - Refresh Token: {data.get('refreshToken')[:50]}...")
                    if data.get('expiresIn'):
                        print(f"  - Expires In: {data.get('expiresIn')} 秒")

                    self.tokens = {
                        'email': data.get('email'),
                        'localId': data.get('localId'),
                        'idToken': data.get('idToken'),
                        'refreshToken': data.get('refreshToken'),
                        'expiresIn': data.get('expiresIn')
                    }

                    # 保存 tokens
                    tokens_file = os.path.join(os.path.dirname(__file__), 'tokens.json')
                    with open(tokens_file, 'w', encoding='utf-8') as f:
                        json.dump(self.tokens, f, indent=2)
                    print(f"\n✅ 凭证已保存到: {tokens_file}")

                    self.oob_code = oob_code
                    return True
                else:
                    print(f"\n❌ 登录失败: HTTP {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                        log_debug("错误响应数据", error_data)

                        error_message = error_data.get('error', {}).get('message', '')
                        if 'EXPIRED' in error_message:
                            print("\n💡 验证码已过期,请重新发送验证邮件")
                        elif 'INVALID' in error_message:
                            print("\n💡 验证码无效,请检查是否复制完整")
                        elif 'EMAIL_NOT_FOUND' in error_message:
                            print("\n💡 邮箱未找到,请检查邮箱地址")
                    except:
                        print(f"响应: {response.text}")
                    return False

        except Exception as e:
            print(f"\n❌ 异常: {type(e).__name__}: {e}")
            if DEBUG:
                traceback.print_exc()
            return False

    async def activate_warp_account(self) -> bool:
        """激活 Warp 账号"""
        print("\n" + "="*60)
        print("步骤 3: 激活 Warp 账号 (onboarding)")
        print("="*60)

        if not self.tokens.get('idToken'):
            print("❌ 没有有效的 ID Token,请先完成登录")
            return False

        url = "https://api.warp.dev/v1/auth/onboarding"

        headers = self.get_headers()
        headers['Authorization'] = f"Bearer {self.tokens['idToken']}"

        payload = {
            "accepted_tos": True,
            "accepted_privacy_policy": True,
            "accepted_community_guidelines": True
        }

        log_debug("请求 URL", url)
        log_debug("请求 Headers", headers)
        log_debug("请求 Payload", payload)

        try:
            print("正在激活账号...")
            client_kwargs = {
                "timeout": 30.0,
                "verify": False,
                "headers": headers
            }
            if PROXY_URL:
                client_kwargs["proxy"] = PROXY_URL

            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.post(url, json=payload)

                print(f"\n状态码: {response.status_code}")
                log_debug("响应 Headers", dict(response.headers))
                log_debug("响应内容", response.text)

                if response.status_code == 200:
                    print("\n✅ Warp 账号激活成功!")
                    try:
                        data = response.json()
                        log_debug("激活响应数据", data)
                    except:
                        pass
                    return True
                elif response.status_code == 409:
                    print("\n✅ 账号已经激活过了")
                    return True
                else:
                    print(f"\n❌ 激活失败: HTTP {response.status_code}")
                    print(f"响应: {response.text}")
                    try:
                        error_data = response.json()
                        log_debug("错误响应数据", error_data)
                    except:
                        pass
                    return False

        except Exception as e:
            print(f"\n❌ 异常: {type(e).__name__}: {e}")
            if DEBUG:
                traceback.print_exc()
            return False

    async def get_jwt_token(self) -> bool:
        """获取 JWT Token"""
        print("\n" + "="*60)
        print("步骤 4: 获取 JWT Token")
        print("="*60)

        if not self.tokens.get('idToken'):
            print("❌ 没有有效的 ID Token,请先完成登录")
            return False

        url = "https://api.warp.dev/v1/auth/tokens/id_token"

        headers = self.get_headers()
        headers['Authorization'] = f"Bearer {self.tokens['idToken']}"

        log_debug("请求 URL", url)
        log_debug("请求 Headers", headers)

        try:
            print("正在获取 JWT Token...")
            client_kwargs = {
                "timeout": 30.0,
                "verify": False,
                "headers": headers
            }
            if PROXY_URL:
                client_kwargs["proxy"] = PROXY_URL

            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.post(url)

                print(f"\n状态码: {response.status_code}")
                log_debug("响应 Headers", dict(response.headers))
                log_debug("响应内容", response.text)

                if response.status_code == 200:
                    data = response.json()
                    jwt_token = data.get('jwt_token')
                    if jwt_token:
                        print("\n✅ JWT Token 获取成功!")
                        print(f"JWT Token: {jwt_token[:50]}...")
                        log_debug("完整 JWT Token", jwt_token)

                        self.tokens['jwt_token'] = jwt_token

                        # 更新保存的 tokens
                        tokens_file = os.path.join(os.path.dirname(__file__), 'tokens.json')
                        with open(tokens_file, 'w', encoding='utf-8') as f:
                            json.dump(self.tokens, f, indent=2)
                        print(f"\n✅ JWT Token 已保存")
                        return True
                    else:
                        print("\n❌ 响应中没有 jwt_token")
                        log_debug("完整响应数据", data)
                        return False
                else:
                    print(f"\n❌ 获取失败: HTTP {response.status_code}")
                    print(f"响应: {response.text}")
                    try:
                        error_data = response.json()
                        log_debug("错误响应数据", error_data)
                    except:
                        pass
                    return False

        except Exception as e:
            print(f"\n❌ 异常: {type(e).__name__}: {e}")
            if DEBUG:
                traceback.print_exc()
            return False


async def main():
    """主函数"""
    global PROXY_URL

    print("\n" + "#"*60)
    print("#" + " "*15 + "Warp 手动注册助手 (调试版本)" + " "*15 + "#")
    print("#"*60)
    print()
    print("此脚本将帮助你手动完成 Warp 账号注册流程")
    print("你需要手动输入邮箱和验证码")
    print()
    print("⚠️  调试模式已启用,将显示详细的请求和响应信息")
    print()

    # 询问是否使用代理
    if PROXY_URL:
        print(f"检测到配置的代理: {PROXY_URL}")
        use_proxy = input("是否使用代理? (y/n，默认 n): ").strip().lower()
        if use_proxy != 'y':
            print("✅ 已禁用代理，将使用直连")
            PROXY_URL = None
        else:
            print(f"✅ 将使用代理: {PROXY_URL}")
    else:
        print("⚠️  未配置代理，将使用直连")
    print()

    register = ManualRegister()

    # 步骤 1: 输入邮箱并发送验证邮件
    print("\n" + "="*60)
    print("第 1 步: 输入邮箱地址")
    print("="*60)
    email = input("\n请输入你的邮箱地址: ").strip()

    if not email:
        print("❌ 邮箱地址不能为空")
        return

    success = await register.send_verification_email(email)
    if not success:
        print("\n❌ 发送验证邮件失败,请检查邮箱地址和网络连接")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. 需要配置代理")
        print("  3. Firebase API Key 失效")
        return

    # 步骤 2: 输入验证码
    print("\n" + "="*60)
    print("第 2 步: 输入验证码")
    print("="*60)
    print("\n请打开邮箱,找到 Warp 发来的验证邮件")
    print("\n发件人可能是:")
    print("  - noreply@warp.dev")
    print("  - noreply@firebase.com")
    print("\n邮件主题可能是:")
    print("  - Sign in to Warp")
    print("  - Warp sign-in link")
    print("\n邮件中有一个链接,类似:")
    print("  https://...firebaseapp.com/__/auth/action?...&oobCode=XXXXX&...")
    print("\n请复制 oobCode= 后面的整个验证码(不包括 & 符号)")
    print("验证码通常很长,请确保完整复制")
    print()

    oob_code = input("请输入验证码 (oobCode): ").strip()

    if not oob_code:
        print("❌ 验证码不能为空")
        return

    success = await register.signin_with_code(oob_code)
    if not success:
        print("\n❌ 登录失败")
        print("\n可能的原因:")
        print("  1. 验证码已过期 (通常 5-10 分钟有效)")
        print("  2. 验证码复制不完整")
        print("  3. 邮箱地址与验证码不匹配")
        print("\n请重新运行脚本并确保快速完成验证")
        return

    # 步骤 3: 激活 Warp 账号
    success = await register.activate_warp_account()
    if not success:
        print("\n❌ 激活账号失败")
        print("\n这一步失败可能是因为:")
        print("  1. ID Token 无效或已过期")
        print("  2. Warp API 服务问题")
        print("  3. 网络连接问题")
        return

    # 步骤 4: 获取 JWT Token
    success = await register.get_jwt_token()
    if not success:
        print("\n⚠️  获取 JWT Token 失败")
        print("\n账号已经激活,但 JWT Token 获取失败")
        print("可以稍后使用 refresh_token 重新获取")
        # 不返回,继续显示完成信息

    # 完成
    print("\n" + "="*60)
    print("✅ 注册流程完成!")
    print("="*60)
    print("\n所有凭证已保存到 test_register/tokens.json")
    print("\n账号信息:")
    print(f"  邮箱: {register.tokens.get('email')}")
    print(f"  Local ID: {register.tokens.get('localId')}")
    if register.tokens.get('idToken'):
        print(f"  ID Token: {register.tokens.get('idToken')[:50]}...")
    if register.tokens.get('refreshToken'):
        print(f"  Refresh Token: {register.tokens.get('refreshToken')[:50]}...")
    if register.tokens.get('jwt_token'):
        print(f"  JWT Token: {register.tokens.get('jwt_token')[:50]}...")
    print()
    print("\n你可以使用这些凭证来对比原注册代码的输出")
    print("找出原代码在哪一步出现了问题")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n\n❌ 程序异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
