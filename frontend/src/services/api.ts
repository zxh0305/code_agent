/**
 * API service for backend communication
 */

const API_BASE = '/api/v1'

// Token management
export const tokenManager = {
  get: () => localStorage.getItem('github_access_token'),
  set: (token: string) => localStorage.setItem('github_access_token', token),
  remove: () => localStorage.removeItem('github_access_token'),
  hasToken: () => !!localStorage.getItem('github_access_token')
}

// Generic fetch wrapper with error handling
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token')

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options?.headers,
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }))
    throw new Error(error.message || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// GitHub API
export const githubApi = {
  // Get OAuth authorization URL
  getAuthUrl: () => request<{ auth_url: string; state: string }>('/github/auth'),

  // Exchange code for token
  exchangeToken: (code: string, state: string) =>
    request<{ access_token: string; token_type: string; scope: string }>('/github/token', {
      method: 'POST',
      body: JSON.stringify({ code, state }),
    }),

  // Get user info
  getUserInfo: () => {
    const token = tokenManager.get()
    if (!token) throw new Error('No GitHub token found')
    return request<any>(`/github/user?access_token=${token}`)
  },

  // Get user repositories
  getRepos: () => {
    const token = tokenManager.get()
    if (!token) throw new Error('No GitHub token found')
    return request<{ repositories: Repository[] }>(`/github/repos?access_token=${token}`)
  },

  // Get repository branches
  getBranches: (owner: string, repo: string) => {
    const token = tokenManager.get()
    if (!token) throw new Error('No GitHub token found')
    return request<{ branches: Branch[] }>(`/github/repos/${owner}/${repo}/branches?access_token=${token}`)
  },

  // Clone repository
  cloneRepo: (data: { owner: string; repo: string; branch?: string }) => {
    const token = tokenManager.get()
    if (!token) throw new Error('No GitHub token found')
    return request<{ message: string; path: string }>(`/github/repos/clone?access_token=${token}`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },
}

// Code Analysis API
export const codeApi = {
  // Analyze code
  analyze: (data: { code: string; language?: string }) =>
    request<CodeAnalysisResult>('/code/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Analyze file
  analyzeFile: (data: { file_path: string; repository_id?: number }) =>
    request<CodeAnalysisResult>('/code/analyze/file', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// LLM API
export const llmApi = {
  // Generate code
  generate: (data: GenerateCodeRequest) =>
    request<LLMResponse>('/llm/generate', {
      method: 'POST',
      body: JSON.stringify({
        prompt: data.prompt,
        language: data.language,
        context: data.context,
        use_local_llm: data.use_local_llm,
        provider: data.provider
      }),
    }),

  // Modify code
  modify: (data: ModifyCodeRequest) =>
    request<LLMResponse>('/llm/modify', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Review code
  review: (data: { code: string; language?: string }) =>
    request<LLMResponse>('/llm/review', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Fix bugs
  fix: (data: { code: string; error_message?: string }) =>
    request<LLMResponse>('/llm/fix', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// PR API
export const prApi = {
  // Create PR
  create: (data: CreatePRRequest) =>
    request<PRResponse>('/pr/create', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Get PR details
  get: (owner: string, repo: string, prNumber: number) =>
    request<PRResponse>(`/pr/${owner}/${repo}/${prNumber}`),

  // Merge PR
  merge: (data: { owner: string; repo: string; pr_number: number }) =>
    request<{ message: string }>('/pr/merge', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// Types
export interface Repository {
  id: number
  name: string
  full_name: string
  description: string | null
  html_url: string
  clone_url: string
  default_branch: string
  private: boolean  // 后端返回的是 private 不是 is_private
  is_private?: boolean  // 兼容字段
  language: string | null
  stars_count: number
  stargazers_count?: number  // 后端可能返回这个字段
  forks_count: number
}

export interface Branch {
  name: string
  commit: {
    sha: string
    url: string
  }
  protected: boolean
}

export interface CodeAnalysisResult {
  classes: any[]
  functions: any[]
  imports: string[]
  metrics: {
    lines_of_code: number
    complexity: number
  }
}

export interface GenerateCodeRequest {
  prompt: string
  language?: string
  context?: string
  use_local_llm?: boolean
  provider?: string  // Add provider field
}

export interface ModifyCodeRequest {
  code: string
  instruction: string
  language?: string
}

export interface LLMResponse {
  code?: string
  content: string
  model: string
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export interface CreatePRRequest {
  owner: string
  repo: string
  title: string
  body?: string
  head: string
  base: string
}

export interface PRResponse {
  id: number
  number: number
  title: string
  body: string | null
  state: string
  html_url: string
  created_at: string
  updated_at: string
}
