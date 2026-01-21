import { Link, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  HomeOutlined,
  SettingOutlined,
  GithubOutlined,
  CodeOutlined,
  PullRequestOutlined,
  RobotOutlined,
  EditOutlined,
} from '@ant-design/icons'

const { Sider } = Layout

const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: <Link to="/">首页</Link>,
  },
  {
    key: '/develop',
    icon: <EditOutlined />,
    label: <Link to="/develop">代码开发</Link>,
  },
  {
    type: 'divider' as const,
  },
  {
    key: 'github',
    icon: <GithubOutlined />,
    label: 'GitHub',
    children: [
      {
        key: '/github/repos',
        label: <Link to="/github/repos">仓库管理</Link>,
      },
      {
        key: '/github/auth',
        label: <Link to="/github/auth">授权管理</Link>,
      },
    ],
  },
  {
    key: 'code',
    icon: <CodeOutlined />,
    label: '代码分析',
    children: [
      {
        key: '/code/analyze',
        label: <Link to="/code/analyze">代码分析</Link>,
      },
    ],
  },
  {
    key: 'pr',
    icon: <PullRequestOutlined />,
    label: 'PR管理',
    children: [
      {
        key: '/pr/list',
        label: <Link to="/pr/list">PR列表</Link>,
      },
      {
        key: '/pr/create',
        label: <Link to="/pr/create">创建PR</Link>,
      },
    ],
  },
  {
    key: 'ai',
    icon: <RobotOutlined />,
    label: 'AI助手',
    children: [
      {
        key: '/ai/generate',
        label: <Link to="/ai/generate">代码生成</Link>,
      },
      {
        key: '/ai/review',
        label: <Link to="/ai/review">代码审核</Link>,
      },
    ],
  },
  {
    type: 'divider' as const,
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: <Link to="/settings">系统设置</Link>,
  },
]

function Sidebar() {
  const location = useLocation()

  return (
    <Sider
      width={220}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
      }}
    >
      <div className="logo">
        <GithubOutlined style={{ marginRight: 8 }} />
        Code Agent
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        defaultOpenKeys={['github', 'code', 'pr', 'ai']}
        items={menuItems}
        onClick={({ key }) => {
          // Force re-render when menu item is clicked
          if (key !== location.pathname) {
            window.location.href = key
          }
        }}
      />
    </Sider>
  )
}

export default Sidebar
