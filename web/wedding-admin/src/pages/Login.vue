<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <h2 class="title">Wedding Admin</h2>
        <p class="subtitle">婚礼SaaS管理系统</p>
      </div>
      <a-card :bordered="false" class="login-card">
        <a-form
          layout="vertical"
          :model="formState"
          @finish="onSubmit"
          @finishFailed="onFinishFailed"
        >
          <a-form-item
            label="用户名"
            name="username"
            :rules="[{ required: true, message: '请输入用户名' }]"
          >
            <a-input 
              v-model:value="formState.username" 
              placeholder="请输入用户名/邮箱" 
              size="large"
              aria-label="用户名"
            />
          </a-form-item>
          
          <a-form-item
            label="密码"
            name="password"
            :rules="[{ required: true, message: '请输入密码' }]"
          >
            <a-input-password 
              v-model:value="formState.password" 
              placeholder="请输入密码" 
              size="large"
              aria-label="密码"
            />
          </a-form-item>

          <div class="login-options">
            <a-checkbox v-model:checked="formState.remember">记住我</a-checkbox>
            <a class="forgot-password" href="#" @click.prevent="onForgotPassword">忘记密码？</a>
          </div>

          <a-form-item class="submit-btn">
            <a-button type="primary" html-type="submit" block :loading="loading" :disabled="isLocked" size="large">
              {{ isLocked ? '请稍后重试' : '登录' }}
            </a-button>
          </a-form-item>
          
          <a-alert v-if="errorMessage" :message="errorMessage" type="error" show-icon class="error-alert" />
        </a-form>
      </a-card>
      <div class="login-footer">
        <span>© 2025 Wedding SaaS Inc.</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { message } from 'ant-design-vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formState = reactive({
  username: '',
  password: '',
  remember: false
})

const loading = ref(false)
const errorMessage = ref('')
const failedAttempts = ref(0)
const isLocked = ref(false)

onMounted(() => {
  const savedUser = localStorage.getItem('remembered_user')
  if (savedUser) {
    formState.username = savedUser
    formState.remember = true
  }
})

async function onSubmit(values: any) {
  if (isLocked.value) return
  
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login(values.username, values.password)
    
    // Reset failures on success
    failedAttempts.value = 0
    
    if (formState.remember) {
      localStorage.setItem('remembered_user', values.username)
    } else {
      localStorage.removeItem('remembered_user')
    }

    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
    message.success('登录成功')
  } catch (err: any) {
    console.error(err)
    failedAttempts.value++
    
    if (failedAttempts.value >= 5) {
      isLocked.value = true
      errorMessage.value = '尝试次数过多，请 1 分钟后再试'
      setTimeout(() => {
        isLocked.value = false
        failedAttempts.value = 0
        errorMessage.value = ''
      }, 60000)
    } else {
      if (err.code === 401 || err.response?.status === 401) {
        errorMessage.value = `用户名或密码错误 (剩余尝试次数: ${5 - failedAttempts.value})`
      } else {
        errorMessage.value = err.message || '登录失败，请稍后重试'
      }
    }
  } finally {
    loading.value = false
  }
}

function onFinishFailed(errorInfo: any) {
  console.log('Failed:', errorInfo)
}

function onForgotPassword() {
  message.info('请联系管理员重置密码')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  background-image: url('https://gw.alipayobjects.com/zos/rmsportal/TVYTbAXWheQpRcWDaDMu.svg');
  background-repeat: no-repeat;
  background-position: center 110px;
  background-size: 100%;
}

.login-content {
  width: 100%;
  max-width: 400px;
  padding: 24px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 33px;
  color: rgba(0, 0, 0, 0.85);
  font-family: Avenir, 'Helvetica Neue', Arial, Helvetica, sans-serif;
  font-weight: 600;
  margin-bottom: 12px;
}

.subtitle {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
}

.login-card {
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16), 0 3px 6px 0 rgba(0, 0, 0, 0.12), 0 5px 12px 4px rgba(0, 0, 0, 0.09);
  border-radius: 8px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.forgot-password {
  color: #1890ff;
}

.submit-btn {
  margin-bottom: 12px;
}

.error-alert {
  margin-top: 12px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  color: rgba(0, 0, 0, 0.45);
}

@media (max-width: 576px) {
  .login-content {
    width: 95%;
    padding: 16px;
  }
}
</style>

