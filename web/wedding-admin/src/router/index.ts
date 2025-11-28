import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const Login = () => import('../pages/Login.vue')
const AdminLayout = () => import('../layouts/AdminLayout.vue')
const Dashboard = () => import('../pages/Dashboard.vue')
const LeadsList = () => import('../pages/crm/LeadsList.vue')
const ProjectList = () => import('../pages/projects/ProjectList.vue')
const ProjectDetail = () => import('../pages/projects/ProjectDetail.vue')
const ProposalList = () => import('../pages/projects/ProposalList.vue')
const ProposalEditor = () => import('../pages/projects/ProposalEditor.vue')
const ApprovalsList = () => import('../pages/approvals/ApprovalsList.vue')
const UserList = () => import('../pages/system/UserList.vue')
const RoleList = () => import('../pages/system/RoleList.vue')

export type Role = 'ADMIN' | 'MANAGER' | 'PLANNER' | 'VENDOR' | 'FINANCE'

const routes: RouteRecordRaw[] = [
  { path: '/login', component: Login, meta: { public: true } },
  {
    path: '/',
    component: AdminLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: Dashboard, meta: { roles: ['ADMIN','MANAGER','PLANNER','FINANCE'] as Role[] } },
      { path: 'crm/leads', component: LeadsList, meta: { roles: ['ADMIN','MANAGER','PLANNER'] as Role[] } },
      { path: 'projects', component: ProjectList, meta: { roles: ['ADMIN','MANAGER','PLANNER'] as Role[] } },
      { path: 'projects/:id', component: ProjectDetail, meta: { roles: ['ADMIN','MANAGER','PLANNER'] as Role[] } },
      { path: 'projects/:id/proposals', component: ProposalList, meta: { roles: ['ADMIN','MANAGER','PLANNER'] as Role[] } },
      { path: 'proposals/:id', component: ProposalEditor, meta: { roles: ['ADMIN','MANAGER','PLANNER'] as Role[] } },
      { path: 'approvals', component: ApprovalsList, meta: { roles: ['ADMIN','MANAGER','PLANNER'] as Role[] } },
      // System Management
      { path: 'system/users', component: UserList, meta: { roles: ['ADMIN'] as Role[] } },
      { path: 'system/roles', component: RoleList, meta: { roles: ['ADMIN'] as Role[] } },
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) return true
  if (!auth.token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  const roles = (to.meta as any).roles as Role[] | undefined
  if (roles && auth.user?.role && !roles.includes(auth.user.role as Role)) {
    return { path: '/dashboard' }
  }
  return true
})

export default router

