<template>
  <div class="role-list">
    <div class="header-actions">
      <h2>角色权限管理</h2>
      <a-alert message="勾选对应复选框以修改角色权限" type="info" show-icon />
    </div>

    <a-table 
      :columns="columns" 
      :data-source="permissions" 
      :loading="loading" 
      row-key="code"
      :pagination="false"
      bordered
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'module'">
          <a-tag color="blue">{{ record.module }}</a-tag>
        </template>
        
        <!-- Dynamic Role Columns -->
        <template v-else-if="roles.some(r => r.code === column.key)">
          <a-checkbox 
            :checked="hasPermission(column.key, record.code)"
            :disabled="updatingRole === column.key"
            @change="(e: any) => handlePermissionChange(column.key, record.code, e.target.checked)"
          />
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { getPermissions, getPermissionMatrix, updateRolePermissions, type Permission } from '../../api/modules/permissions'
import { getRoles, type Role } from '../../api/modules/users'

const permissions = ref<Permission[]>([])
const roles = ref<Role[]>([])
const matrix = ref<Record<string, string[]>>({})
const loading = ref(false)
const updatingRole = ref<string | null>(null)

// Base columns
const baseColumns = [
  { title: '模块', dataIndex: 'module', key: 'module', width: 100 },
  { title: '权限名称', dataIndex: 'name', key: 'name', width: 150 },
  { title: '描述', dataIndex: 'description', key: 'description' }
]

// Dynamic columns including roles
const columns = computed(() => {
  const roleColumns = roles.value.map(role => ({
    title: role.name,
    key: role.code,
    dataIndex: role.code,
    align: 'center',
    width: 120
  }))
  return [...baseColumns, ...roleColumns]
})

function hasPermission(roleCode: string, permissionCode: string) {
  return matrix.value[roleCode]?.includes(permissionCode) || false
}

async function handlePermissionChange(roleCode: string, permissionCode: string, checked: boolean) {
  if (updatingRole.value) return
  updatingRole.value = roleCode

  try {
    // Calculate new permissions for this role
    const currentPerms = matrix.value[roleCode] || []
    let newPerms: string[]
    
    if (checked) {
      newPerms = [...currentPerms, permissionCode]
    } else {
      newPerms = currentPerms.filter(p => p !== permissionCode)
    }

    // Call API
    await updateRolePermissions(roleCode, newPerms)
    
    // Update local state
    matrix.value[roleCode] = newPerms
    message.success('权限更新成功')
  } catch (err: any) {
    message.error(err.message || '更新权限失败')
  } finally {
    updatingRole.value = null
  }
}

async function loadData() {
  loading.value = true
  try {
    const [permsRes, rolesRes, matrixRes] = await Promise.all([
      getPermissions(),
      getRoles(),
      getPermissionMatrix()
    ])
    permissions.value = permsRes
    roles.value = rolesRes
    matrix.value = matrixRes
  } catch (err) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.role-list {
  padding: 24px;
}
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
