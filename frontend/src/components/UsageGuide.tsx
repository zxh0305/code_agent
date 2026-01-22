import { Card, Steps, Typography, Space, Alert } from 'antd'
import { GithubOutlined, FolderOutlined, BranchesOutlined, CodeOutlined } from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography

function UsageGuide() {
  return (
    <Card
      title={
        <Space>
          <CodeOutlined />
          <span>快速开始</span>
        </Space>
      }
      style={{ marginBottom: 24 }}
    >
      <Steps
        direction="vertical"
        current={-1}
        items={[
          {
            title: '连接 GitHub 账户',
            icon: <GithubOutlined />,
            description: (
              <div>
                <Paragraph>
                  点击下方的 <Text strong>"连接 GitHub"</Text> 按钮，授权应用访问你的 GitHub 仓库。
                </Paragraph>
                <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                  <li>首次使用需要在 GitHub 进行授权</li>
                  <li>Token 会保存在本地，刷新页面不会丢失</li>
                  <li>可随时点击顶部的 "断开连接" 按钮</li>
                </ul>
              </div>
            ),
          },
          {
            title: '选择仓库',
            icon: <FolderOutlined />,
            description: (
              <div>
                <Paragraph>
                  在仓库选择器中选择目标仓库。
                </Paragraph>
                <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                  <li>支持搜索和筛选</li>
                  <li>私有仓库会显示橙色标签</li>
                  <li>点击刷新按钮更新列表</li>
                </ul>
              </div>
            ),
          },
          {
            title: '选择分支',
            icon: <BranchesOutlined />,
            description: (
              <div>
                <Paragraph>
                  选择仓库后，会自动加载分支列表并选中默认分支。
                </Paragraph>
                <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                  <li>可以切换到其他分支</li>
                  <li>受保护的分支会显示红色标签</li>
                  <li>会显示仓库的详细信息</li>
                </ul>
              </div>
            ),
          },
          {
            title: '描述代码需求',
            icon: <CodeOutlined />,
            description: (
              <div>
                <Paragraph>
                  在输入框中详细描述你的代码需求，然后点击 <Text strong>"生成代码"</Text> 按钮。
                </Paragraph>
                <Alert
                  type="info"
                  showIcon
                  message="提示"
                  description={
                    <div>
                      <p style={{ marginBottom: 8 }}>好的需求描述应该包含：</p>
                      <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                        <li>功能的具体描述</li>
                        <li>使用的技术栈（框架、库）</li>
                        <li>输入输出格式</li>
                        <li>特殊要求（性能、安全等）</li>
                      </ul>
                    </div>
                  }
                  style={{ marginTop: 12 }}
                />
              </div>
            ),
          },
        ]}
      />

      <Alert
        type="warning"
        showIcon
        message="注意事项"
        description={
          <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
            <li>生成的代码仅供参考，请仔细检查后再使用</li>
            <li>复杂功能建议分步生成，逐步完善</li>
            <li>确保已配置正确的 AI 模型（在设置页面）</li>
          </ul>
        }
        style={{ marginTop: 16 }}
      />
    </Card>
  )
}

export default UsageGuide
