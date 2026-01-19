"""
GitHub integration service.
Handles GitHub OAuth, repository operations, and API interactions.
"""

import os
import shutil
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

import httpx
from github import Github, GithubException
from git import Repo, GitCommandError

from app.core.config import settings
from app.core.redis import redis_client
from app.core.security import generate_random_string


class GitHubService:
    """Service for GitHub integration."""

    def __init__(self):
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_secret
        self.redirect_uri = settings.GITHUB_REDIRECT_URI
        self.scopes = settings.GITHUB_SCOPES

    async def generate_auth_url(self) -> Dict[str, str]:
        """
        Generate GitHub OAuth authorization URL.

        Returns:
            Dict containing auth_url and state
        """
        state = generate_random_string(16)

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": state,
            "allow_signup": "true"
        }

        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"

        # Store state in Redis for validation (30 minutes TTL)
        await redis_client.set(f"github_state:{state}", self.client_id, ttl=1800)

        return {
            "auth_url": auth_url,
            "state": state
        }

    async def exchange_code_for_token(
        self,
        code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub
            state: State parameter for CSRF validation

        Returns:
            Token response from GitHub
        """
        # Validate state
        stored_client_id = await redis_client.get(f"github_state:{state}")
        if not stored_client_id or stored_client_id != self.client_id:
            raise ValueError("Invalid state parameter")

        # Exchange code for token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri
                }
            )
            response.raise_for_status()
            token_data = response.json()

        if "error" in token_data:
            raise ValueError(f"GitHub auth error: {token_data.get('error_description', token_data['error'])}")

        # Clean up state
        await redis_client.delete(f"github_state:{state}")

        return token_data

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get GitHub user information.

        Args:
            access_token: GitHub access token

        Returns:
            User information from GitHub
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            response.raise_for_status()
            return response.json()

    async def list_user_repositories(
        self,
        access_token: str,
        page: int = 1,
        per_page: int = 30,
        sort: str = "updated",
        direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        List user's GitHub repositories.

        Args:
            access_token: GitHub access token
            page: Page number
            per_page: Items per page
            sort: Sort field (created, updated, pushed, full_name)
            direction: Sort direction (asc, desc)

        Returns:
            List of repository information
        """
        g = Github(access_token)
        user = g.get_user()

        repos = []
        for repo in user.get_repos(sort=sort, direction=direction):
            repos.append({
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "html_url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "default_branch": repo.default_branch,
                "private": repo.private,
                "fork": repo.fork,
                "archived": repo.archived,
                "language": repo.language,
                "stargazers_count": repo.stargazers_count,
                "forks_count": repo.forks_count,
                "watchers_count": repo.watchers_count,
                "open_issues_count": repo.open_issues_count,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
            })

            if len(repos) >= per_page * page:
                break

        start_idx = (page - 1) * per_page
        return repos[start_idx:start_idx + per_page]

    async def get_repository(
        self,
        access_token: str,
        owner: str,
        repo_name: str
    ) -> Dict[str, Any]:
        """
        Get repository information.

        Args:
            access_token: GitHub access token
            owner: Repository owner
            repo_name: Repository name

        Returns:
            Repository information
        """
        g = Github(access_token)
        repo = g.get_repo(f"{owner}/{repo_name}")

        return {
            "id": repo.id,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "html_url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
            "default_branch": repo.default_branch,
            "private": repo.private,
            "fork": repo.fork,
            "archived": repo.archived,
            "language": repo.language,
            "languages": dict(repo.get_languages()),
            "stargazers_count": repo.stargazers_count,
            "forks_count": repo.forks_count,
            "watchers_count": repo.watchers_count,
            "open_issues_count": repo.open_issues_count,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
        }

    def clone_repository(
        self,
        clone_url: str,
        local_path: str,
        access_token: str,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clone a GitHub repository to local storage.

        Args:
            clone_url: Repository clone URL
            local_path: Local path to clone to
            access_token: GitHub access token for authentication
            branch: Optional branch to clone

        Returns:
            Clone operation result
        """
        try:
            # Create directory if not exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Add token to URL for authentication
            auth_url = clone_url.replace(
                "https://",
                f"https://{access_token}@"
            )

            # Clone repository
            if branch:
                repo = Repo.clone_from(auth_url, local_path, branch=branch)
            else:
                repo = Repo.clone_from(auth_url, local_path)

            return {
                "status": "success",
                "local_path": local_path,
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha
            }
        except GitCommandError as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def pull_repository(self, local_path: str) -> Dict[str, Any]:
        """
        Pull latest changes from remote.

        Args:
            local_path: Local repository path

        Returns:
            Pull operation result
        """
        try:
            repo = Repo(local_path)
            origin = repo.remote("origin")
            pull_info = origin.pull()

            return {
                "status": "success",
                "commit": repo.head.commit.hexsha,
                "changes": len(pull_info)
            }
        except GitCommandError as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def create_branch(
        self,
        local_path: str,
        branch_name: str,
        base_branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new branch.

        Args:
            local_path: Local repository path
            branch_name: Name of new branch
            base_branch: Base branch to create from

        Returns:
            Branch creation result
        """
        try:
            repo = Repo(local_path)

            # Checkout base branch if specified
            if base_branch:
                repo.git.checkout(base_branch)

            # Create and checkout new branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()

            return {
                "status": "success",
                "branch": branch_name,
                "commit": repo.head.commit.hexsha
            }
        except GitCommandError as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def commit_changes(
        self,
        local_path: str,
        message: str,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Commit changes to repository.

        Args:
            local_path: Local repository path
            message: Commit message
            files: Optional list of files to commit (all if None)

        Returns:
            Commit result
        """
        try:
            repo = Repo(local_path)

            # Add files
            if files:
                repo.index.add(files)
            else:
                repo.git.add(A=True)

            # Commit
            commit = repo.index.commit(message)

            return {
                "status": "success",
                "commit_id": commit.hexsha,
                "message": message
            }
        except GitCommandError as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def push_changes(
        self,
        local_path: str,
        branch: Optional[str] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Push changes to remote.

        Args:
            local_path: Local repository path
            branch: Branch to push
            force: Force push

        Returns:
            Push result
        """
        try:
            repo = Repo(local_path)
            origin = repo.remote("origin")

            if branch:
                if force:
                    push_info = origin.push(branch, force=True)
                else:
                    push_info = origin.push(branch)
            else:
                if force:
                    push_info = origin.push(force=True)
                else:
                    push_info = origin.push()

            return {
                "status": "success",
                "branch": branch or repo.active_branch.name
            }
        except GitCommandError as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_file_content(
        self,
        local_path: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Get file content from repository.

        Args:
            local_path: Local repository path
            file_path: Path to file

        Returns:
            File content
        """
        full_path = os.path.join(local_path, file_path)
        if not os.path.exists(full_path):
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "status": "success",
                "content": content,
                "path": file_path
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def write_file(
        self,
        local_path: str,
        file_path: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Write content to a file.

        Args:
            local_path: Local repository path
            file_path: Path to file
            content: File content

        Returns:
            Write result
        """
        full_path = os.path.join(local_path, file_path)
        try:
            # Create directory if not exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "status": "success",
                "path": file_path
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def list_files(
        self,
        local_path: str,
        path: str = "",
        extensions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in repository.

        Args:
            local_path: Local repository path
            path: Subdirectory path
            extensions: Filter by file extensions

        Returns:
            List of file information
        """
        full_path = os.path.join(local_path, path)
        files = []

        for root, dirs, filenames in os.walk(full_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for filename in filenames:
                if filename.startswith("."):
                    continue

                if extensions:
                    ext = os.path.splitext(filename)[1]
                    if ext not in extensions:
                        continue

                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, local_path)

                files.append({
                    "name": filename,
                    "path": rel_path,
                    "size": os.path.getsize(file_path),
                    "is_dir": False
                })

        return files


# Global service instance
github_service = GitHubService()
