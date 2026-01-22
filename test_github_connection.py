#!/usr/bin/env python3
"""
测试 GitHub 连接功能
"""
import asyncio
import sys
from app.services.github_service import github_service
from app.core.config import settings

async def test_github_connection():
    """测试 GitHub 连接功能"""
    print("=" * 60)
    print("GitHub 连接功能测试")
    print("=" * 60)

    # 1. 测试配置
    print("\n1. 检查配置...")
    print(f"   GitHub Client ID: {settings.GITHUB_CLIENT_ID[:10]}..." if settings.GITHUB_CLIENT_ID else "   ❌ GitHub Client ID 未配置")
    print(f"   GitHub Client Secret: {'已配置' if settings.GITHUB_CLIENT_secret else '❌ 未配置'}")
    print(f"   Redirect URI: {settings.GITHUB_REDIRECT_URI}")
    print(f"   Scopes: {settings.GITHUB_SCOPES}")

    if not settings.GITHUB_CLIENT_ID or settings.GITHUB_CLIENT_ID == "your_github_client_id":
        print("\n❌ GitHub OAuth 未配置，请先配置 .env 文件")
        return False

    # 2. 测试生成授权 URL
    print("\n2. 测试生成授权 URL...")
    try:
        result = await github_service.generate_auth_url()
        print(f"   ✅ 授权 URL 生成成功")
        print(f"   State: {result['state']}")
        print(f"   Auth URL: {result['auth_url'][:80]}...")
    except Exception as e:
        print(f"   ❌ 生成授权 URL 失败: {e}")
        return False

    # 3. 测试 GitHub API 连接（不需要 token）
    print("\n3. 测试 GitHub API 可访问性...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.github.com/zen", timeout=10.0)
            if response.status_code == 200:
                print(f"   ✅ GitHub API 可访问")
                print(f"   GitHub 禅: {response.text}")
            else:
                print(f"   ⚠️  GitHub API 返回状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ GitHub API 连接失败: {e}")
        return False

    # 4. 测试 Redis 连接（用于存储 state）
    print("\n4. 测试 Redis 连接...")
    try:
        from app.core.redis import redis_client
        test_key = "test:connection"
        await redis_client.set(test_key, "test_value", ttl=10)
        value = await redis_client.get(test_key)
        await redis_client.delete(test_key)
        if value == "test_value":
            print(f"   ✅ Redis 连接正常")
        else:
            print(f"   ⚠️  Redis 读写异常")
    except Exception as e:
        print(f"   ❌ Redis 连接失败: {e}")
        print(f"   注意: GitHub OAuth 功能需要 Redis 存储 state")

    print("\n" + "=" * 60)
    print("✅ GitHub 连接功能测试完成")
    print("=" * 60)
    print("\n说明:")
    print("1. 如果所有测试通过，GitHub 连接功能可以使用")
    print("2. 要完成 OAuth 流程，需要:")
    print("   - 访问授权 URL")
    print("   - 用户授权后获取 code")
    print("   - 使用 code 交换 access_token")
    print("3. 获取 token 后就可以使用所有 GitHub API 功能")

    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_github_connection())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
