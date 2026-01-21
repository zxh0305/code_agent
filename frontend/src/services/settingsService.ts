import axios from 'axios'

const API_BASE_URL = '/api/v1'

export interface SystemSettings {
  // GitHub OAuth
  github_client_id: string
  github_client_secret: string
  github_redirect_uri: string
  github_scopes: string

  // OpenAI
  openai_api_key: string
  openai_model: string
  openai_max_tokens: number
  openai_temperature: number

  // SiliconFlow
  siliconflow_api_key: string
  siliconflow_base_url: string
  siliconflow_model: string

  // Qwen
  qwen_api_key: string
  qwen_base_url: string
  qwen_model: string

  // Zhipu
  zhipu_api_key: string
  zhipu_base_url: string
  zhipu_model: string

  // Default LLM Provider
  default_llm_provider: string

  // Local LLM
  local_llm_enabled: boolean
  local_llm_url: string
  local_llm_model: string

  // JWT
  jwt_secret_key: string
  jwt_algorithm: string
  jwt_expire_minutes: number
}

export interface TestLLMProviderRequest {
  provider: string
  api_key?: string
  base_url?: string
  model?: string
}

export interface TestResult {
  success: boolean
  message?: string
}

class SettingsService {
  /**
   * 获取当前系统设置
   */
  async getSettings(): Promise<SystemSettings> {
    const response = await axios.get(`${API_BASE_URL}/settings`)
    return response.data.settings
  }

  /**
   * 保存系统设置
   */
  async saveSettings(settings: SystemSettings): Promise<void> {
    const response = await axios.post(`${API_BASE_URL}/settings`, settings)
    return response.data
  }

  /**
   * 测试GitHub OAuth连接
   */
  async testGithubConnection(clientId: string, clientsecret: string): Promise<TestResult> {
    try {
      const response = await axios.post(`${API_BASE_URL}/settings/test/github`, {
        client_id: clientId,
        client_secret: clientsecret,
      })
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '连接测试失败',
      }
    }
  }

  /**
   * 测试OpenAI API连接
   */
  async testOpenAIConnection(apiKey: string): Promise<TestResult> {
    try {
      const response = await axios.post(`${API_BASE_URL}/settings/test/openai`, {
        api_key: apiKey,
      })
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '连接测试失败',
      }
    }
  }

  async testLLMProvider(request: TestLLMProviderRequest): Promise<TestResult> {
    try {
      const response = await axios.post(`${API_BASE_URL}/settings/test/llm`, request)
      return response.data
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '连接测试失败',
      }
    }
  }
}

export const settingsService = new SettingsService()
