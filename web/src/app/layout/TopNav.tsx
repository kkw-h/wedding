import { Menu, Dropdown } from 'antd'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../providers/AuthProvider'

function TopNav() {
  const { pathname } = useLocation()
  const { user, signOut } = useAuth()
  return (
    <Menu mode="horizontal" selectedKeys={[pathname]} items={[
      { key: '/preplans', label: <Link to="/preplans">预案规划</Link> },
      { key: '/flows', label: <Link to="/flows">婚礼流程</Link> },
      { key: '/venues', label: <Link to="/venues">场地管理</Link> },
      { key: '/staff', label: <Link to="/staff">人员信息</Link> },
      { key: '/budgets', label: <Link to="/budgets">预算查看</Link> },
      user ? { key: 'user', label: (
        <Dropdown
          menu={{ items: [
            { key: 'me', label: <Link to="/me">我的信息</Link> },
            { key: 'logout', label: <span onClick={() => signOut()}>退出登录</span> }
          ] }}
        >
          <span>{user.email || '已登录'}</span>
        </Dropdown>
      ) } : { key: '/login', label: <Link to="/login">登录</Link> }
    ]} />
  )
}

export default TopNav