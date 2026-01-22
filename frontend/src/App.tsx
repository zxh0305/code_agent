import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Sidebar from './components/Sidebar'
import Settings from './pages/Settings'
import Home from './pages/Home'
import Develop from './pages/Develop'
import GitHubCallback from './pages/GitHubCallback'
import './styles/App.css'

const { Content } = Layout

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Routes>
        {/* GitHub OAuth 回调页面 - 独立布局 */}
        <Route path="/github/callback" element={<GitHubCallback />} />

        {/* 主应用页面 - 带侧边栏 */}
        <Route path="*" element={
          <>
            <Sidebar />
            <Layout>
              <Content style={{ margin: '24px', background: '#fff', borderRadius: '8px' }}>
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/develop" element={<Develop />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Content>
            </Layout>
          </>
        } />
      </Routes>
    </Layout>
  )
}

export default App
