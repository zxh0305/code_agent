import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Spin, Result, Button } from 'antd'
import { LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { githubApi, tokenManager } from '../services/api'

function GitHubCallback() {
  const navigate = useNavigate()
  const location = useLocation()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('正在处理 GitHub 授权...')

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // 从 URL 中获取 code 和 state 参数
        const params = new URLSearchParams(location.search)
        const code = params.get('code')
        const state = params.get('state')

        if (!code || !state) {
          throw new Error('缺少授权参数')
        }

        // 交换 code 获取 access token
        const response = await githubApi.exchangeToken(code, state)

        // 存储 token
        tokenManager.set(response.access_token)

        setStatus('success')
        setMessage('GitHub 授权成功！')

        // 3秒后跳转到开发页面
        setTimeout(() => {
          navigate('/develop')
        }, 1500)
      } catch (error: any) {
        console.error('GitHub OAuth error:', error)
        setStatus('error')
        setMessage(error.message || 'GitHub 授权失败，请重试')
      }
    }

    handleCallback()
  }, [location, navigate])

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      {status === 'loading' && (
        <div style={{ textAlign: 'center', color: '#fff' }}>
          <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
          <div style={{ marginTop: 24, fontSize: 18 }}>{message}</div>
        </div>
      )}

      {status === 'success' && (
        <Result
          status="success"
          icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
          title={<span style={{ color: '#fff' }}>{message}</span>}
          subTitle={<span style={{ color: 'rgba(255,255,255,0.8)' }}>即将跳转到开发页面...</span>}
        />
      )}

      {status === 'error' && (
        <Result
          status="error"
          icon={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
          title={<span style={{ color: '#fff' }}>授权失败</span>}
          subTitle={<span style={{ color: 'rgba(255,255,255,0.8)' }}>{message}</span>}
          extra={
            <Button type="primary" onClick={() => navigate('/develop')}>
              返回开发页面
            </Button>
          }
        />
      )}
    </div>
  )
}

export default GitHubCallback
