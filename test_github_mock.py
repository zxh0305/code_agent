#!/usr/bin/env python3
"""
GitHub 连接功能单元测试（模拟测试，不需要真实凭证）
"""
import asyncio
import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock

async def test_github_service_methods():
    """测试 GitHub service 的各个方法"""
    print("=" * 60)
    print("GitHub 连接功能单元测试")
    print("=" * 60)

    all_passed = True

    # 测试 1: 测试生成授权 URL 功能
    print("\n[测试 1] 测试生成授权 URL...")
    try:
        from app.services.github_service import GitHubService

        # 创建一个测试用的 service 实例
        service = GitHubService()
        service.client_id = "test_client_id"
        service.client_secret = "test_secret"
        service.redirect_uri = "http://localhost:8082/callback"
        service.scopes = "repo,user"

        # Mock Redis
        with patch('app.services.github_service.redis_client') as mock_redis:
            mock_redis.set = AsyncMock()
            result = await service.generate_auth_url()

            assert 'auth_url' in result
            assert 'state' in result
            assert 'github.com/login/oauth/authorize' in result['auth_url']
            assert 'test_client_id' in result['auth_url']
            print("   ✅ 生成授权 URL 功能正常")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        all_passed = False

    # 测试 2: 测试 token 交换功能（模拟）
    print("\n[测试 2] 测试 token 交换功能...")
    try:
        from app.services.github_service import GitHubService
        import httpx

        service = GitHubService()
        service.client_id = "test_client_id"
        service.client_secret = "test_secret"

        # Mock Redis 和 HTTP 请求
        with patch('app.services.github_service.redis_client') as mock_redis, \
             patch('httpx.AsyncClient') as mock_client:

            # 模拟 Redis 返回
            mock_redis.get = AsyncMock(return_value="test_client_id")
            mock_redis.delete = AsyncMock()

            # 模拟 HTTP 响应
            mock_response = Mock()
            mock_response.json.return_value = {
                "access_token": "test_token",
                "token_type": "bearer",
                "scope": "repo,user"
            }
            mock_response.raise_for_status = Mock()

            mock_client_instance = AsyncMock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await service.exchange_code_for_token("test_code", "test_state")

            assert result.get('access_token') == "test_token"
            print("   ✅ Token 交换功能正常")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        all_passed = False

    # 测试 3: 测试获取用户信息功能
    print("\n[测试 3] 测试获取用户信息功能...")
    try:
        from app.services.github_service import GitHubService

        service = GitHubService()

        with patch('httpx.AsyncClient') as mock_client:
            # 模拟 HTTP 响应
            mock_response = Mock()
            mock_response.json.return_value = {
                "login": "testuser",
                "id": 12345,
                "name": "Test User"
            }
            mock_response.raise_for_status = Mock()

            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await service.get_user_info("test_token")

            assert result.get('login') == "testuser"
            print("   ✅ 获取用户信息功能正常")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        all_passed = False

    # 测试 4: 测试 Git 操作功能
    print("\n[测试 4] 测试 Git 操作功能...")
    try:
        from app.services.github_service import GitHubService

        service = GitHubService()

        # 测试克隆功能（模拟）
        with patch('app.services.github_service.Repo') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo_instance.active_branch.name = "main"
            mock_repo_instance.head.commit.hexsha = "abc123"
            mock_repo.clone_from.return_value = mock_repo_instance

            result = service.clone_repository(
                "https://github.com/test/repo.git",
                "/tmp/test_repo",
                "test_token"
            )

            assert result['status'] == 'success'
            print("   ✅ 克隆仓库功能正常")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        all_passed = False

    # 测试 5: 测试文件操作功能
    print("\n[测试 5] 测试文件操作功能...")
    try:
        from app.services.github_service import GitHubService
        import tempfile
        import os

        service = GitHubService()

        # 创建临时目录测试
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            test_content = "Hello, GitHub!"

            # 测试写文件
            result = service.write_file(tmpdir, "test.txt", test_content)
            assert result['status'] == 'success'

            # 测试读文件
            result = service.get_file_content(tmpdir, "test.txt")
            assert result['status'] == 'success'
            assert result['content'] == test_content

            print("   ✅ 文件读写功能正常")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        all_passed = False

    # 测试 6: 测试 API 路由
    print("\n[测试 6] 测试 API 路由定义...")
    try:
        from app.api.github_routes import router

        routes = [route.path for route in router.routes]
        expected_routes = ['/auth', '/callback', '/token', '/user', '/repos']

        for expected in expected_routes:
            matching = [r for r in routes if expected in r]
            assert len(matching) > 0, f"缺少路由: {expected}"

        print("   ✅ API 路由定义完整")
        print(f"   总共定义了 {len(routes)} 个路由")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过 - GitHub 连接功能正常")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(test_github_service_methods())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
