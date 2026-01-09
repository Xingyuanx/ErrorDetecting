# API 服务层优化指南

本文档旨在为 `frontend-vue` 项目提供一套标准化的前端 API 服务层优化方案。该方案完全基于现有前端代码结构，在**不修改后端任何接口或逻辑**的前提下，提升代码的可维护性、健壮性及用户体验。

---

## 目录
1. [现有 API 调用分析](#1-现有-api-调用分析)
2. [请求封装优化方案 (Service 层)](#2-请求封装优化方案-service-层)
3. [拦截器配置 (自动化 Token 与数据简化)](#3-拦截器配置-自动化-token-与数据简化)
4. [统一错误处理方案](#4-统一错误处理方案)
5. [进阶优化：缓存、重试与监控](#5-进阶优化缓存重试与监控)
6. [兼容性、回滚与迁移指南](#6-兼容性回滚与迁移指南)

---

## 1. 现有 API 调用分析

### 1.1 核心问题
通过对 [Diagnosis.vue](file:///home/devbox/project/frontend-vue/src/app/views/Diagnosis.vue) 和 [ClusterList.vue](file:///home/devbox/project/frontend-vue/src/app/views/ClusterList.vue) 的分析，发现以下痛点：

*   **冗余代码**：每个请求都手动携带 Headers。
    ```typescript
    // ClusterList.vue 示例
    await api.get('/v1/clusters', { 
      headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined 
    })
    ```
*   **类型安全缺失**：大量使用 `any`，无法利用 TypeScript 的自动补全和编译检查。
*   **逻辑耦合**：API 路径、参数构造与 UI 逻辑混杂在一起，难以复用。
*   **分散的错误处理**：每个组件都在重复编写类似的 `try-catch` 和错误格式化逻辑。

---

## 2. 请求封装优化方案 (Service 层)

### 2.1 优化方案
引入 **Service 层**，将 API 调用从组件中解耦。

### 2.2 代码示例
创建 `src/app/api/cluster.service.ts`：

```typescript
import api from '../lib/api';
import { Cluster, ClusterRegisterPayload } from '../types/cluster';

export const ClusterService = {
  /** 获取集群列表 */
  async getAll(): Promise<Cluster[]> {
    const { data } = await api.get<{ clusters: Cluster[] }>('/v1/clusters');
    return data.clusters;
  },

  /** 注册新集群 */
  async register(payload: ClusterRegisterPayload): Promise<void> {
    await api.post('/v1/clusters', payload);
  }
};
```

### 2.3 对比效果
*   **优化前**：组件负责构造 URL、处理 Headers、转换类型。
*   **优化后**：组件仅需一行调用 `const list = await ClusterService.getAll()`。

> [!IMPORTANT]
> **关键点**：Service 层必须返回经过类型定义的 `Promise`，以确保下游调用者的类型安全。

---

## 3. 拦截器配置 (自动化 Token 与数据简化)

### 3.1 优化方案
在 [api.ts](file:///home/devbox/project/frontend-vue/src/app/lib/api.ts) 中配置拦截器。

### 3.2 请求拦截器：自动注入 Token
```typescript
api.interceptors.request.use(config => {
  const auth = useAuthStore();
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`;
  }
  return config;
});
```

### 3.3 响应拦截器：数据简化
```typescript
api.interceptors.response.use(
  response => response.data, // 直接返回 data 字段
  error => Promise.reject(error)
);
```

---

## 4. 统一错误处理方案

### 4.1 优化方案
将原本分散在各组件的 `formatError` 逻辑移至响应拦截器。

### 4.2 代码示例
```typescript
api.interceptors.response.use(
  res => res,
  error => {
    const status = error.response?.status;
    let message = "系统繁忙，请稍后再试";

    if (status === 401) {
      message = "登录已过期";
      useAuthStore().logout();
      window.location.hash = '#/login';
    } else if (status === 403) {
      message = "无权访问此资源";
    }

    // 触发全局提示（需配合 UI 组件）
    // Notification.error(message); 
    return Promise.reject({ ...error, friendlyMessage: message });
  }
);
```

---

## 5. 进阶优化：缓存、重试与监控

### 5.1 接口缓存策略
对于不常变动的数据（如集群列表、角色常量），增加内存缓存。
```typescript
const cache = new Map();
export const CachedClusterService = {
  async getAll() {
    if (cache.has('clusters')) return cache.get('clusters');
    const data = await ClusterService.getAll();
    cache.set('clusters', data);
    return data;
  }
};
```

### 5.2 请求重试机制 (Exponential Backoff)
针对网络波动导致的失败，在拦截器中增加重试逻辑。
```typescript
// 使用 axios-retry 插件或手动实现
if (error.config && error.config.retryCount < 3) {
  error.config.retryCount++;
  return api(error.config);
}
```

### 5.3 性能监控埋点
记录每个 API 的响应耗时，便于定位性能瓶颈。
```typescript
api.interceptors.request.use(config => {
  config.metadata = { startTime: new Date() };
  return config;
});

api.interceptors.response.use(response => {
  const duration = new Date() - response.config.metadata.startTime;
  console.log(`API [${response.config.url}] 耗时: ${duration}ms`);
  return response;
});
```

---

## 6. 兼容性、回滚与迁移指南

### 6.1 100% 后端兼容性保证
*   **原则**：所有重构仅改变前端封装形式，不改变 HTTP 报文。
*   **验证**：重构后对比 Chrome DevTools 中的 `Network` 面板，确保 `Request URL`, `Method`, `Headers` 与重构前完全一致。

### 6.2 回滚方案
1.  **保留旧实例**：不要直接删除原有的 [api.ts](file:///home/devbox/project/frontend-vue/src/app/lib/api.ts) 逻辑，而是创建 `api_v2.ts`。
2.  **逐组件切换**：若新版 Service 出现问题，只需将组件内的导入改回原有的 `api` 即可。

### 6.3 版本迁移指南
1.  **Phase 1**: 创建 `src/app/types/` 定义所有业务接口。
2.  **Phase 2**: 升级 `api.ts` 引入拦截器（建议先只引入 Token 注入）。
3.  **Phase 3**: 编写 Service 层，先从 [ClusterList.vue](file:///home/devbox/project/frontend-vue/src/app/views/ClusterList.vue) 开始试点重构。
4.  **Phase 4**: 移除组件内所有手动 Headers 处理。

---

> [!WARNING]
> **警示**：在重构过程中，切勿修改 `baseURL` 或请求路径的前缀，否则将导致反向代理失效。
