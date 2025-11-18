import { ConfigProvider, Layout } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import TopNav from './layout/TopNav'
import SideMenu from './layout/SideMenu'
import StoreProvider from './providers/StoreProvider'
import { AuthProvider } from './providers/AuthProvider'
import RequireAuth from './router/RequireAuth'
import Login from '@/modules/auth/pages/Login'
import Profile from '@/modules/auth/pages/Profile'
import PreplanList from '@/modules/preplans/pages/List'
import PreplanDetail from '@/modules/preplans/pages/Detail'
import PreplanEdit from '@/modules/preplans/pages/Edit'
import FlowList from '@/modules/flows/pages/List'
import FlowEdit from '@/modules/flows/pages/Edit'
import VenueList from '@/modules/venues/pages/List'
import VenueDetail from '@/modules/venues/pages/Detail'
import VenueEdit from '@/modules/venues/pages/Edit'
import StaffList from '@/modules/staff/pages/List'
import StaffDetail from '@/modules/staff/pages/Detail'
import StaffEdit from '@/modules/staff/pages/Edit'
import BudgetList from '@/modules/budgets/pages/List'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <StoreProvider>
        <AuthProvider>
        <BrowserRouter>
          <Layout style={{ minHeight: '100%' }}>
            <Layout.Header style={{ padding: 0 }}>
              <TopNav />
            </Layout.Header>
            <Layout>
              <Layout.Sider width={200}>
                <SideMenu />
              </Layout.Sider>
              <Layout.Content style={{ padding: 24 }}>
                <Routes>
                  <Route path="/" element={<Navigate to="/preplans" replace />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/me" element={<RequireAuth><Profile /></RequireAuth>} />
                  <Route path="/preplans" element={<RequireAuth><PreplanList /></RequireAuth>} />
                  <Route path="/preplans/:id" element={<PreplanDetail />} />
                  <Route path="/preplans/new" element={<RequireAuth><PreplanEdit /></RequireAuth>} />
                  <Route path="/preplans/:id/edit" element={<RequireAuth><PreplanEdit /></RequireAuth>} />
                  <Route path="/flows" element={<RequireAuth><FlowList /></RequireAuth>} />
                  <Route path="/flows/new" element={<RequireAuth><FlowEdit /></RequireAuth>} />
                  <Route path="/flows/:id/edit" element={<RequireAuth><FlowEdit /></RequireAuth>} />
                  <Route path="/venues" element={<RequireAuth><VenueList /></RequireAuth>} />
                  <Route path="/venues/:id" element={<RequireAuth><VenueDetail /></RequireAuth>} />
                  <Route path="/venues/new" element={<RequireAuth><VenueEdit /></RequireAuth>} />
                  <Route path="/venues/:id/edit" element={<RequireAuth><VenueEdit /></RequireAuth>} />
                  <Route path="/staff" element={<RequireAuth><StaffList /></RequireAuth>} />
                  <Route path="/staff/:id" element={<RequireAuth><StaffDetail /></RequireAuth>} />
                  <Route path="/staff/:id/edit" element={<RequireAuth><StaffEdit /></RequireAuth>} />
                  <Route path="/budgets" element={<RequireAuth><BudgetList /></RequireAuth>} />
                </Routes>
              </Layout.Content>
            </Layout>
          </Layout>
        </BrowserRouter>
        </AuthProvider>
      </StoreProvider>
    </ConfigProvider>
  )
}

export default App