import { Card, Typography, Row, Col, Statistic, Button } from 'antd'
import {
  GithubOutlined,
  CodeOutlined,
  PullRequestOutlined,
  RobotOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { Link } from 'react-router-dom'

const { Title, Paragraph } = Typography

function Home() {
  return (
    <div style={{ padding: '24px', marginLeft: 220 }}>
      <Title level={2}>
        <GithubOutlined style={{ marginRight: 12 }} />
        智能GitHub代码开发协作平台
      </Title>
      <Paragraph style={{ fontSize: 16, color: '#666' }}>
        一个由AI驱动的智能GitHub代码开发协作平台，旨在简化代码开发、分析和PR管理流程。
      </Paragraph>

      {/* 快速开始提示 */}
      <Card style={{ marginBottom: 24, background: '#e6f7ff', border: '1px solid #91d5ff' }}>
        <Title level={4} style={{ color: '#1890ff' }}>
          <SettingOutlined style={{ marginRight: 8 }} />
          开始使用前，请先完成系统配置
        </Title>
        <Paragraph>
          在使用平台功能之前，您需要配置GitHub OAuth凭证和OpenAI API密钥。
        </Paragraph>
        <Link to="/settings">
          <Button type="primary" icon={<SettingOutlined />}>
            前往设置
          </Button>
        </Link>
      </Card>

      {/* 功能统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="GitHub仓库"
              value={0}
              prefix={<GithubOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="代码分析"
              value={0}
              prefix={<CodeOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Pull Requests"
              value={0}
              prefix={<PullRequestOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="AI交互"
              value={0}
              prefix={<RobotOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 功能介绍 */}
      <Title level={3}>平台功能</Title>
      <Row gutter={16}>
        <Col span={6}>
          <Card title={<><GithubOutlined /> GitHub集成</>} hoverable>
            <ul style={{ paddingLeft: 16 }}>
              <li>OAuth授权认证</li>
              <li>仓库克隆/拉取/推送</li>
              <li>分支管理</li>
              <li>文件读写操作</li>
            </ul>
          </Card>
        </Col>
        <Col span={6}>
          <Card title={<><CodeOutlined /> 代码分析</>} hoverable>
            <ul style={{ paddingLeft: 16 }}>
              <li>AST语法解析</li>
              <li>代码结构提取</li>
              <li>依赖分析</li>
              <li>度量指标计算</li>
            </ul>
          </Card>
        </Col>
        <Col span={6}>
          <Card title={<><PullRequestOutlined /> PR管理</>} hoverable>
            <ul style={{ paddingLeft: 16 }}>
              <li>创建/更新PR</li>
              <li>代码审核</li>
              <li>合并管理</li>
              <li>评论互动</li>
            </ul>
          </Card>
        </Col>
        <Col span={6}>
          <Card title={<><RobotOutlined /> AI助手</>} hoverable>
            <ul style={{ paddingLeft: 16 }}>
              <li>代码生成</li>
              <li>代码修改</li>
              <li>Bug修复</li>
              <li>文档生成</li>
            </ul>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Home
