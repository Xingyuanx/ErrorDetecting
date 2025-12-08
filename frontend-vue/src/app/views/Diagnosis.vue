<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">故障诊断</h2></div>
    <div class="diag-container">
      <div id="diag-left" class="diag-pane diag-pane--left">
        <div draggable="true" class="btn diag-log-btn" data-log="示例日志 A">示例日志 A</div>
        <div draggable="true" class="btn diag-log-btn" data-log="示例日志 B">示例日志 B</div>
      </div>
      <div id="diag-divider-1" class="diag-divider"></div>
      <div id="diag-middle" class="diag-pane diag-pane--mid">
        <div class="u-text-sm u-text-gray-700">选择左侧日志或节点，预览内容显示于右侧</div>
        <div id="diag-live-logs-list" style="margin-top:8px"></div>
      </div>
      <div id="diag-divider-2" class="diag-divider"></div>
      <div id="diag-right" class="diag-pane diag-pane--right">
        <textarea id="chat-input" class="diag-chat"></textarea>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
onMounted(() => {
  const input = document.getElementById('chat-input') as HTMLTextAreaElement|null
  if (input) {
    input.addEventListener('dragover', e => e.preventDefault())
    input.addEventListener('drop', e => { e.preventDefault(); const d = (e as DragEvent).dataTransfer?.getData('text/plain')||''; input.value = `${input.value}\n${d}`.trim() })
  }
  const left = document.getElementById('diag-left') as HTMLElement|null
  const mid = document.getElementById('diag-middle') as HTMLElement|null
  const right = document.getElementById('diag-right') as HTMLElement|null
  const d1 = document.getElementById('diag-divider-1') as HTMLElement|null
  const d2 = document.getElementById('diag-divider-2') as HTMLElement|null
  if (!left || !mid || !right || !d1 || !d2) return
  let drag1 = false, drag2 = false, startX1 = 0, startX2 = 0
  let leftW = left.getBoundingClientRect().width
  let midW = mid.getBoundingClientRect().width
  let rightW = right.getBoundingClientRect().width
  const minLeft = 240, minMid = 300, minRight = 320
  const onMove1 = (e: MouseEvent) => {
    if (!drag1) return
    const dx = e.clientX - startX1
    const newLeft = Math.max(minLeft, leftW + dx)
    const delta = newLeft - leftW
    const newMid = Math.max(minMid, midW - delta)
    left.style.width = `${newLeft}px`
    mid.style.width = `${newMid}px`
  }
  const onUp1 = () => {
    drag1 = false
    leftW = left.getBoundingClientRect().width
    midW = mid.getBoundingClientRect().width
    document.removeEventListener('mousemove', onMove1)
    document.removeEventListener('mouseup', onUp1)
  }
  d1.addEventListener('mousedown', (e) => {
    drag1 = true
    startX1 = (e as MouseEvent).clientX
    leftW = left.getBoundingClientRect().width
    midW = mid.getBoundingClientRect().width
    document.addEventListener('mousemove', onMove1)
    document.addEventListener('mouseup', onUp1)
  })
  const onMove2 = (e: MouseEvent) => {
    if (!drag2) return
    const dx = startX2 - e.clientX
    const newRight = Math.max(minRight, rightW + dx)
    const delta = newRight - rightW
    const newMid = Math.max(minMid, midW - delta)
    right.style.width = `${newRight}px`
    mid.style.width = `${newMid}px`
  }
  const onUp2 = () => {
    drag2 = false
    rightW = right.getBoundingClientRect().width
    midW = mid.getBoundingClientRect().width
    document.removeEventListener('mousemove', onMove2)
    document.removeEventListener('mouseup', onUp2)
  }
  d2.addEventListener('mousedown', (e) => {
    drag2 = true
    startX2 = (e as MouseEvent).clientX
    rightW = right.getBoundingClientRect().width
    midW = mid.getBoundingClientRect().width
    document.addEventListener('mousemove', onMove2)
    document.addEventListener('mouseup', onUp2)
  })
})
</script>

<style>
.diag-container { display:flex; gap:0; height:480px }
.diag-pane { border:1px solid #e5e7eb; overflow:auto }
.diag-pane--left { width: 320px }
.diag-pane--mid { flex: 1; min-width: 300px; padding: 8px }
.diag-pane--right { width: 380px; display:flex; flex-direction:column }
.diag-divider { width:6px; background:#e5e7eb; cursor: col-resize }
.diag-chat { flex:1; padding:8px }
</style>
