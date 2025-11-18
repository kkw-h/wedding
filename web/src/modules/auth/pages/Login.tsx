import { Alert, Card, Space } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import { supabase } from '@/shared/api/supabase'
import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { useEffect } from 'react'
import { useAuth } from '@/app/providers/AuthProvider'

function Login() {
  const nav = useNavigate()
  const location = useLocation() as any
  const { user, loading } = useAuth()

  useEffect(() => {
    if (supabase && !loading && user) {
      const to = location.state?.from?.pathname || '/preplans'
      nav(to, { replace: true })
    }
  }, [user, loading])

  return (
    <Space align="center" style={{ width: '100%', height: '100%', justifyContent: 'center' }}>
      <Card style={{ width: 380 }}>
        {!supabase ? (
          <Alert type="error" showIcon message="未配置 Supabase" description="请在 web/.env 设置 VITE_SUPABASE_URL 与 VITE_SUPABASE_ANON_KEY 后重启开发服务器" />
        ) : (
          <Auth
            supabaseClient={supabase}
            appearance={{ theme: ThemeSupa }}
            providers={[]}
            redirectTo={window.location.origin}
          />
        )}
      </Card>
    </Space>
  )
}

export default Login