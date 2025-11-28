<template>
  <div class="user-list">
    <div class="header-actions">
      <h2>用户管理</h2>
      <a-button type="primary" @click="showCreateModal">新增用户</a-button>
    </div>

    <a-table :columns="columns" :data-source="users" :loading="loading" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'roles'">
          <a-tag v-for="roleCode in record.roles" :key="roleCode" :color="getRoleColor(roleCode)">
            {{ getRoleName(roleCode) }}
          </a-tag>
        </template>
        <template v-if="column.key === 'is_active'">
          <a-badge :status="record.is_active ? 'success' : 'error'" :text="record.is_active ? '启用' : '禁用'" />
        </template>
        <template v-if="column.key === 'actions'">
          <a-space>
            <a-button type="link" size="small" @click="editUser(record)">编辑</a-button>
            <a-popconfirm
              title="确定要删除此用户吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="handleDelete(record)"
            >
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- Create/Edit Modal -->
    <a-modal
      v-model:visible="modalVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      @ok="handleModalOk"
      :confirmLoading="modalLoading"
    >
      <a-form layout="vertical" :model="formState" ref="formRef">
        <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="formState.username" :disabled="isEdit" />
        </a-form-item>
        
        <a-form-item 
          label="密码" 
          name="password" 
          :rules="[{ required: !isEdit, message: '请输入密码' }]"
        >
          <a-input-password v-model:value="formState.password" :placeholder="isEdit ? '留空则不修改' : '请输入密码'" />
        </a-form-item>

        <a-form-item label="角色" name="roles" :rules="[{ required: true, message: '请选择角色' }]">
          <a-select v-model:value="formState.roles" mode="multiple" placeholder="请选择角色">
            <a-select-option v-for="role in availableRoles" :key="role.code" :value="role.code">
              {{ role.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="状态" name="is_active">
          <a-switch v-model:checked="formState.is_active" checked-children="启用" un-checked-children="禁用" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { message } from 'ant-design-vue'
import { getUsers, createUser, updateUser, deleteUser, getRoles, type User, type Role } from '../../api/modules/users'

const users = ref<User[]>([])
const availableRoles = ref<Role[]>([])
const loading = ref(false)
const modalVisible = ref(false)
const modalLoading = ref(false)
const isEdit = ref(false)
const currentId = ref('')

const formRef = ref()
const formState = reactive({
  username: '',
  password: '',
  roles: [] as string[],
  is_active: true
})

const columns = [
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '角色', key: 'roles', dataIndex: 'roles' },
  { title: '状态', key: 'is_active', dataIndex: 'is_active' },
  { title: '操作', key: 'actions' }
]

function getRoleColor(role: string) {
  const colors: Record<string, string> = {
    ADMIN: 'red',
    MANAGER: 'orange',
    PLANNER: 'blue',
    FINANCE: 'green',
    VENDOR: 'cyan'
  }
  return colors[role] || 'default'
}

function getRoleName(roleCode: string) {
  const role = availableRoles.value.find(r => r.code === roleCode)
  return role ? role.name : roleCode
}

async function loadData() {
  loading.value = true
  try {
    const [usersRes, rolesRes] = await Promise.all([getUsers(), getRoles()])
    users.value = usersRes
    availableRoles.value = rolesRes
  } catch (err) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

function showCreateModal() {
  isEdit.value = false
  currentId.value = ''
  formState.username = ''
  formState.password = ''
  formState.roles = ['PLANNER']
  formState.is_active = true
  modalVisible.value = true
}

function editUser(user: User) {
  isEdit.value = true
  currentId.value = user.id
  formState.username = user.username
  formState.password = '' // Don't show password
  formState.roles = [...user.roles]
  formState.is_active = user.is_active
  modalVisible.value = true
}

async function handleDelete(user: User) {
  try {
    await deleteUser(user.id)
    message.success('删除成功')
    loadData()
  } catch (err: any) {
    message.error(err.message || '删除失败')
  }
}

async function handleModalOk() {
  try {
    await formRef.value.validate()
    modalLoading.value = true
    
    if (isEdit.value) {
      await updateUser(currentId.value, {
        roles: formState.roles,
        is_active: formState.is_active,
        ...(formState.password ? { password: formState.password } : {})
      })
      message.success('更新成功')
    } else {
      await createUser({
        username: formState.username,
        password: formState.password,
        roles: formState.roles,
        is_active: formState.is_active
      })
      message.success('创建成功')
    }
    
    modalVisible.value = false
    loadData()
  } catch (err: any) {
    if (err.errorFields) return // Form validation error
    message.error(err.message || '操作失败')
  } finally {
    modalLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.user-list {
  padding: 24px;
}
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
