<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider breakpoint="lg" collapsible>
      <div style="height:48px;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600">Wedding Admin</div>
      <a-menu theme="dark" :selectedKeys="[selectedKey]" mode="inline" @click="onMenu">
        <template v-for="m in menusPermitted" :key="m.key">
          <a-sub-menu v-if="m.children" :key="m.key" :title="m.label">
            <a-menu-item v-for="child in m.children" :key="child.key">
              {{ child.label }}
            </a-menu-item>
          </a-sub-menu>
          <a-menu-item v-else :key="m.key">
            {{ m.label }}
          </a-menu-item>
        </template>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background:#fff;display:flex;justify-content:space-between;align-items:center">
        <div/>
        <div style="display:flex;gap:12px;align-items:center">
          <a-switch :checked="ui.isPresentationMode" @change="ui.togglePresentation" />
          <span>演示模式</span>
          <a-dropdown>
            <a-button>账号</a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="logout">退出登录</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      <a-layout-content style="padding:16px">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUIStore } from '../stores/ui'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const ui = useUIStore()

const selectedKey = computed(() => (route.path.startsWith('/crm') ? 'crm/leads' : route.path.replace(/^\//, '') || 'dashboard'))

const menus = [
  { key: 'dashboard', label: '仪表盘', roles: ['ADMIN','MANAGER','PLANNER','FINANCE'] },
  { key: 'crm/leads', label: '线索/CRM', roles: ['ADMIN','MANAGER','PLANNER'] },
  { key: 'projects', label: '项目中心', roles: ['ADMIN','MANAGER','PLANNER'] },
  { key: 'approvals', label: '审批流', roles: ['ADMIN','MANAGER','PLANNER'] },
  {
    key: 'system',
    label: '系统管理',
    roles: ['ADMIN'],
    children: [
      { key: 'system/users', label: '用户管理', roles: ['ADMIN'] },
      { key: 'system/roles', label: '角色权限', roles: ['ADMIN'] },
    ]
  }
]
const menusPermitted = computed(() => menus.filter(m => !auth.user?.role || m.roles.includes(auth.user.role)))

function onMenu(e: any) {
  router.push('/' + e.key)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
