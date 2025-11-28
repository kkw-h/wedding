<template>
  <div class="proposal-editor">
    <a-page-header
      :title="proposal?.name || 'Loading...'"
      :sub-title="saveStatus"
      @back="$router.back()"
    >
      <template #extra>
        <a-button @click="showHistory = true">版本历史</a-button>
        <a-button type="primary" @click="saveVersion">发布版本</a-button>
      </template>
    </a-page-header>

    <div class="editor-content" v-if="proposal">
      <a-row :gutter="16">
        <a-col :span="18">
          <a-card title="方案内容编辑" :bodyStyle="{ padding: 0 }">
            <div style="border: 1px solid #ccc; z-index: 1000">
              <Toolbar
                style="border-bottom: 1px solid #ccc"
                :editor="editorRef"
                :defaultConfig="toolbarConfig"
                :mode="mode"
              />
              <Editor
                style="height: 600px; overflow-y: hidden;"
                v-model="valueHtml"
                :defaultConfig="editorConfig"
                :mode="mode"
                @onCreated="handleCreated"
                @onChange="onContentChange"
              />
            </div>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card title="方案信息">
            <p><strong>描述:</strong> {{ proposal.description }}</p>
            <p>
              <strong>状态:</strong>
              <a-select 
                v-if="proposal" 
                v-model:value="proposal.status" 
                style="width: 120px; margin-left: 8px" 
                @change="handleStatusChange"
              >
                <a-select-option v-for="(label, key) in statusMap" :key="key" :value="key">
                  {{ label }}
                </a-select-option>
              </a-select>
            </p>
            <p><strong>创建人:</strong> {{ proposal.creator?.username || proposal.created_by }}</p>
            <p><strong>创建时间:</strong> {{ proposal.created_at }}</p>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <a-drawer
      v-model:open="showHistory"
      title="版本历史"
      placement="right"
      width="400"
    >
      <a-timeline>
        <a-timeline-item v-for="v in versions" :key="v.id" color="blue">
          <p>
            <strong v-if="v.version_number">v{{ v.version_number }} </strong>
            <span v-if="v.change_type" style="margin-left: 8px; font-size: 12px; color: #999">
              {{ v.change_type === 'MAJOR' ? '重大修改' : '微调' }}
            </span>
          </p>
          <p v-if="v.change_log?.summary" style="color: #666; margin: 4px 0">
            备注: {{ v.change_log.summary }}
          </p>
          <p>{{ v.created_at }}</p>
          <p>操作人: {{ v.editor_id }}</p>
          <a-space>
            <a-button size="small" @click="restore(v)">恢复此版本</a-button>
          </a-space>
        </a-timeline-item>
      </a-timeline>
    </a-drawer>

    <a-modal v-model:open="versionModalOpen" title="发布新版本" @ok="confirmSaveVersion">
      <a-form layout="vertical">
        <a-form-item label="修改类型" required>
          <a-radio-group v-model:value="versionForm.changeType">
            <a-radio value="MAJOR">重大修改</a-radio>
            <a-radio value="MINOR">微调</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="本次提交版本号" required>
          <a-input v-model:value="nextVersionNumber" disabled placeholder="系统自动生成" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="versionForm.changeLog" placeholder="修改摘要" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, shallowRef, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  getProposal, updateProposal, getVersions, createVersion, restoreVersion,
  ProposalItem, ProposalVersion 
} from '../../api/modules/proposals'
import { message } from 'ant-design-vue'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'

const statusMap: Record<string, string> = {
  'DRAFT': '草稿',
  'ACTIVE': '进行中',
  'SELECTED': '已定稿',
  'ARCHIVED': '已归档'
}

function debounce(func: Function, wait: number) {
  let timeout: any
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

const route = useRoute()
const proposalId = route.params.id as string

const proposal = ref<ProposalItem | null>(null)
const saveStatus = ref('Ready')
const showHistory = ref(false)
const versions = ref<ProposalVersion[]>([])

// Editor setup
const editorRef = shallowRef()
const valueHtml = ref('<p>开始编辑方案...</p>')
const mode = 'default'
const toolbarConfig = {}
const editorConfig = { placeholder: '请输入内容...' }

const handleCreated = (editor: any) => {
  editorRef.value = editor
}

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

// Auto-save logic
const autoSave = debounce(async () => {
  if (!proposal.value) return
  saveStatus.value = 'Saving...'
  try {
    // Store as JSON object containing HTML
    const data = { html: valueHtml.value }
    
    await updateProposal(proposalId, { current_data: data })
    saveStatus.value = 'Saved'
  } catch (e) {
    saveStatus.value = 'Save Failed'
  }
}, 2000)

async function handleStatusChange(status: string) {
  try {
    await updateProposal(proposalId, { status })
    message.success('状态更新成功')
  } catch (e: any) {
    message.error('状态更新失败: ' + e.message)
    // revert change if needed, but for now simple error message
    load() // reload to reset status
  }
}

function onContentChange() {
  saveStatus.value = 'Unsaved changes...'
  autoSave()
}

async function load() {
  try {
    const p = await getProposal(proposalId)
    proposal.value = p
    
    // Parse current_data
    if (p.current_data && typeof p.current_data === 'object' && p.current_data.html) {
        valueHtml.value = p.current_data.html
    } else {
        // Fallback or empty
        valueHtml.value = '<p>开始编辑方案...</p>'
    }

    const v = await getVersions(proposalId)
    versions.value = v
  } catch (e: any) {
    message.error('加载失败: ' + e.message)
  }
}

// Version Control
const versionModalOpen = ref(false)
const versionForm = ref({ changeLog: '', changeType: 'MINOR' as 'MAJOR' | 'MINOR' })

const nextVersionNumber = computed(() => {
  const latest = versions.value.length > 0 ? versions.value[0] : null
  const currentVersion = latest?.version_number || '1.0'
  
  if (!latest) return '1.0'
  
  const [major, minor] = currentVersion.split('.').map(Number)
  if (versionForm.value.changeType === 'MAJOR') {
    return `${major + 1}.0`
  } else {
    return `${major}.${minor + 1}`
  }
})

function saveVersion() {
  versionForm.value = { changeLog: '', changeType: 'MINOR' }
  versionModalOpen.value = true
}

async function confirmSaveVersion() {
  try {
    const data = { html: valueHtml.value }
    await createVersion(proposalId, {
      snapshot_data: data,
      change_log: { summary: versionForm.value.changeLog },
      action_type: 'MANUAL_SAVE',
      change_type: versionForm.value.changeType
    })
    message.success('版本发布成功')
    versionModalOpen.value = false
    // Refresh versions
    versions.value = await getVersions(proposalId)
  } catch (e: any) {
    message.error('发布失败: ' + e.message)
  }
}

async function restore(v: ProposalVersion) {
  try {
    await restoreVersion(proposalId, v.id)
    message.success('恢复成功')
    
    // Manually update editor content since we just restored
    // The restoreVersion API updates the DB, we need to reload or just update local state
    // To ensure consistency, let's reload
    await load()
    showHistory.value = false
  } catch (e: any) {
    message.error('恢复失败: ' + e.message)
  }
}

onMounted(load)
</script>

<style scoped>
.proposal-editor {
  padding: 24px;
}
</style>
