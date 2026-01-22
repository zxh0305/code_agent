"""
LLM (Large Language Model) service.
Handles AI-powered code generation, modification, and analysis.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.core.config import settings


@dataclass
class LLMResponse:
    """LLM response structure."""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str


class PromptTemplates:
    """Collection of prompt templates for different tasks."""

    CODE_GENERATION = """You are an expert software developer. Generate high-quality, production-ready code based on the following requirements.

Requirements:
{requirements}

Context (existing code structure):
{context}

Language: {language}

Please generate code that:
1. Follows best practices and coding standards for {language}
2. Is well-documented with appropriate comments
3. Handles edge cases and errors appropriately
4. Is efficient and maintainable

Generate ONLY the code, without explanations unless specifically asked."""

    CODE_MODIFICATION = """You are an expert software developer. Modify the following code according to the requirements.

Original Code:
```{language}
{original_code}
```

Modification Requirements:
{requirements}

Code Structure Context:
{context}

Please provide the modified code that:
1. Implements the requested changes
2. Maintains existing functionality unless explicitly asked to change it
3. Follows the existing code style and conventions
4. Includes appropriate comments explaining significant changes

Return ONLY the complete modified code."""

    CODE_REVIEW = """You are an expert code reviewer. Review the following code and provide constructive feedback.

Code to Review:
```{language}
{code}
```

Focus on:
1. Code quality and readability
2. Potential bugs or issues
3. Performance considerations
4. Security concerns
5. Best practices and coding standards

Provide your review in the following format:
- Summary: Brief overview of the code quality
- Issues: List of identified issues (severity: high/medium/low)
- Suggestions: Recommended improvements
- Positive Aspects: What's done well"""

    BUG_FIX = """You are an expert debugger. Analyze the following code and fix any bugs.

Buggy Code:
```{language}
{code}
```

Error/Issue Description:
{error_description}

Stack Trace (if available):
{stack_trace}

Please:
1. Identify the root cause of the bug
2. Provide the fixed code
3. Explain what was wrong and how you fixed it

Return the fixed code with comments explaining the fix."""

    DOCUMENTATION_GENERATION = """You are a technical writer. Generate comprehensive documentation for the following code.

Code:
```{language}
{code}
```

Generate documentation that includes:
1. Overview/Purpose
2. Function/Class descriptions
3. Parameter descriptions
4. Return value descriptions
5. Usage examples
6. Any important notes or warnings

Use appropriate documentation format for {language} (docstrings, JSDoc, etc.)."""

    PR_DESCRIPTION = """Generate a professional Pull Request description based on the following changes.

Changed Files:
{changed_files}

Commit Messages:
{commit_messages}

Generate a PR description with:
1. Summary of changes (2-3 sentences)
2. Detailed list of changes
3. Testing instructions (if applicable)
4. Any breaking changes or migration notes

Format the description in Markdown."""

    COMMIT_MESSAGE = """Generate a professional commit message for the following changes.

Changed Files:
{changed_files}

Diff Summary:
{diff_summary}

Generate a commit message following conventional commits format:
<type>(<scope>): <subject>

<body>

Types: feat, fix, docs, style, refactor, test, chore
Keep the subject line under 50 characters.
Explain what and why in the body if needed."""


class LLMService:
    """Service for LLM interactions with multiple providers."""

    def __init__(self):
        self.providers = {
            "openai": {
                "api_key": settings.OPENAI_API_KEY,
                "base_url": None,
                "model": settings.OPENAI_MODEL
            },
            "siliconflow": {
                "api_key": getattr(settings, "SILICONFLOW_API_KEY", ""),
                "base_url": getattr(settings, "SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
                "model": getattr(settings, "SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3")
            },
            "qwen": {
                "api_key": getattr(settings, "QWEN_API_KEY", ""),
                "base_url": getattr(settings, "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                "model": getattr(settings, "QWEN_MODEL", "qwen-plus")
            },
            "zhipu": {
                "api_key": getattr(settings, "ZHIPU_API_KEY", ""),
                "base_url": getattr(settings, "ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
                "model": getattr(settings, "ZHIPU_MODEL", "glm-4")
            },
            "local": {
                "api_key": None,
                "base_url": settings.LOCAL_LLM_URL,
                "model": settings.LOCAL_LLM_MODEL
            }
        }
        self.default_provider = getattr(settings, "DEFAULT_LLM_PROVIDER", "openai")
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

    def _get_client(self, provider: Optional[str] = None) -> OpenAI:
        """Get OpenAI client for specified provider."""
        provider = provider or self.default_provider
        config = self.providers.get(provider, self.providers["openai"])

        if provider == "local":
            return OpenAI(
                base_url=config["base_url"],
                api_key="not-needed",
                timeout=120.0  # 2 minutes timeout
            )
        return OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],
            timeout=120.0  # 2 minutes timeout
        )

    def _get_async_client(self, provider: Optional[str] = None) -> AsyncOpenAI:
        """Get async OpenAI client for specified provider."""
        provider = provider or self.default_provider
        config = self.providers.get(provider, self.providers["openai"])

        if provider == "local":
            if not config["base_url"]:
                raise ValueError("LOCAL_LLM_URL is not configured. Please set LOCAL_LLM_URL in .env file or use a different provider.")
            return AsyncOpenAI(
                base_url=config["base_url"],
                api_key="not-needed"
            )
        
        # Validate API key for non-local providers
        if not config["api_key"] or config["api_key"] in ["your_openai_api_key", "your_api_key", ""]:
            raise ValueError(
                f"API key for provider '{provider}' is not configured. "
                f"Please set {provider.upper()}_API_KEY in .env file with a valid API key."
            )
        
        return AsyncOpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],
            timeout=120.0  # 2 minutes timeout
        )

    def _get_model(self, provider: Optional[str] = None) -> str:
        """Get model name for specified provider."""
        provider = provider or self.default_provider
        config = self.providers.get(provider, self.providers["openai"])
        return config["model"]

    def _parse_response(self, response: ChatCompletion) -> LLMResponse:
        """Parse OpenAI response into LLMResponse."""
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            finish_reason=response.choices[0].finish_reason or "stop"
        )

    def generate_code(
        self,
        requirements: str,
        language: str = "python",
        context: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code based on requirements.

        Args:
            requirements: Code requirements description
            language: Programming language
            context: Existing code context
            provider: LLM provider to use (openai, siliconflow, qwen, zhipu, local)

        Returns:
            Generated code and metadata
        """
        try:
            prompt = PromptTemplates.CODE_GENERATION.format(
                requirements=requirements,
                context=context or "No existing context provided",
                language=language
            )

            client = self._get_client(provider)
            model = self._get_model(provider)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            result = self._parse_response(response)

            return {
                "status": "success",
                "code": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def generate_code_async(
        self,
        requirements: str,
        language: str = "python",
        context: Optional[str] = None,
        use_local: bool = False,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code based on requirements (async version).

        Args:
            requirements: Code requirements description
            language: Programming language
            context: Existing code context
            provider: LLM provider to use (openai, siliconflow, qwen, zhipu, local)
        Returns:
            Generated code and metadata
        """
        try:
            prompt = PromptTemplates.CODE_GENERATION.format(
                requirements=requirements,
                context=context or "No existing context provided",
                language=language
            )

            client = self._get_async_client(provider)
            model = self._get_model(provider)
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            result = self._parse_response(response)
            return {
                "status": "success",
                "code": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def modify_code(
        self,
        original_code: str,
        requirements: str,
        language: str = "python",
        context: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify existing code based on requirements.

        Args:
            original_code: Original code to modify
            requirements: Modification requirements
            language: Programming language
            context: Additional context
            provider: LLM provider to use

        Returns:
            Modified code and metadata
        """
        try:
            prompt = PromptTemplates.CODE_MODIFICATION.format(
                original_code=original_code,
                requirements=requirements,
                language=language,
                context=context or "No additional context"
            )

            client = self._get_client(provider)
            model = self._get_model(provider)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            result = self._parse_response(response)

            # Extract code from response (remove markdown code blocks if present)
            code = result.content
            if code.startswith("```"):
                lines = code.split("\n")
                code = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

            return {
                "status": "success",
                "code": code,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def review_code(
        self,
        code: str,
        language: str = "python",
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Review code and provide feedback.

        Args:
            code: Code to review
            language: Programming language
            provider: LLM provider to use

        Returns:
            Code review results
        """
        try:
            prompt = PromptTemplates.CODE_REVIEW.format(
                code=code,
                language=language
            )

            client = self._get_client(provider)
            model = self._get_model(provider)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more consistent reviews
            )

            result = self._parse_response(response)

            return {
                "status": "success",
                "review": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def fix_bug(
        self,
        code: str,
        error_description: str,
        language: str = "python",
        stack_trace: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fix bugs in code.

        Args:
            code: Buggy code
            error_description: Description of the error
            language: Programming language
            stack_trace: Stack trace if available
            provider: LLM provider to use

        Returns:
            Fixed code and explanation
        """
        try:
            prompt = PromptTemplates.BUG_FIX.format(
                code=code,
                error_description=error_description,
                language=language,
                stack_trace=stack_trace or "Not provided"
            )

            client = self._get_client(provider)
            model = self._get_model(provider)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert debugger."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )

            result = self._parse_response(response)

            return {
                "status": "success",
                "fixed_code": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def generate_documentation(
        self,
        code: str,
        language: str = "python",
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate documentation for code.

        Args:
            code: Code to document
            language: Programming language
            provider: LLM provider to use

        Returns:
            Generated documentation
        """
        try:
            prompt = PromptTemplates.DOCUMENTATION_GENERATION.format(
                code=code,
                language=language
            )

            client = self._get_client(provider)
            model = self._get_model(provider)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a technical writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )

            result = self._parse_response(response)

            return {
                "status": "success",
                "documentation": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def generate_pr_description(
        self,
        changed_files: List[str],
        commit_messages: List[str],
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate PR description.

        Args:
            changed_files: List of changed file paths
            commit_messages: List of commit messages
            provider: LLM provider to use

        Returns:
            Generated PR description
        """
        try:
            prompt = PromptTemplates.PR_DESCRIPTION.format(
                changed_files="\n".join(f"- {f}" for f in changed_files),
                commit_messages="\n".join(f"- {m}" for m in commit_messages)
            )

            client = self._get_client(provider)
            model = self._get_model(provider)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert at writing clear, concise PR descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.5
            )

            result = self._parse_response(response)

            return {
                "status": "success",
                "description": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def generate_commit_message(
        self,
        changed_files: List[str],
        diff_summary: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate commit message.

        Args:
            changed_files: List of changed file paths
            diff_summary: Summary of changes
            provider: LLM provider to use

        Returns:
            Generated commit message
        """
        try:
            prompt = PromptTemplates.COMMIT_MESSAGE.format(
                changed_files="\n".join(f"- {f}" for f in changed_files),
                diff_summary=diff_summary
            )

            client = self._get_client(provider)
            model = self._get_model(provider)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You write clear, conventional commit messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=256,
                temperature=0.3
            )

            result = self._parse_response(response)

            return {
                "status": "success",
                "message": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        General chat with LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            provider: LLM provider to use

        Returns:
            Chat response
        """
        try:
            client = self._get_async_client(provider)
            model = self._get_model(provider)

            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            response = await client.chat.completions.create(
                model=model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            result = self._parse_response(response)

            return {
                "status": "success",
                "response": result.content,
                "model": result.model,
                "tokens": {
                    "prompt": result.prompt_tokens,
                    "completion": result.completion_tokens,
                    "total": result.total_tokens
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Global service instance
llm_service = LLMService()
