import { useState, useEffect, useCallback } from 'react'
import {
  Card,
  Typography,
  Input,
  Button,
  Select,
  Space,
  Row,
  Col,
  Divider,
  message,
  Spin,
  Alert,
  Tag,
  Tooltip,
  Badge,
  Collapse,
} from 'antd'
import {
  GithubOutlined,
  ReloadOutlined,
  SendOutlined,
  BranchesOutlined,
  FolderOutlined,
  CodeOutlined,
  LinkOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  RobotOutlined,
  DatabaseOutlined,
  DisconnectOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons'
import { githubApi, llmApi, Repository, Branch, tokenManager } from '../services/api'
import { settingsService } from '../services/settingsService'
import UsageGuide from '../components/UsageGuide'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input
const { Option } = Select

// 提供商名称映射
const providerNames: Record<string, string> = {
  openai: 'OpenAI',
  siliconflow: '硅基流动',
  qwen: '千问',
  zhipu: '智谱',
  local: '本地LLM'
}

function Develop() {
  // State for requirement input
  const [requirement, setRequirement] = useState('')
  const [generating, setGenerating] = useState(false)
  const [generatedCode, setGeneratedCode] = useState('')
  const [showGuide, setShowGuide] = useState(true)

  // State for GitHub connection
  const [isConnected, setIsConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [repos, setRepos] = useState<Repository[]>([])
  const [branches, setBranches] = useState<Branch[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null)
  const [selectedBranch, setSelectedBranch] = useState<string | null>(null)
  const [repoLoading, setRepoLoading] = useState(false)
  const [branchLoading, setBranchLoading] = useState(false)

  // State for current settings
  const [currentModel, setCurrentModel] = useState<string>('gpt-4o')
  const [currentProvider, setCurrentProvider] = useState<string>('openai')

  // Check GitHub connection status
  const checkConnection = useCallback(async () => {
    if (!tokenManager.hasToken()) {
      setIsConnected(false)
      setRepos([])
      return
    }

    try {
      setLoading(true)
      const response = await githubApi.getRepos()
      setRepos(response.repositories || [])
      setIsConnected(true)
    } catch (error) {
      console.error('Failed to check GitHub connection:', error)
      setIsConnected(false)
      setRepos([])
      // 如果 token 失效,清除 token
      if (error instanceof Error && error.message.includes('token')) {
        tokenManager.remove()
      }
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    checkConnection()
    loadCurrentSettings()
  }, [checkConnection])

  // Load current settings
  const loadCurrentSettings = async () => {
    try {
      const settings = await settingsService.getSettings()
      const provider = settings.default_llm_provider || 'openai'

      // 设置当前提供商
      setCurrentProvider(provider)

      // 根据提供商设置对应的模型
      switch (provider) {
        case 'openai':
          setCurrentModel(settings.openai_model || 'gpt-4o')
          break
        case 'siliconflow':
          setCurrentModel(settings.siliconflow_model || 'deepseek-ai/DeepSeek-V3')
          break
        case 'qwen':
          setCurrentModel(settings.qwen_model || 'qwen-plus')
          break
        case 'zhipu':
          setCurrentModel(settings.zhipu_model || 'glm-4')
          break
        case 'local':
          setCurrentModel(settings.local_llm_model || 'codellama')
          break
        default:
          setCurrentModel('gpt-4o')
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  // Refresh repositories
  const refreshRepos = async () => {
    if (!tokenManager.hasToken()) {
      message.warning('请先连接 GitHub')
      return
    }

    try {
      setRepoLoading(true)
      const response = await githubApi.getRepos()
      setRepos(response.repositories || [])
      setIsConnected(true)
      message.success('仓库列表已刷新')
    } catch (error: any) {
      message.error(error.message || '刷新仓库列表失败')
      setIsConnected(false)
    } finally {
      setRepoLoading(false)
    }
  }

  // Handle repository selection
  const handleRepoSelect = async (value: string) => {
    setSelectedRepo(value)
    setSelectedBranch(null)
    setBranches([])

    if (!value) return

    const [owner, repo] = value.split('/')
    try {
      setBranchLoading(true)
      const response = await githubApi.getBranches(owner, repo)
      setBranches(response.branches || [])

      // Auto-select default branch
      const selectedRepoData = repos.find((r) => r.full_name === value)
      if (selectedRepoData?.default_branch) {
        const defaultBranch = response.branches.find(
          (b) => b.name === selectedRepoData.default_branch
        )
        if (defaultBranch) {
          setSelectedBranch(defaultBranch.name)
        }
      }
    } catch (error: any) {
      message.error(error.message || '获取分支列表失败')
    } finally {
      setBranchLoading(false)
    }
  }

  // Refresh branches
  const refreshBranches = async () => {
    if (!selectedRepo) {
      message.warning('请先选择仓库')
      return
    }

    const [owner, repo] = selectedRepo.split('/')
    try {
      setBranchLoading(true)
      const response = await githubApi.getBranches(owner, repo)
      setBranches(response.branches || [])
      message.success('分支列表已刷新')
    } catch (error: any) {
      message.error(error.message || '刷新分支列表失败')
    } finally {
      setBranchLoading(false)
    }
  }

  // Connect to GitHub
  const connectGitHub = async () => {
    try {
      const { auth_url } = await githubApi.getAuthUrl()
      window.location.href = auth_url
    } catch (error: any) {
      message.error(error.message || '获取GitHub授权链接失败')
    }
  }

  // Disconnect GitHub
  const disconnectGitHub = () => {
    tokenManager.remove()
    setIsConnected(false)
    setRepos([])
    setBranches([])
    setSelectedRepo(null)
    setSelectedBranch(null)
    message.success('已断开 GitHub 连接')
  }

  // Analyze code from requirement
  const handleAnalyze = async () => {
    if (!requirement.trim()) {
      message.warning('请输入代码需求描述')
      return
    }

    try {
      setGenerating(true)
      const response = await llmApi.analyzeCode({
        source_code: requirement,
      })
      setGeneratedCode(response.code || response.analysis || "分析完成")
      message.success('代码分析成功')
    } catch (error: any) {
      message.error(error.message || '代码分析失败')
    } finally {
      setGenerating(false)
    }
  }

  // Get selected repo info
  const selectedRepoInfo = repos.find((r) => r.full_name === selectedRepo)

  return (
    <div style={{ padding: '24px', marginLeft: 220 }}>
      {/* Current Context Bar */}
      <Card
        style={{
          marginBottom: 24,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          borderRadius: 12,
        }}
      >
        <Row gutter={16} align="middle" justify="space-between">
          <Col>
            <Space size="large">
              <Badge
                count={<RobotOutlined />}
                style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
              >
                <div style={{ color: '#fff', fontSize: 14 }}>
                  <Text style={{ color: '#fff', fontSize: 12, opacity: 0.8 }}>AI模型:</Text>
                  <div style={{ fontSize: 16, fontWeight: 'bold', marginTop: 4 }}>
                    {providerNames[currentProvider] || currentProvider} - {currentModel}
                  </div>
                </div>
              </Badge>

              <Badge
                count={isConnected ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                style={{
                  backgroundColor: isConnected
                    ? 'rgba(82, 196, 26, 0.8)'
                    : 'rgba(255, 77, 79, 0.8)',
                }}
              >
                <div style={{ color: '#fff', fontSize: 14 }}>
                  <Text style={{ color: '#fff', fontSize: 12, opacity: 0.8 }}>GitHub:</Text>
                  <div style={{ fontSize: 16, fontWeight: 'bold', marginTop: 4 }}>
                    {isConnected ? '已连接' : '未连接'}
                  </div>
                </div>
              </Badge>

              {selectedRepo && (
                <Badge
                  count={<DatabaseOutlined />}
                  style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
                >
                  <div style={{ color: '#fff', fontSize: 14 }}>
                    <Text style={{ color: '#fff', fontSize: 12, opacity: 0.8 }}>仓库:</Text>
                    <div style={{ fontSize: 16, fontWeight: 'bold', marginTop: 4 }}>
                      {selectedRepo}
                    </div>
                  </div>
                </Badge>
              )}

              {selectedBranch && (
                <Badge
                  count={<BranchesOutlined />}
                  style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
                >
                  <div style={{ color: '#fff', fontSize: 14 }}>
                    <Text style={{ color: '#fff', fontSize: 12, opacity: 0.8 }}>分支:</Text>
                    <div style={{ fontSize: 16, fontWeight: 'bold', marginTop: 4 }}>
                      {selectedBranch}
                    </div>
                  </div>
                </Badge>
              )}
            </Space>
          </Col>
          <Col>
            <Space>
              {isConnected && (
                <Button
                  type="primary"
                  danger
                  ghost
                  icon={<DisconnectOutlined />}
                  onClick={disconnectGitHub}
                >
                  断开连接
                </Button>
              )}
              <Button
                type="primary"
                ghost
                icon={<ReloadOutlined />}
                onClick={() => {
                  checkConnection()
                  loadCurrentSettings()
                }}
              >
                刷新状态
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      <Title level={2}>
        <CodeOutlined style={{ marginRight: 12 }} />
        代码分析
      </Title>
      <Paragraph style={{ fontSize: 16, color: '#666' }}>
        输入您的代码，AI将为您分析代码结构、函数、类等。
      </Paragraph>

      {/* Usage Guide - 可折叠 */}
      {!isConnected && showGuide && (
        <div style={{ marginBottom: 24 }}>
          <UsageGuide />
        </div>
      )}

      {/* Code Requirement Input */}
      <Card
        title={
          <Space>
            <SendOutlined />
            <span>代码需求</span>
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <TextArea
          placeholder="请详细描述您的代码需求，例如：&#10;- 创建一个用户登录功能，包含邮箱和密码验证&#10;- 实现一个文件上传组件，支持拖拽上传&#10;- 编写一个API接口，获取用户列表并支持分页"
          rows={6}
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          style={{ marginBottom: 16, fontSize: 14 }}
        />

        {/* GitHub Connection Section - 放在输入框下方 */}
        {!isConnected ? (
          <Alert
            message="未连接到GitHub"
            description="请先连接您的GitHub账户以选择目标仓库和分支。"
            type="warning"
            showIcon
            icon={<GithubOutlined />}
            action={
              <Button type="primary" icon={<GithubOutlined />} onClick={connectGitHub}>
                连接GitHub
              </Button>
            }
            style={{ marginBottom: 16 }}
          />
        ) : (
          <div style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              {/* Repository Selection */}
              <Col span={12}>
                <Space style={{ width: '100%', marginBottom: 8 }} direction="vertical" size={4}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text strong>
                      <FolderOutlined style={{ marginRight: 8 }} />
                      选择仓库
                    </Text>
                    <Button
                      type="link"
                      size="small"
                      icon={<ReloadOutlined />}
                      loading={repoLoading}
                      onClick={refreshRepos}
                    >
                      刷新
                    </Button>
                  </div>
                  <Select
                    placeholder="选择仓库"
                    style={{ width: '100%' }}
                    value={selectedRepo}
                    onChange={handleRepoSelect}
                    loading={repoLoading}
                    showSearch
                    allowClear
                    filterOption={(input, option) =>
                      (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
                    }
                  >
                    {repos.map((repo) => (
                      <Option key={repo.full_name} value={repo.full_name} label={repo.full_name}>
                        <Space>
                          <GithubOutlined />
                          {repo.full_name}
                          {(repo.private || repo.is_private) && <Tag color="orange">私有</Tag>}
                        </Space>
                      </Option>
                    ))}
                  </Select>
                </Space>
              </Col>

              {/* Branch Selection */}
              <Col span={12}>
                <Space style={{ width: '100%', marginBottom: 8 }} direction="vertical" size={4}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text strong>
                      <BranchesOutlined style={{ marginRight: 8 }} />
                      选择分支
                    </Text>
                    <Button
                      type="link"
                      size="small"
                      icon={<ReloadOutlined />}
                      loading={branchLoading}
                      onClick={refreshBranches}
                      disabled={!selectedRepo}
                    >
                      刷新
                    </Button>
                  </div>
                  <Select
                    placeholder={selectedRepo ? '选择分支' : '请先选择仓库'}
                    style={{ width: '100%' }}
                    value={selectedBranch}
                    onChange={setSelectedBranch}
                    loading={branchLoading}
                    disabled={!selectedRepo}
                    showSearch
                    allowClear
                    filterOption={(input, option) =>
                      (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
                    }
                  >
                    {branches.map((branch) => (
                      <Option key={branch.name} value={branch.name} label={branch.name}>
                        <Space>
                          <BranchesOutlined />
                          {branch.name}
                          {branch.protected && <Tag color="red">受保护</Tag>}
                        </Space>
                      </Option>
                    ))}
                  </Select>
                </Space>
              </Col>
            </Row>

            {/* Selected Repository Info */}
            {selectedRepoInfo && (
              <Card size="small" style={{ background: '#fafafa', marginTop: 16 }}>
                <Row gutter={16} align="middle">
                  <Col flex="auto">
                    <div>
                      <Text strong>{selectedRepoInfo.full_name}</Text>
                      {selectedRepoInfo.description && (
                        <Paragraph
                          type="secondary"
                          style={{ marginBottom: 0, marginTop: 4, fontSize: 12 }}
                          ellipsis={{ rows: 2 }}
                        >
                          {selectedRepoInfo.description}
                        </Paragraph>
                      )}
                    </div>
                  </Col>
                  <Col>
                    <Space>
                      {selectedRepoInfo.language && (
                        <Tag color="blue">{selectedRepoInfo.language}</Tag>
                      )}
                      <Tag>⭐ {selectedRepoInfo.stars_count || selectedRepoInfo.stargazers_count || 0}</Tag>
                      <Tooltip title="在GitHub中打开">
                        <Button
                          type="link"
                          size="small"
                          icon={<LinkOutlined />}
                          href={selectedRepoInfo.html_url}
                          target="_blank"
                        />
                      </Tooltip>
                    </Space>
                  </Col>
                </Row>
              </Card>
            )}
          </div>
        )}

        <Row justify="end">
          <Col>
            <Button
              type="primary"
              size="large"
              icon={<CodeOutlined />}
              loading={generating}
              onClick={handleAnalyze}
              disabled={!requirement.trim()}
            >
              分析代码
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Generated Code Output */}
      {generatedCode && (
        <Card
          title={
            <Space>
              <CodeOutlined />
              <span>分析结果</span>
            </Space>
          }
          extra={
            <Button
              type="primary"
              onClick={() => {
                navigator.clipboard.writeText(generatedCode)
                message.success('代码已复制到剪贴板')
              }}
            >
              复制代码
            </Button>
          }
        >
          <pre
            style={{
              background: '#1e1e1e',
              color: '#d4d4d4',
              padding: 16,
              borderRadius: 8,
              overflow: 'auto',
              maxHeight: 500,
              fontSize: 14,
              lineHeight: 1.5,
            }}
          >
            {generatedCode}
          </pre>
        </Card>
      )}
    </div>
  )
}

export default Develop
