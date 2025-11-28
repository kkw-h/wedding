<template>
  <a-card title="审批流">
    <a-form layout="inline" @finish="submit">
      <a-form-item label="项目ID">
        <a-input v-model:value="projectId" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit">发起折扣申请</a-button>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createApproval } from '../../api/modules/approvals'

const projectId = ref('')

async function submit() {
  await createApproval({ project_id: projectId.value, type: 'DISCOUNT', content: { original_price: 100000, target_price: 95000, reason: '示例申请' } })
}
</script>

