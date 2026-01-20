import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Sidebar from './components/Sidebar'
import Settings from './pages/Settings'
import Home from './pages/Home'
import Develop from './pages/Develop'
import './styles/App.css'

const { Content } = Layout

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
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
    </Layout>
  )
}

export default App
