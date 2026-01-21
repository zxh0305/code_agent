import { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Button,
  message,
  Tabs,
  Typography,
  Alert,
  Space,
  Tooltip,
  Divider,
  Tag,
  Switch,
  Select,
} from 'antd'
import {
  GithubOutlined,
  KeyOutlined,
  RobotOutlined,
  SaveOutlined,
  ReloadOutlined,
  QuestionCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  LinkOutlined,
} from '@ant-design/icons'
import { settingsService, SystemSettings, TestLLMProviderRequest } from '../services/settingsService'

const { Title, Text, Paragraph } = Typography
const { TabPane } = Tabs

function Settings() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [testingGithub, setTestingGithub] = useState(false)
  const [testingLLM, setTestingLLM] = useState(false)
  const [githubStatus, setGithubStatus] = useState<'success' | 'error' | 'untested'>('untested')
  const [selectedProvider, setSelectedProvider] = useState('openai')
  const [providerStatus, setProviderStatus] = useState<Record<string, 'success' | 'error' | 'untested'>>({
    openai: 'untested',
    siliconflow: 'untested',
    qwen: 'untested',
    zhipu: 'untested',
    local: 'untested'
  })

  const providers = [
    { value: 'openai', label: 'OpenAI', icon: <RobotOutlined /> },
    { value: 'siliconflow', label: '硅基流动', icon: <RobotOutlined /> },
    { value: 'qwen', label: '千问', icon: <RobotOutlined /> },
    { value: 'zhipu', label: '智谱', icon: <RobotOutlined /> },
    { value: 'local', label: '本地 LLM', icon: <RobotOutlined /> }
  ]

  // 加载设置
  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    try {
      const settings = await settingsService.getSettings()
      form.setFieldsValue(settings)
    } catch (error) {
      message.error('加载设置失败')
    } finally {
      setLoading(false)
    }
  }

  // 保存设置
  const handleSave = async (values: SystemSettings) => {
    setSaving(true)
    try {
      await settingsService.saveSettings(values)
      message.success('设置保存成功')
    } catch (error) {
      message.error('保存设置失败')
    } finally {
      setSaving(false)
    }
  }

  // 测试GitHub连接
  const testGithubConnection = async () => {
    setTestingGithub(true)
    try {
      const values = form.getFieldsValue()
      const result = await settingsService.testGithubConnection(
        values.github_client_id,
        values.github_client_secret
      )
      if (result.success) {
        setGithubStatus('success')
        message.success('GitHub连接测试成功')
      } else {
        setGithubStatus('error')
        message.error(result.message || 'GitHub连接测试失败')
      }
    } catch (error) {
      setGithubStatus('error')
      message.error('GitHub连接测试失败')
    } finally {
      setTestingGithub(false)
    }
  }

  // 测试LLM提供商连接
  const testProviderConnection = async () => {
    const values = form.getFieldsValue()
    const provider = selectedProvider

    setProviderStatus(prev => ({ ...prev, [provider]: 'untested' }))
    setTestingLLM(true)

    try {
      const request: TestLLMProviderRequest = {
        provider,
        api_key: values[`${provider}_api_key`],
        base_url: values[`${provider}_base_url`],
        model: values[`${provider}_model`]
      }

      const result = await settingsService.testLLMProvider(request)

      if (result.success) {
        setProviderStatus(prev => ({ ...prev, [provider]: 'success' }))
        message.success(`${providers.find(p => p.value === provider)?.label}连接测试成功`)
      } else {
        setProviderStatus(prev => ({ ...prev, [provider]: 'error' }))
        message.error(result.message || '连接测试失败')
      }
    } catch (error) {
      setProviderStatus(prev => ({ ...prev, [provider]: 'error' }))
      message.error('连接测试失败')
    } finally {
      setTestingLLM(false)
    }
  }

  const renderStatusTag = (status: 'success' | 'error' | 'untested') => {
    switch (status) {
      case 'success':
        return <Tag icon={<CheckCircleOutlined />} color="success">已验证</Tag>
      case 'error':
        return <Tag icon={<ExclamationCircleOutlined />} color="error">验证失败</Tag>
      default:
        return <Tag color="default">未验证</Tag>
    }
  }

  return (
    <div style={{ padding: '24px', marginLeft: 220, maxWidth: 900 }}>
      <Title level={2}>
        <KeyOutlined style={{ marginRight: 12 }} />
        系统设置
      </Title>
      <Paragraph style={{ color: '#666' }}>
        配置平台必要的凭证和参数，这些设置将保存在服务器端。
      </Paragraph>

      <Alert
        message="安全提示"
        description="请妥善保管您的API密钥和凭证，不要分享给他人。所有敏感信息将加密存储。"
        type="warning"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          github_redirect_uri: 'http://localhost:8080/api/v1/github/callback',
          github_scopes: 'repo,user',
          openai_model: 'gpt-4o',
          openai_max_tokens: 4096,
          openai_temperature: 0.7,
          siliconflow_base_url: 'https://api.siliconflow.cn/v1',
          siliconflow_model: 'deepseek-ai/DeepSeek-V3',
          qwen_base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
          qwen_model: 'qwen-plus',
          zhipu_base_url: 'https://open.bigmodel.cn/api/paas/v4',
          zhipu_model: 'glm-4',
          default_llm_provider: 'openai',
          jwt_algorithm: 'HS256',
          jwt_expire_minutes: 1440,
        }}
      >
        <Tabs defaultActiveKey="github">
          {/* GitHub OAuth 设置 */}
          <TabPane
            tab={
              <span>
                <GithubOutlined />
                GitHub OAuth
                {renderStatusTag(githubStatus)}
              </span>
            }
            key="github"
          >
            <Card>
              <Alert
                message="如何获取GitHub OAuth凭证？"
                description={
                  <div>
                    <ol style={{ margin: '8px 0', paddingLeft: 20 }}>
                      <li>访问 <a href="https://github.com/settings/developers" target="_blank" rel="noopener noreferrer">GitHub Developer Settings <LinkOutlined /></a></li>
                      <li>点击 "New OAuth App"</li>
                      <li>填写应用信息：
                        <ul>
                          <li>Application name: 您的应用名称</li>
                          <li>Homepage URL: http://localhost:8080</li>
                          <li>Authorization callback URL: http://localhost:8080/api/v1/github/callback</li>
                        </ul>
                      </li>
                      <li>创建后复制 Client ID 和 Client Secret</li>
                    </ol>
                  </div>
                }
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              <Form.Item
                name="github_client_id"
                label={
                  <span>
                    Client ID
                    <Tooltip title="GitHub OAuth App的Client ID">
                      <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                    </Tooltip>
                  </span>
                }
                rules={[{ required: true, message: '请输入GitHub Client ID' }]}
              >
                <Input placeholder="例如: Iv1.a1b2c3d4e5f6g7h8" />
              </Form.Item>

              <Form.Item
                name="github_client_secret"
                label={
                  <span>
                    Client Secret
                    <Tooltip title="GitHub OAuth App的Client Secret">
                      <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                    </Tooltip>
                  </span>
                }
                rules={[{ required: true, message: '请输入GitHub Client Secret' }]}
              >
                <Input.Password
                  placeholder="您的Client Secret"
                  iconRender={(visible) => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>

              <Form.Item
                name="github_redirect_uri"
                label="回调URL"
              >
                <Input placeholder="http://localhost:8080/api/v1/github/callback" />
              </Form.Item>

              <Form.Item
                name="github_scopes"
                label="授权范围"
              >
                <Input placeholder="repo,user" disabled />
              </Form.Item>

              <Button
                onClick={testGithubConnection}
                loading={testingGithub}
                icon={<CheckCircleOutlined />}
              >
                测试连接
              </Button>
            </Card>
          </TabPane>

          {/* LLM 提供商设置 */}
          <TabPane
            tab={
              <span>
                <RobotOutlined />
                LLM 提供商
              </span>
            }
            key="llm"
          >
            <Card>
              {/* 默认提供商选择 */}
              <Form.Item
                name="default_llm_provider"
                label="默认提供商"
                tooltip="系统默认使用的LLM提供商"
              >
                <Select>
                  {providers.map(p => (
                    <Select.Option key={p.value} value={p.value}>
                      {p.icon} {p.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              <Divider />

              {/* 提供商选择下拉菜单 */}
              <Form.Item label="选择要配置的提供商">
                <Select
                  value={selectedProvider}
                  onChange={setSelectedProvider}
                  style={{ width: 200 }}
                >
                  {providers.map(p => (
                    <Select.Option key={p.value} value={p.value}>
                      {p.icon} {p.label} {renderStatusTag(providerStatus[p.value])}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              {/* 动态渲染当前提供商的配置 */}
              {selectedProvider !== 'local' && (
                <>
                  <Alert
                    message={`${providers.find(p => p.value === selectedProvider)?.label} 配置`}
                    description={
                      <div>
                        <Text type="secondary">
                          配置 {providers.find(p => p.value === selectedProvider)?.label} 的 API 密钥和参数。
                          {selectedProvider === 'openai' && ' 注意：使用OpenAI API需要有效的付费账户或额度。'}
                        </Text>
                      </div>
                    }
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Form.Item
                    name={`${selectedProvider}_api_key`}
                    label="API Key"
                    rules={[{ required: false, message: '请输入API Key' }]}
                  >
                    <Input.Password
                      placeholder="输入API Key"
                      iconRender={(visible) => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
                    />
                  </Form.Item>

                  <Form.Item
                    name={`${selectedProvider}_base_url`}
                    label="API 地址"
                  >
                    <Input placeholder="API Base URL" />
                  </Form.Item>

                  <Form.Item
                    name={`${selectedProvider}_model`}
                    label="模型名称"
                  >
                    <Input placeholder="模型名称" />
                  </Form.Item>
                </>
              )}

              {selectedProvider === 'local' && (
                <>
                  <Alert
                    message="本地LLM配置"
                    description={
                      <div>
                        <Text type="secondary">
                          如果您有本地部署的LLM服务（如CodeLlama），可以在此配置。
                        </Text>
                      </div>
                    }
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Form.Item
                    name="local_llm_enabled"
                    label="启用本地LLM"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>

                  <Form.Item
                    name="local_llm_url"
                    label="本地LLM服务地址"
                  >
                    <Input placeholder="http://localhost:8000/v1" />
                  </Form.Item>

                  <Form.Item
                    name="local_llm_model"
                    label="本地LLM模型名称"
                  >
                    <Input placeholder="codellama" />
                  </Form.Item>
                </>
              )}

              <Button
                onClick={testProviderConnection}
                loading={testingLLM}
                icon={<CheckCircleOutlined />}
              >
                测试连接
              </Button>
            </Card>
          </TabPane>

          {/* JWT 安全设置 */}
          <TabPane
            tab={
              <span>
                <KeyOutlined />
                安全设置
              </span>
            }
            key="jwt"
          >
            <Card>
              <Alert
                message="JWT密钥说明"
                description="JWT密钥用于用户认证令牌的签名。生产环境中请使用强随机密钥，至少32个字符。"
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              <Form.Item
                name="jwt_secret_key"
                label={
                  <span>
                    JWT签名密钥
                    <Tooltip title="用于签名JWT令牌，请使用强随机字符串">
                      <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                    </Tooltip>
                  </span>
                }
                rules={[
                  { required: true, message: '请输入JWT签名密钥' },
                  { min: 32, message: '密钥长度至少32个字符' },
                ]}
              >
                <Input.Password
                  placeholder="至少32个字符的随机密钥"
                  iconRender={(visible) => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>

              <Button
                onClick={() => {
                  const randomKey = Array.from(crypto.getRandomValues(new Uint8Array(32)))
                    .map((b) => b.toString(16).padStart(2, '0'))
                    .join('')
                  form.setFieldValue('jwt_secret_key', randomKey)
                  message.success('已生成随机密钥')
                }}
                style={{ marginBottom: 16 }}
              >
                生成随机密钥
              </Button>

              <Form.Item
                name="jwt_algorithm"
                label="加密算法"
              >
                <Input disabled placeholder="HS256" />
              </Form.Item>

              <Form.Item
                name="jwt_expire_minutes"
                label="令牌有效期（分钟）"
              >
                <Input type="number" placeholder="1440" />
              </Form.Item>
            </Card>
          </TabPane>
        </Tabs>

        <Divider />

        <Space>
          <Button
            type="primary"
            htmlType="submit"
            loading={saving}
            icon={<SaveOutlined />}
            size="large"
          >
            保存设置
          </Button>
          <Button
            onClick={loadSettings}
            loading={loading}
            icon={<ReloadOutlined />}
            size="large"
          >
            重新加载
          </Button>
        </Space>
      </Form>
    </div>
  )
}

export default Settings
