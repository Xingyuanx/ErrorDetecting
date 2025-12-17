# Hadoop Fault Detecting API 前端联调指南

## 1. 项目概述

### 1.1 后端API服务
- **服务名称**: Hadoop Fault Detecting API
- **基础URL**: `http://localhost:8000/api/v1`
- **技术栈**: FastAPI + Python 3.13
- **文档地址**: 
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`
  - 详细API文档: `docs/api.md`

### 1.2 前端技术栈
- **框架**: Vue 3
- **构建工具**: Vite
- **HTTP客户端**: Axios
- **状态管理**: Pinia/Vuex
- **UI组件库**: Element Plus/Naive UI

## 2. 开发环境搭建

### 2.1 前端开发环境
```bash
# 安装Node.js (推荐使用nvm管理Node.js版本)
nvm install 18
nvm use 18

# 安装Vue CLI或Vite
npm create vite@latest my-vue-app -- --template vue
cd my-vue-app

# 安装依赖
npm install

# 安装Axios
npm install axios

# 启动开发服务器
npm run dev
```

### 2.2 后端开发环境
```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动开发服务器
python -m uvicorn app.main:app --reload
```

## 3. API认证机制

### 3.1 JWT认证流程
1. 前端调用`/user/login`接口，传入用户名和密码
2. 后端验证成功后返回JWT token
3. 前端将token存储在localStorage或Cookie中
4. 每次请求时在Authorization头中携带token
5. 后端验证token的有效性

### 3.2 登录接口示例
```http
POST /user/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "ok": true,
  "username": "admin",
  "fullName": "admin",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 4. Vue项目配置

### 4.1 Axios配置
在`src/utils/axios.js`中配置Axios实例：

```javascript
import axios from 'axios';

// 创建Axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    // 处理错误
    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case 401:
          // 未授权，跳转到登录页
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          // 禁止访问
          console.error('没有权限访问该资源');
          break;
        case 404:
          // 资源不存在
          console.error('请求的资源不存在');
          break;
        case 500:
          // 服务器内部错误
          console.error('服务器内部错误');
          break;
        default:
          console.error('请求失败:', error.response.data.detail);
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      console.error('网络错误，无法连接到服务器');
    } else {
      // 请求配置错误
      console.error('请求配置错误:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 4.2 环境变量配置
在`.env.development`中配置开发环境变量：

```env
# Vite环境变量
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE="Hadoop Fault Detecting"
```

在`.env.production`中配置生产环境变量：

```env
VITE_API_BASE_URL=https://your-production-api-url/api/v1
VITE_APP_TITLE="Hadoop Fault Detecting"
```

## 5. 核心功能模块联调

### 5.1 登录模块

**登录组件示例** (`src/components/LoginForm.vue`):

```vue
<template>
  <div class="login-form">
    <h2>登录</h2>
    <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '../utils/axios';

const loginFormRef = ref();
const loading = ref(false);

const loginForm = reactive({
  username: '',
  password: ''
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
};

const handleLogin = async () => {
  try {
    await loginFormRef.value.validate();
    loading.value = true;
    
    const response = await apiClient.post('/user/login', loginForm);
    
    if (response.ok) {
      // 保存token到localStorage
      localStorage.setItem('token', response.token);
      localStorage.setItem('username', response.username);
      localStorage.setItem('fullName', response.fullName);
      
      ElMessage.success('登录成功');
      // 跳转到首页
      window.location.href = '/';
    } else {
      ElMessage.error('登录失败，请检查用户名和密码');
    }
  } catch (error) {
    ElMessage.error('登录失败: ' + (error.response?.data?.detail || error.message));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-form {
  width: 300px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
```

### 5.2 集群管理模块

**获取集群列表示例** (`src/views/Clusters.vue`):

```vue
<template>
  <div class="clusters-view">
    <h1>集群管理</h1>
    <el-table :data="clusters" style="width: 100%">
      <el-table-column prop="uuid" label="UUID" width="200"></el-table-column>
      <el-table-column prop="host" label="主机名"></el-table-column>
      <el-table-column prop="ip" label="IP地址"></el-table-column>
      <el-table-column prop="count" label="节点数量"></el-table-column>
      <el-table-column prop="health" label="健康状态"></el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../utils/axios';

const clusters = ref([]);

const fetchClusters = async () => {
  try {
    const response = await apiClient.get('/clusters');
    clusters.value = response.clusters;
  } catch (error) {
    console.error('获取集群列表失败:', error);
  }
};

onMounted(() => {
  fetchClusters();
});
</script>
```

### 5.3 节点管理模块

**获取节点列表示例** (`src/views/Nodes.vue`):

```vue
<template>
  <div class="nodes-view">
    <h1>节点管理</h1>
    <el-select v-model="selectedCluster" placeholder="选择集群" @change="fetchNodes">
      <el-option
        v-for="cluster in clusters"
        :key="cluster.uuid"
        :label="cluster.host"
        :value="cluster.uuid"
      ></el-option>
    </el-select>
    
    <el-table :data="nodes" style="width: 100%" v-if="selectedCluster">
      <el-table-column prop="name" label="节点名称"></el-table-column>
      <el-table-column prop="ip" label="IP地址"></el-table-column>
      <el-table-column prop="status" label="状态"></el-table-column>
      <el-table-column prop="cpu" label="CPU使用率"></el-table-column>
      <el-table-column prop="mem" label="内存使用率"></el-table-column>
      <el-table-column prop="updated" label="最后更新"></el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../utils/axios';

const clusters = ref([]);
const nodes = ref([]);
const selectedCluster = ref('');

const fetchClusters = async () => {
  try {
    const response = await apiClient.get('/clusters');
    clusters.value = response.clusters;
  } catch (error) {
    console.error('获取集群列表失败:', error);
  }
};

const fetchNodes = async () => {
  if (!selectedCluster.value) return;
  
  try {
    const response = await apiClient.get('/nodes', {
      params: { cluster: selectedCluster.value }
    });
    nodes.value = response.nodes;
  } catch (error) {
    console.error('获取节点列表失败:', error);
  }
};

onMounted(() => {
  fetchClusters();
});
</script>
```

### 5.4 日志管理模块

**获取日志列表示例** (`src/views/Logs.vue`):

```vue
<template>
  <div class="logs-view">
    <h1>日志管理</h1>
    
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="集群">
        <el-select v-model="searchForm.cluster" placeholder="选择集群">
          <el-option
            v-for="cluster in clusters"
            :key="cluster.uuid"
            :label="cluster.host"
            :value="cluster.uuid"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="节点">
        <el-select v-model="searchForm.node" placeholder="选择节点">
          <el-option
            v-for="node in nodes"
            :key="node.name"
            :label="node.name"
            :value="node.name"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchLogs">查询</el-button>
      </el-form-item>
    </el-form>
    
    <el-table :data="logs" style="width: 100%">
      <el-table-column prop="time" label="时间" width="200"></el-table-column>
      <el-table-column prop="level" label="级别" width="80"></el-table-column>
      <el-table-column prop="cluster" label="集群" width="120"></el-table-column>
      <el-table-column prop="node" label="节点" width="120"></el-table-column>
      <el-table-column prop="op" label="服务" width="100"></el-table-column>
      <el-table-column prop="message" label="日志内容"></el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../utils/axios';

const clusters = ref([]);
const nodes = ref([]);
const logs = ref([]);

const searchForm = ref({
  cluster: '',
  node: ''
});

const fetchClusters = async () => {
  try {
    const response = await apiClient.get('/clusters');
    clusters.value = response.clusters;
  } catch (error) {
    console.error('获取集群列表失败:', error);
  }
};

const fetchNodes = async () => {
  if (!searchForm.value.cluster) return;
  
  try {
    const response = await apiClient.get('/nodes', {
      params: { cluster: searchForm.value.cluster }
    });
    nodes.value = response.nodes;
  } catch (error) {
    console.error('获取节点列表失败:', error);
  }
};

const fetchLogs = async () => {
  try {
    const response = await apiClient.get('/logs', {
      params: {
        cluster: searchForm.value.cluster,
        node: searchForm.value.node
      }
    });
    logs.value = response.items;
  } catch (error) {
    console.error('获取日志列表失败:', error);
  }
};

onMounted(() => {
  fetchClusters();
});
</script>

<style scoped>
.search-form {
  margin-bottom: 20px;
}
</style>
```

## 6. 状态管理

### 6.1 使用Pinia管理用户状态

```bash
# 安装Pinia
npm install pinia
```

**用户状态管理** (`src/stores/user.js`):

```javascript
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    fullName: localStorage.getItem('fullName') || '',
    isLoggedIn: !!localStorage.getItem('token')
  }),
  
  actions: {
    login(userData) {
      this.token = userData.token;
      this.username = userData.username;
      this.fullName = userData.fullName;
      this.isLoggedIn = true;
      
      // 保存到localStorage
      localStorage.setItem('token', userData.token);
      localStorage.setItem('username', userData.username);
      localStorage.setItem('fullName', userData.fullName);
    },
    
    logout() {
      this.token = '';
      this.username = '';
      this.fullName = '';
      this.isLoggedIn = false;
      
      // 清除localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('fullName');
    }
  }
});
```

**使用示例**:

```javascript
import { useUserStore } from '../stores/user';

const userStore = useUserStore();

// 登录时
userStore.login(response);

// 登出时
userStore.logout();
```

## 7. 错误处理

### 7.1 全局错误处理

在`src/main.js`中配置全局错误处理:

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import apiClient from './utils/axios'
import { ElMessage } from 'element-plus'

const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err, info)
  ElMessage.error('系统发生错误，请刷新页面重试')
}

// 配置Axios实例到app实例
app.config.globalProperties.$api = apiClient

app.mount('#app')
```

### 7.2 常见错误处理

| 错误类型 | 状态码 | 处理方式 |
|----------|--------|----------|
| 未授权 | 401 | 清除token，跳转到登录页 |
| 禁止访问 | 403 | 显示"没有权限访问该资源"提示 |
| 资源不存在 | 404 | 显示"请求的资源不存在"提示 |
| 服务器错误 | 500 | 显示"服务器内部错误"提示 |
| 网络错误 | - | 显示"网络连接失败"提示 |
| 超时错误 | - | 显示"请求超时，请重试"提示 |

## 8. 开发工具和调试技巧

### 8.1 浏览器开发者工具
- **Network** 面板：查看请求和响应详情
- **Application** 面板：查看localStorage、Cookie等
- **Console** 面板：查看日志和错误信息

### 8.2 Postman
用于测试API接口，生成API调用代码

### 8.3 Swagger UI
直接在浏览器中测试API接口，无需编写代码

### 8.4 Vue DevTools
Chrome/Firefox扩展，用于调试Vue组件和状态管理

## 9. 最佳实践

### 9.1 代码组织
- 按功能模块组织API调用
- 统一的错误处理机制
- 使用拦截器处理认证和响应

### 9.2 性能优化
- 使用防抖和节流减少请求次数
- 合理使用缓存
- 分页加载数据
- 图片懒加载

### 9.3 安全性
- 不要在前端存储敏感信息
- 使用HTTPS传输数据
- 实现CSRF保护
- 定期刷新token

### 9.4 可维护性
- 编写清晰的注释
- 遵循一致的代码风格
- 单元测试和集成测试
- 文档化API调用

## 10. 常见问题和解决方案

### 10.1 问题：登录后token不生效
**解决方案**：
- 检查token是否正确存储在localStorage中
- 检查请求头中是否携带了Authorization头
- 检查token是否过期
- 检查后端是否正确配置了JWT密钥

### 10.2 问题：CORS跨域错误
**解决方案**：
- 后端已配置CORS中间件，允许所有来源
- 检查前端请求的URL是否正确
- 检查浏览器控制台的网络请求

### 10.3 问题：API返回500错误
**解决方案**：
- 检查请求参数是否正确
- 检查后端日志
- 查看详细的错误信息
- 联系后端开发人员

### 10.4 问题：集群或节点数据为空
**解决方案**：
- 确保集群和节点已正确配置
- 检查数据库连接是否正常
- 检查后端服务是否正常运行

### 10.5 问题：AI聊天接口超时
**解决方案**：
- 增加请求超时时间
- 优化AI服务配置
- 检查网络连接
- 考虑使用WebSocket实现实时通信

## 11. 部署建议

### 11.1 前端部署
- 使用Vite构建生产版本：`npm run build`
- 部署到Nginx或CDN
- 配置反向代理指向后端API

### 11.2 后端部署
- 使用Docker容器化部署
- 配置环境变量
- 使用PM2或systemd管理进程
- 配置日志收集

### 11.3 CI/CD
- 使用GitHub Actions或GitLab CI实现自动化部署
- 配置测试流程
- 配置代码质量检查

## 12. 联系方式

- **后端开发团队**：Hadoop故障检测团队
- **前端开发团队**：Vue开发团队
- **邮箱**：support@hadoop-fault-detect.example.com
- **文档更新**：`docs/frontend_integration_guide.md`

## 13. 版本历史

| 版本 | 日期 | 描述 |
|------|------|------|
| v1.0 | 2025-12-18 | 初始版本 |

---

**更新记录**：
- 2025-12-18：创建文档，包含Vue 3 + Vite + Axios配置和示例代码
- 2025-12-18：添加状态管理和错误处理章节
- 2025-12-18：添加开发工具和最佳实践章节
- 2025-12-18：添加常见问题和解决方案章节
