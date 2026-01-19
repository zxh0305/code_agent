"""
Pull Request management service.
Handles PR creation, updates, and lifecycle management.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from github import Github, GithubException

from app.core.config import settings


class PullRequestService:
    """Service for managing GitHub Pull Requests."""

    def __init__(self):
        pass

    def create_pull_request(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        draft: bool = False,
        reviewers: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        issue_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new Pull Request.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch
            draft: Create as draft PR
            reviewers: List of reviewer usernames
            labels: List of labels
            issue_number: Related issue number

        Returns:
            PR creation result
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")

            # Check if head branch exists
            try:
                repo.get_branch(head_branch)
            except GithubException as e:
                if e.status == 404:
                    return {
                        "status": "error",
                        "message": f"Branch '{head_branch}' does not exist"
                    }
                raise

            # Create PR body with issue link if provided
            full_body = body
            if issue_number:
                full_body += f"\n\nRelated to #{issue_number}"

            # Create the PR
            pr = repo.create_pull(
                title=title,
                body=full_body,
                head=head_branch,
                base=base_branch,
                draft=draft
            )

            # Add reviewers if specified
            if reviewers:
                try:
                    pr.create_review_request(reviewers=reviewers)
                except GithubException:
                    pass  # Ignore if reviewers can't be added

            # Add labels if specified
            if labels:
                try:
                    pr.add_to_labels(*labels)
                except GithubException:
                    pass  # Ignore if labels can't be added

            return {
                "status": "success",
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "title": pr.title,
                "state": pr.state,
                "head_branch": head_branch,
                "base_branch": base_branch,
                "created_at": pr.created_at.isoformat()
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_pull_request(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """
        Get Pull Request details.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number

        Returns:
            PR details
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")
            pr = repo.get_pull(pr_number)

            return {
                "status": "success",
                "pr": {
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "state": pr.state,
                    "html_url": pr.html_url,
                    "head_branch": pr.head.ref,
                    "base_branch": pr.base.ref,
                    "user": pr.user.login,
                    "draft": pr.draft,
                    "mergeable": pr.mergeable,
                    "mergeable_state": pr.mergeable_state,
                    "commits": pr.commits,
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                    "changed_files": pr.changed_files,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                    "closed_at": pr.closed_at.isoformat() if pr.closed_at else None
                }
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }

    def list_pull_requests(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        base_branch: Optional[str] = None,
        head_branch: Optional[str] = None,
        page: int = 1,
        per_page: int = 30
    ) -> Dict[str, Any]:
        """
        List Pull Requests in a repository.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            state: PR state (open, closed, all)
            sort: Sort field
            direction: Sort direction
            base_branch: Filter by base branch
            head_branch: Filter by head branch
            page: Page number
            per_page: Items per page

        Returns:
            List of PRs
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")

            prs = repo.get_pulls(
                state=state,
                sort=sort,
                direction=direction,
                base=base_branch,
                head=head_branch
            )

            result_prs = []
            start_idx = (page - 1) * per_page
            for i, pr in enumerate(prs):
                if i < start_idx:
                    continue
                if i >= start_idx + per_page:
                    break

                result_prs.append({
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "html_url": pr.html_url,
                    "head_branch": pr.head.ref,
                    "base_branch": pr.base.ref,
                    "user": pr.user.login,
                    "draft": pr.draft,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else None
                })

            return {
                "status": "success",
                "pull_requests": result_prs,
                "page": page,
                "per_page": per_page
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }

    def update_pull_request(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        base_branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a Pull Request.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            title: New title
            body: New body
            state: New state (open, closed)
            base_branch: New base branch

        Returns:
            Updated PR details
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")
            pr = repo.get_pull(pr_number)

            # Update fields
            update_kwargs = {}
            if title is not None:
                update_kwargs["title"] = title
            if body is not None:
                update_kwargs["body"] = body
            if state is not None:
                update_kwargs["state"] = state
            if base_branch is not None:
                update_kwargs["base"] = base_branch

            if update_kwargs:
                pr.edit(**update_kwargs)

            return {
                "status": "success",
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "message": "PR updated successfully"
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }

    def merge_pull_request(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
        merge_method: str = "merge"  # merge, squash, rebase
    ) -> Dict[str, Any]:
        """
        Merge a Pull Request.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            commit_title: Merge commit title
            commit_message: Merge commit message
            merge_method: Merge method

        Returns:
            Merge result
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")
            pr = repo.get_pull(pr_number)

            # Check if mergeable
            if not pr.mergeable:
                return {
                    "status": "error",
                    "message": f"PR is not mergeable. State: {pr.mergeable_state}"
                }

            # Merge PR
            merge_result = pr.merge(
                commit_title=commit_title,
                commit_message=commit_message,
                merge_method=merge_method
            )

            return {
                "status": "success",
                "merged": merge_result.merged,
                "sha": merge_result.sha,
                "message": merge_result.message
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }

    def add_comment(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        body: str
    ) -> Dict[str, Any]:
        """
        Add a comment to a Pull Request.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            body: Comment body

        Returns:
            Comment creation result
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")
            pr = repo.get_pull(pr_number)

            comment = pr.create_issue_comment(body)

            return {
                "status": "success",
                "comment_id": comment.id,
                "html_url": comment.html_url,
                "created_at": comment.created_at.isoformat()
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }

    def get_pr_files(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """
        Get files changed in a Pull Request.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number

        Returns:
            List of changed files
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")
            pr = repo.get_pull(pr_number)

            files = []
            for f in pr.get_files():
                files.append({
                    "filename": f.filename,
                    "status": f.status,
                    "additions": f.additions,
                    "deletions": f.deletions,
                    "changes": f.changes,
                    "patch": f.patch,
                    "blob_url": f.blob_url,
                    "raw_url": f.raw_url
                })

            return {
                "status": "success",
                "files": files,
                "total": len(files)
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }

    def create_review(
        self,
        access_token: str,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",  # APPROVE, REQUEST_CHANGES, COMMENT
        comments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a review on a Pull Request.

        Args:
            access_token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            body: Review body
            event: Review event type
            comments: List of review comments

        Returns:
            Review creation result
        """
        try:
            g = Github(access_token)
            repo = g.get_repo(f"{repo_owner}/{repo_name}")
            pr = repo.get_pull(pr_number)

            review = pr.create_review(
                body=body,
                event=event,
                comments=comments or []
            )

            return {
                "status": "success",
                "review_id": review.id,
                "state": review.state,
                "html_url": review.html_url
            }

        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "error_code": e.status
            }


# Global service instance
pr_service = PullRequestService()
