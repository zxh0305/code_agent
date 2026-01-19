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
import { settingsService, SystemSettings } from '../services/settingsService'

const { Title, Text, Paragraph } = Typography
const { TabPane } = Tabs

function Settings() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [testingGithub, setTestingGithub] = useState(false)
  const [testingOpenAI, setTestingOpenAI] = useState(false)
  const [githubStatus, setGithubStatus] = useState<'success' | 'error' | 'untested'>('untested')
  const [openaiStatus, setOpenaiStatus] = useState<'success' | 'error' | 'untested'>('untested')

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

  // 测试OpenAI连接
  const testOpenAIConnection = async () => {
    setTestingOpenAI(true)
    try {
      const values = form.getFieldsValue()
      const result = await settingsService.testOpenAIConnection(values.openai_api_key)
      if (result.success) {
        setOpenaiStatus('success')
        message.success('OpenAI连接测试成功')
      } else {
        setOpenaiStatus('error')
        message.error(result.message || 'OpenAI连接测试失败')
      }
    } catch (error) {
      setOpenaiStatus('error')
      message.error('OpenAI连接测试失败')
    } finally {
      setTestingOpenAI(false)
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

          {/* OpenAI 设置 */}
          <TabPane
            tab={
              <span>
                <RobotOutlined />
                OpenAI API
                {renderStatusTag(openaiStatus)}
              </span>
            }
            key="openai"
          >
            <Card>
              <Alert
                message="如何获取OpenAI API密钥？"
                description={
                  <div>
                    <ol style={{ margin: '8px 0', paddingLeft: 20 }}>
                      <li>访问 <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">OpenAI API Keys <LinkOutlined /></a></li>
                      <li>登录您的OpenAI账户</li>
                      <li>点击 "Create new secret key"</li>
                      <li>复制生成的API密钥（注意：密钥只显示一次）</li>
                    </ol>
                    <Text type="secondary">注意：使用OpenAI API需要有效的付费账户或额度。</Text>
                  </div>
                }
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              <Form.Item
                name="openai_api_key"
                label={
                  <span>
                    API Key
                    <Tooltip title="OpenAI API密钥，以sk-开头">
                      <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                    </Tooltip>
                  </span>
                }
                rules={[{ required: false, message: '请输入OpenAI API Key' }]}
              >
                <Input.Password
                  placeholder="sk-..."
                  iconRender={(visible) => (visible ? <EyeOutlined /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>

              <Form.Item
                name="openai_model"
                label="模型选择"
              >
                <Input placeholder="gpt-4o" />
              </Form.Item>

              <Form.Item
                name="openai_max_tokens"
                label="最大Token数"
              >
                <Input type="number" placeholder="4096" />
              </Form.Item>

              <Form.Item
                name="openai_temperature"
                label="Temperature"
              >
                <Input type="number" step="0.1" placeholder="0.7" />
              </Form.Item>

              <Divider />

              <Title level={5}>本地LLM设置（可选）</Title>
              <Paragraph type="secondary">
                如果您有本地部署的LLM服务（如CodeLlama），可以在此配置作为OpenAI的替代方案。
              </Paragraph>

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

              <Button
                onClick={testOpenAIConnection}
                loading={testingOpenAI}
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
