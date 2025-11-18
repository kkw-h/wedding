import { Menu } from 'antd'
import { Link, useLocation } from 'react-router-dom'

function SideMenu() {
  const { pathname } = useLocation()
  const root = pathname.split('/')[1]
  return (
    <Menu mode="inline" selectedKeys={[`/${root}`]} items={[
      { key: '/preplans', label: <Link to="/preplans">预案列表</Link> },
      { key: '/flows', label: <Link to="/flows">流程列表</Link> },
      { key: '/venues', label: <Link to="/venues">场地列表</Link> },
      { key: '/staff', label: <Link to="/staff">人员列表</Link> },
      { key: '/budgets', label: <Link to="/budgets">预算概览</Link> }
    ]} />
  )
}

export default SideMenu