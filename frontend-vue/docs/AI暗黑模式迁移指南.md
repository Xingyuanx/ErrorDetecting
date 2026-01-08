# AI 暗黑模式 (Dark Mode) 迁移指南

本文档为 AI 助手设计，旨在通过结构化的步骤将 `frontend-vue` 项目从硬编码配色迁移至支持响应式切换的暗黑模式架构。

---

## 1. 核心任务目标
将项目中分散在各个 `.vue` 文件 `<style>` 块中的硬编码颜色（Hex/RGB）统一提取为 CSS 变量，并基于 `.dark` 类名实现暗黑主题覆盖。

---

## 2. 语义化变量映射表 (Context for AI)

在迁移时，请遵循以下映射逻辑：

| 语义类别 | 浅色模式 (当前值) | 暗黑模式 (目标值) | CSS 变量名 |
| :--- | :--- | :--- | :--- |
| 品牌主色 | `#0ea5e9` | `#0ea5e9` | `--el-color-primary` |
| 页面背景 | `#f0f9ff` | `#0f172a` | `--app-bg` |
| 内容区背景 | `#f8fafc` | `#1e293b` | `--app-content-bg` |
| 卡片/容器背景 | `#ffffff` | `#1e293b` | `--app-card-bg` |
| 顶部导航背景 | `#ffffff` | `#0f172a` | `--app-header-bg` |
| 主要文字 | `#1f2937` | `#f1f5f9` | `--app-text-primary` |
| 次要文字 | `#6b7280` | `#94a3b8` | `--app-text-secondary` |
| 边框颜色 | `#e2e8f0` | `#334155` | `--app-border-color` |

---

## 3. 实施路径 (Implementation Steps)

### 第一步：全局变量定义
在 [App.vue](file:///home/devbox/project/frontend-vue/src/app/App.vue) 或新建 `src/app/styles/vars.css` 中定义基础变量：

```css
:root {
  --app-bg: #f0f9ff;
  --app-content-bg: #f8fafc;
  --app-card-bg: #ffffff;
  --app-header-bg: #ffffff;
  --app-text-primary: #1f2937;
  --app-text-secondary: #6b7280;
  --app-border-color: #e2e8f0;
}

html.dark {
  --app-bg: #0f172a;
  --app-content-bg: #1e293b;
  --app-card-bg: #1e293b;
  --app-header-bg: #0f172a;
  --app-text-primary: #f1f5f9;
  --app-text-secondary: #94a3b8;
  --app-border-color: #334155;
}
```

### 第二步：Element Plus 适配
在 [main.ts](file:///home/devbox/project/frontend-vue/src/app/main.ts) 中引入官方暗黑样式：
```typescript
import 'element-plus/theme-chalk/dark/css-vars.css'
```

### 第三步：状态切换逻辑
在 [ui.ts](file:///home/devbox/project/frontend-vue/src/app/stores/ui.ts) 中集成 `@vueuse/core`：
```typescript
import { useDark, useToggle } from '@vueuse/core'

export const useUIStore = defineStore('ui', {
  state: () => ({
    isDark: useDark(),
    // ... 其他状态
  }),
  actions: {
    toggleTheme() {
      const toggle = useToggle(this.isDark)
      toggle()
    }
  }
})
```

### 第四步：清理硬编码颜色 (重点)
遍历以下关键文件，将 hardcoded color 替换为变量：
- **[App.vue](file:///home/devbox/project/frontend-vue/src/app/App.vue)**: 替换 `body` 的 `background-color`。
- **[Diagnosis.vue](file:///home/devbox/project/frontend-vue/src/app/views/Diagnosis.vue)**: 替换所有 `#1f2937`、`#6b7280` 和背景色。
- **[Sidebar.vue](file:///home/devbox/project/frontend-vue/src/app/components/Sidebar.vue)**: 确保侧边栏在暗黑模式下不再使用固定的 `#001529`。

---

## 4. AI 迁移注意事项 (Constraint)

1. **不要遗漏 ECharts**: 监控图表的 `theme` 必须随 `uiStore.isDark` 动态切换。
2. **渐变色处理**: [Login.vue](file:///home/devbox/project/frontend-vue/src/app/views/Login.vue) 中的线性渐变在暗黑模式下需要调整为更深邃的色调。
3. **保持原子性**: 每次修改一个组件的颜色，并确保该组件在双主题下均渲染正常。
4. **优先使用 Element Plus 变量**: 如果能用 `--el-fill-color` 等官方变量，则优先使用。
