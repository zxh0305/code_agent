import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Layout,
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
  List,
  Modal,
  Dropdown,
  Empty,
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
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  MoreOutlined,
  HistoryOutlined,
  FileTextOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import {
  githubApi,
  llmApi,
  taskApi,
  Repository,
  Branch,
  Task,
} from '../services/api'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input
const { Option } = Select
const { Sider, Content } = Layout

function Develop() {
  // Task state
  const [tasks, setTasks] = useState<Task[]>([])
  const [currentTask, setCurrentTask] = useState<Task | null>(null)
  const [taskLoading, setTaskLoading] = useState(false)
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null)
  const [editingName, setEditingName] = useState('')
  const editInputRef = useRef<any>(null)

  // Requirement and generation state
  const [requirement, setRequirement] = useState('')
  const [generating, setGenerating] = useState(false)
  const [generatedCode, setGeneratedCode] = useState('')

  // GitHub state
  const [isConnected, setIsConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [repos, setRepos] = useState<Repository[]>([])
  const [branches, setBranches] = useState<Branch[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null)
  const [selectedBranch, setSelectedBranch] = useState<string | null>(null)
  const [repoLoading, setRepoLoading] = useState(false)
  const [branchLoading, setBranchLoading] = useState(false)

  // Load tasks
  const loadTasks = useCallback(async () => {
    try {
      setTaskLoading(true)
      const taskList = await taskApi.list({ is_archived: false })
      setTasks(taskList)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setTaskLoading(false)
    }
  }, [])

  // Load GitHub repos
  const checkConnection = useCallback(async () => {
    try {
      setLoading(true)
      const accessToken = localStorage.getItem('github_token')
      const response = await githubApi.getRepos(accessToken || undefined)
      setRepos(response.repositories || [])
      setIsConnected(true)
    } catch (error) {
      setIsConnected(false)
      setRepos([])
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    loadTasks()
    checkConnection()
  }, [loadTasks, checkConnection])

  // Focus on edit input when editing
  useEffect(() => {
    if (editingTaskId && editInputRef.current) {
      editInputRef.current.focus()
    }
  }, [editingTaskId])

  // Create new task
  const handleCreateTask = async () => {
    try {
      const newTask = await taskApi.create({ name: '新建任务' })
      setTasks([newTask, ...tasks])
      setCurrentTask(newTask)
      setRequirement('')
      setGeneratedCode('')
      setSelectedRepo(null)
      setSelectedBranch(null)
      message.success('新任务已创建')
    } catch (error: any) {
      message.error(error.message || '创建任务失败')
    }
  }

  // Select task
  const handleSelectTask = async (task: Task) => {
    setCurrentTask(task)
    setRequirement(task.requirement || '')
    setGeneratedCode(task.generated_code || '')
    setSelectedRepo(task.repository || null)
    setSelectedBranch(task.branch || null)

    // Load branches if repo is selected
    if (task.repository) {
      const [owner, repo] = task.repository.split('/')
      if (owner && repo) {
        try {
          setBranchLoading(true)
          const accessToken = localStorage.getItem('github_token')
          const response = await githubApi.getBranches(owner, repo, accessToken || undefined)
          setBranches(response.branches || [])
        } catch (error) {
          console.error('Failed to load branches:', error)
        } finally {
          setBranchLoading(false)
        }
      }
    }
  }

  // Start editing task name
  const handleStartEdit = (task: Task, e?: React.MouseEvent) => {
    e?.stopPropagation()
    setEditingTaskId(task.id)
    setEditingName(task.name)
  }

  // Save task name
  const handleSaveTaskName = async () => {
    if (!editingTaskId || !editingName.trim()) {
      setEditingTaskId(null)
      return
    }

    try {
      await taskApi.rename(editingTaskId, editingName.trim())
      setTasks(tasks.map(t =>
        t.id === editingTaskId ? { ...t, name: editingName.trim() } : t
      ))
      if (currentTask?.id === editingTaskId) {
        setCurrentTask({ ...currentTask, name: editingName.trim() })
      }
    } catch (error: any) {
      message.error(error.message || '重命名失败')
    } finally {
      setEditingTaskId(null)
    }
  }

  // Delete task
  const handleDeleteTask = async (taskId: number, e?: React.MouseEvent) => {
    e?.stopPropagation()
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个任务吗？此操作不可恢复。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await taskApi.delete(taskId)
          setTasks(tasks.filter(t => t.id !== taskId))
          if (currentTask?.id === taskId) {
            setCurrentTask(null)
            setRequirement('')
            setGeneratedCode('')
          }
          message.success('任务已删除')
        } catch (error: any) {
          message.error(error.message || '删除失败')
        }
      },
    })
  }

  // Refresh repositories
  const refreshRepos = async () => {
    try {
      setRepoLoading(true)
      const accessToken = localStorage.getItem('github_token')
      const response = await githubApi.getRepos(accessToken || undefined)
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
      const accessToken = localStorage.getItem('github_token')
      const response = await githubApi.getBranches(owner, repo, accessToken || undefined)
      setBranches(response.branches || [])

      // Auto-select default branch
      const selectedRepoData = repos.find((r) => r.full_name === value)
      if (selectedRepoData?.default_branch) {
        const defaultBranch = (response.branches || []).find(
          (b: Branch) => b.name === selectedRepoData.default_branch
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
      const accessToken = localStorage.getItem('github_token')
      const response = await githubApi.getBranches(owner, repo, accessToken || undefined)
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
      const response = await githubApi.getAuthUrl()
      window.location.href = response.auth_url
    } catch (error: any) {
      message.error(error.message || '获取GitHub授权链接失败')
    }
  }

  // Generate code
  const handleGenerate = async () => {
    if (!requirement.trim()) {
      message.warning('请输入代码需求描述')
      return
    }

    try {
      setGenerating(true)
      const response = await llmApi.generate({
        prompt: requirement,
        context: selectedRepo
          ? `Repository: ${selectedRepo}, Branch: ${selectedBranch || 'main'}`
          : undefined,
      })
      const code = response.code || response.content
      setGeneratedCode(code)

      // Save to current task
      if (currentTask) {
        await taskApi.update(currentTask.id, {
          requirement,
          generated_code: code,
          repository: selectedRepo || undefined,
          branch: selectedBranch || undefined,
          status: 'in_progress',
        })
        setCurrentTask({
          ...currentTask,
          requirement,
          generated_code: code,
          repository: selectedRepo,
          branch: selectedBranch,
          status: 'in_progress',
        })
      }

      message.success('代码生成成功')
    } catch (error: any) {
      message.error(error.message || '代码生成失败')
    } finally {
      setGenerating(false)
    }
  }

  // Auto-save requirement changes
  const handleRequirementChange = async (value: string) => {
    setRequirement(value)
    // Debounced save would be better, but keeping it simple
  }

  // Copy code to clipboard
  const copyCode = () => {
    navigator.clipboard.writeText(generatedCode)
    message.success('代码已复制到剪贴板')
  }

  // Get selected repo info
  const selectedRepoInfo = repos.find((r) => r.full_name === selectedRepo)

  // Format task time
  const formatTime = (dateStr: string | null) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString()
  }

  return (
    <Layout style={{ height: '100vh', marginLeft: 220 }}>
      {/* Left Task Panel */}
      <Sider
        width={280}
        style={{
          background: '#f5f5f5',
          borderRight: '1px solid #e8e8e8',
          overflow: 'auto',
        }}
      >
        <div style={{ padding: '16px' }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            block
            size="large"
            onClick={handleCreateTask}
            style={{ marginBottom: 16 }}
          >
            新建任务
          </Button>

          <div style={{ marginBottom: 12 }}>
            <Text type="secondary">
              <HistoryOutlined style={{ marginRight: 8 }} />
              历史任务 ({tasks.length})
            </Text>
          </div>

          {taskLoading ? (
            <div style={{ textAlign: 'center', padding: 20 }}>
              <Spin />
            </div>
          ) : tasks.length === 0 ? (
            <Empty
              description="暂无任务"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ) : (
            <List
              dataSource={tasks}
              renderItem={(task) => (
                <div
                  key={task.id}
                  onClick={() => handleSelectTask(task)}
                  style={{
                    padding: '12px',
                    marginBottom: 8,
                    background: currentTask?.id === task.id ? '#e6f7ff' : '#fff',
                    borderRadius: 8,
                    cursor: 'pointer',
                    border: currentTask?.id === task.id ? '1px solid #1890ff' : '1px solid #e8e8e8',
                    transition: 'all 0.2s',
                  }}
                >
                  {editingTaskId === task.id ? (
                    <Input
                      ref={editInputRef}
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      onBlur={handleSaveTaskName}
                      onPressEnter={handleSaveTaskName}
                      size="small"
                      style={{ marginBottom: 4 }}
                    />
                  ) : (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Text
                        strong
                        style={{ flex: 1, wordBreak: 'break-word' }}
                        onDoubleClick={(e) => handleStartEdit(task, e)}
                      >
                        <FileTextOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                        {task.name}
                      </Text>
                      <Dropdown
                        menu={{
                          items: [
                            {
                              key: 'rename',
                              icon: <EditOutlined />,
                              label: '重命名',
                              onClick: ({ domEvent }) => handleStartEdit(task, domEvent as any),
                            },
                            {
                              key: 'delete',
                              icon: <DeleteOutlined />,
                              label: '删除',
                              danger: true,
                              onClick: ({ domEvent }) => handleDeleteTask(task.id, domEvent as any),
                            },
                          ],
                        }}
                        trigger={['click']}
                      >
                        <Button
                          type="text"
                          size="small"
                          icon={<MoreOutlined />}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Dropdown>
                    </div>
                  )}
                  <div style={{ marginTop: 4 }}>
                    {task.repository && (
                      <Tag color="blue" style={{ marginRight: 4, marginBottom: 4 }}>
                        <GithubOutlined /> {task.repository.split('/')[1]}
                      </Tag>
                    )}
                    {task.status === 'in_progress' && (
                      <Tag color="processing">进行中</Tag>
                    )}
                    {task.status === 'completed' && (
                      <Tag color="success">已完成</Tag>
                    )}
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {formatTime(task.updated_at)}
                  </Text>
                </div>
              )}
            />
          )}
        </div>
      </Sider>

      {/* Main Content */}
      <Content style={{ padding: 24, overflow: 'auto', background: '#fff' }}>
        {!currentTask ? (
          <div style={{ textAlign: 'center', paddingTop: 100 }}>
            <CodeOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
            <Title level={4} type="secondary" style={{ marginTop: 24 }}>
              选择一个任务或创建新任务开始
            </Title>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateTask}>
              新建任务
            </Button>
          </div>
        ) : (
          <div style={{ maxWidth: 1000, margin: '0 auto' }}>
            {/* Task Header */}
            <div style={{ marginBottom: 24 }}>
              <Title level={3} style={{ marginBottom: 8 }}>
                <FileTextOutlined style={{ marginRight: 12 }} />
                {currentTask.name}
              </Title>
              <Space>
                <Tag color={currentTask.status === 'completed' ? 'success' : currentTask.status === 'in_progress' ? 'processing' : 'default'}>
                  {currentTask.status === 'completed' ? '已完成' : currentTask.status === 'in_progress' ? '进行中' : '草稿'}
                </Tag>
                <Text type="secondary">更新于 {formatTime(currentTask.updated_at)}</Text>
              </Space>
            </div>

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
                onChange={(e) => handleRequirementChange(e.target.value)}
                style={{ marginBottom: 16, fontSize: 14 }}
              />
              <Row justify="space-between" align="middle">
                <Col>
                  {selectedRepo && (
                    <Space>
                      <Tag color="blue" icon={<FolderOutlined />}>
                        {selectedRepo}
                      </Tag>
                      {selectedBranch && (
                        <Tag color="green" icon={<BranchesOutlined />}>
                          {selectedBranch}
                        </Tag>
                      )}
                    </Space>
                  )}
                </Col>
                <Col>
                  <Button
                    type="primary"
                    size="large"
                    icon={<SendOutlined />}
                    loading={generating}
                    onClick={handleGenerate}
                    disabled={!requirement.trim()}
                  >
                    生成代码
                  </Button>
                </Col>
              </Row>
            </Card>

            {/* GitHub Connection */}
            <Card
              title={
                <Space>
                  <GithubOutlined />
                  <span>GitHub 仓库</span>
                  {isConnected ? (
                    <Tag color="success" icon={<CheckCircleOutlined />}>
                      已连接
                    </Tag>
                  ) : (
                    <Tag color="warning" icon={<ExclamationCircleOutlined />}>
                      未连接
                    </Tag>
                  )}
                </Space>
              }
              style={{ marginBottom: 24 }}
              extra={
                loading ? (
                  <Spin size="small" />
                ) : (
                  <Tooltip title="刷新连接状态">
                    <Button
                      type="text"
                      icon={<ReloadOutlined />}
                      onClick={checkConnection}
                    />
                  </Tooltip>
                )
              }
            >
              {!isConnected ? (
                <Alert
                  message="未连接到GitHub"
                  description="请先连接您的GitHub账户以选择仓库和分支。"
                  type="warning"
                  showIcon
                  action={
                    <Button type="primary" onClick={connectGitHub}>
                      连接GitHub
                    </Button>
                  }
                />
              ) : (
                <>
                  <Row gutter={16}>
                    <Col span={12}>
                      <div style={{ marginBottom: 8 }}>
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
                          style={{ float: 'right' }}
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
                          (option?.children as unknown as string)
                            ?.toLowerCase()
                            .includes(input.toLowerCase())
                        }
                      >
                        {repos.map((repo) => (
                          <Option key={repo.full_name} value={repo.full_name}>
                            <Space>
                              <GithubOutlined />
                              {repo.full_name}
                              {repo.private && <Tag color="orange" style={{ marginLeft: 4 }}>私有</Tag>}
                            </Space>
                          </Option>
                        ))}
                      </Select>
                    </Col>

                    <Col span={12}>
                      <div style={{ marginBottom: 8 }}>
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
                          style={{ float: 'right' }}
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
                          (option?.children as unknown as string)
                            ?.toLowerCase()
                            .includes(input.toLowerCase())
                        }
                      >
                        {branches.map((branch) => (
                          <Option key={branch.name} value={branch.name}>
                            <Space>
                              <BranchesOutlined />
                              {branch.name}
                              {branch.protected && <Tag color="red" style={{ marginLeft: 4 }}>受保护</Tag>}
                            </Space>
                          </Option>
                        ))}
                      </Select>
                    </Col>
                  </Row>

                  {selectedRepoInfo && (
                    <>
                      <Divider style={{ margin: '16px 0' }} />
                      <Card size="small" style={{ background: '#fafafa' }}>
                        <Row justify="space-between" align="middle">
                          <Col>
                            <Text strong>{selectedRepoInfo.full_name}</Text>
                            {selectedRepoInfo.description && (
                              <Paragraph
                                type="secondary"
                                style={{ marginBottom: 0, marginTop: 4 }}
                                ellipsis={{ rows: 1 }}
                              >
                                {selectedRepoInfo.description}
                              </Paragraph>
                            )}
                          </Col>
                          <Col>
                            <Space>
                              {selectedRepoInfo.language && (
                                <Tag color="blue">{selectedRepoInfo.language}</Tag>
                              )}
                              <Tag>⭐ {selectedRepoInfo.stargazers_count}</Tag>
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
                    </>
                  )}
                </>
              )}
            </Card>

            {/* Generated Code Output */}
            {generatedCode && (
              <Card
                title={
                  <Space>
                    <CodeOutlined />
                    <span>生成的代码</span>
                  </Space>
                }
                extra={
                  <Button
                    type="primary"
                    icon={<CopyOutlined />}
                    onClick={copyCode}
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
                    lineHeight: 1.6,
                    margin: 0,
                  }}
                >
                  {generatedCode}
                </pre>
              </Card>
            )}
          </div>
        )}
      </Content>
    </Layout>
  )
}

export default Develop
