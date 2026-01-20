/**
 * API service for backend communication
 */

const API_BASE = '/api/v1'

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
    throw new Error(error.message || error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// GitHub API
export const githubApi = {
  // Get OAuth authorization URL
  getAuthUrl: () => request<{ auth_url: string }>('/github/auth'),

  // Get user repositories
  getRepos: (accessToken?: string) => {
    const params = accessToken ? `?access_token=${accessToken}` : ''
    return request<{ repositories: Repository[] }>(`/github/repos${params}`)
  },

  // Get repository branches
  getBranches: (owner: string, repo: string, accessToken?: string) => {
    const params = accessToken ? `?access_token=${accessToken}` : ''
    return request<{ branches: Branch[] }>(`/github/repos/${owner}/${repo}/branches${params}`)
  },

  // Clone repository
  cloneRepo: (data: { owner: string; repo: string; branch?: string }) =>
    request<{ message: string; path: string }>('/github/repos/clone', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// Task API
export const taskApi = {
  // Create task
  create: (data: TaskCreate) =>
    request<Task>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // List tasks
  list: (params?: { page?: number; per_page?: number; status?: string; is_archived?: boolean }) => {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.set('page', String(params.page))
    if (params?.per_page) searchParams.set('per_page', String(params.per_page))
    if (params?.status) searchParams.set('status', params.status)
    if (params?.is_archived !== undefined) searchParams.set('is_archived', String(params.is_archived))
    const query = searchParams.toString()
    return request<Task[]>(`/tasks${query ? `?${query}` : ''}`)
  },

  // Get task
  get: (taskId: number) => request<Task>(`/tasks/${taskId}`),

  // Update task
  update: (taskId: number, data: TaskUpdate) =>
    request<Task>(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Rename task
  rename: (taskId: number, name: string) =>
    request<{ status: string; name: string }>(`/tasks/${taskId}/rename?name=${encodeURIComponent(name)}`, {
      method: 'PATCH',
    }),

  // Archive task
  archive: (taskId: number) =>
    request<{ status: string }>(`/tasks/${taskId}/archive`, { method: 'PATCH' }),

  // Unarchive task
  unarchive: (taskId: number) =>
    request<{ status: string }>(`/tasks/${taskId}/unarchive`, { method: 'PATCH' }),

  // Delete task
  delete: (taskId: number) =>
    request<{ status: string }>(`/tasks/${taskId}`, { method: 'DELETE' }),
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
      body: JSON.stringify(data),
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
export interface Task {
  id: number
  name: string
  description: string | null
  repository: string | null
  branch: string | null
  requirement: string | null
  generated_code: string | null
  language: string | null
  status: string
  is_archived: boolean
  metadata: Record<string, any> | null
  created_at: string | null
  updated_at: string | null
}

export interface TaskCreate {
  name?: string
  description?: string
  repository?: string
  branch?: string
  requirement?: string
  language?: string
}

export interface TaskUpdate {
  name?: string
  description?: string
  repository?: string
  branch?: string
  requirement?: string
  generated_code?: string
  language?: string
  status?: string
  is_archived?: boolean
  metadata?: Record<string, any>
}

export interface Repository {
  id: number
  name: string
  full_name: string
  description: string | null
  html_url: string
  clone_url: string
  default_branch: string
  private: boolean
  language: string | null
  stargazers_count: number
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
