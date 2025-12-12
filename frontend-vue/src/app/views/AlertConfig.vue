<template>
  <section class="layout__section">
    <div class="layout__page-header exec-header">
      <div>
        <h2 class="layout__page-title">告警配置（原型）</h2>
        <div class="layout__page-subtitle">设置告警规则、通知渠道与阈值</div>
      </div>
      <div class="header-actions"><button class="btn btn--primary" type="button" @click="open=true">新增配置</button></div>
    </div>

    <article class="layout__card u-mt-2">
      <div class="layout__card-header"><h3 class="layout__card-title">通知与阈值</h3></div>
      <div class="layout__card-body">
        <form class="layout__grid layout__grid--3" @submit.prevent>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">告警严重级别</label>
            <select v-model="severity" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option value="INFO">INFO</option>
              <option value="WARN">WARN</option>
              <option value="ERROR">ERROR</option>
            </select>
            <div class="u-mt-2">
              <label class="u-text-sm u-font-medium u-text-gray-700"><input type="checkbox" v-model="enableEmail" class="u-mr-1" />启用邮件通知</label>
            </div>
            <div class="u-mt-1">
              <label class="u-text-sm u-font-medium u-text-gray-700"><input type="checkbox" v-model="enableSms" class="u-mr-1" />启用短信通知</label>
            </div>
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">邮件接收人</label>
            <input v-model.trim="email" class="u-w-full u-p-2 u-border u-rounded u-mt-1" placeholder="ops@example.com" />
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">Webhook 地址</label>
            <input v-model.trim="webhook" class="u-w-full u-p-2 u-border u-rounded u-mt-1" placeholder="https://hooks.example.com/alert" />
            <div class="u-mt-2">
              <label class="u-text-sm u-font-medium u-text-gray-700"><input type="checkbox" v-model="enableWebhook" class="u-mr-1" />启用 Webhook</label>
            </div>
          </div>
        </form>
      </div>
    </article>

    <article class="layout__card u-mt-3">
      <div class="layout__card-header"><h3 class="layout__card-title">规则列表（占位数据）</h3></div>
      <div class="layout__card-body u-p-0">
        <table class="dashboard__table">
          <thead><tr><th>规则名称</th><th>条件</th><th>级别</th><th>通知渠道</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="r in rules" :key="r.name" class="dashboard__table-row">
              <td>{{ r.name }}</td>
              <td>{{ r.cond }}</td>
              <td><span :class="levelClass(r.level)">{{ r.level }}</span></td>
              <td>{{ r.channel }}</td>
              <td><button class="btn u-text-sm" type="button" @click="edit(r)">编辑</button><button class="btn u-text-sm u-ml-1" type="button" @click="del(r.name)">删除</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <article class="layout__card u-mt-3" v-show="open">
      <div class="layout__card-header"><h3 class="layout__card-title">新增配置</h3></div>
      <div class="layout__card-body">
        <form @submit.prevent="save">
          <div class="form-grid">
            <input v-model.trim="form.name" class="header__search-input" placeholder="规则名称" />
            <input v-model.trim="form.cond" class="header__search-input" placeholder="条件描述" />
            <select v-model="form.level" class="header__search-input"><option value="INFO">INFO</option><option value="WARN">WARN</option><option value="ERROR">ERROR</option></select>
            <input v-model.trim="form.channel" class="header__search-input" placeholder="通知渠道，如 邮件 或 邮件+Webhook" />
          </div>
          <div class="u-mt-2"><button class="btn btn--primary" type="submit">保存</button><button class="btn u-ml-1" type="button" @click="open=false">取消</button></div>
          <div class="u-text-sm u-text-gray-700 u-mt-1">{{ err }}</div>
        </form>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
const severity = ref<'INFO'|'WARN'|'ERROR'>('INFO')
const enableEmail = ref(false)
const enableSms = ref(false)
const enableWebhook = ref(false)
const email = ref('ops@example.com')
const webhook = ref('https://hooks.example.com/alert')
const rules = reactive<{ name:string; cond:string; level:'INFO'|'WARN'|'ERROR'; channel:string }[]>([
  { name:'cpu-high-usage', cond:'CPU > 85% 持续 5 分钟', level:'WARN', channel:'邮件' },
  { name:'node-disconnected', cond:'心跳丢失 3 次', level:'ERROR', channel:'邮件 + Webhook' }
])
const open = ref(false)
const err = ref('')
const form = reactive<{ name:string; cond:string; level:'INFO'|'WARN'|'ERROR'; channel:string }>({ name:'', cond:'', level:'INFO', channel:'' })
function levelClass(l:'INFO'|'WARN'|'ERROR'){ return l==='ERROR'?'level--error': l==='WARN'?'level--warn':'level--info' }
function save(){
  if (!form.name || !form.cond) { err.value='请填写规则名称与条件'; return }
  if (rules.some(r => r.name===form.name)) { err.value='规则名称已存在'; return }
  rules.push({ name: form.name, cond: form.cond, level: form.level, channel: form.channel || '邮件' })
  err.value=''; open.value=false; form.name=''; form.cond=''; form.level='INFO'; form.channel=''
}
function del(n:string){ const i = rules.findIndex(r => r.name===n); if (i>=0) rules.splice(i,1) }
function edit(r:any){ open.value=true; form.name=r.name; form.cond=r.cond; form.level=r.level; form.channel=r.channel }
</script>

<style scoped>
.exec-header{ display:flex; justify-content:space-between; align-items:center }
.layout__page-subtitle{ color:#6b7280; font-size:13px }
.layout__card{ background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 8px 24px rgba(16,24,40,0.06) }
.layout__card-header{ padding:12px 16px; border-bottom:1px solid #e5e7eb }
.layout__card-title{ font-size:14px; font-weight:600 }
.layout__card-body{ padding:16px }
.layout__grid{ display:grid; gap:16px }
.layout__grid--3{ grid-template-columns: 1fr 1fr 1fr }
.form-grid{ display:grid; grid-template-columns: repeat(4, 1fr); gap:12px }
.level--info{ color:#2563eb }
.level--warn{ color:#f59e0b }
.level--error{ color:#dc2626 }
</style>
