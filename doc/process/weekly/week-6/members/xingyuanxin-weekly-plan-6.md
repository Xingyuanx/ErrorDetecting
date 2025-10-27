# 第一周（每天19:00-22:00）详细计划

## 周一
### 19:00-20:00：项目背景与需求边界理解
1. 阅读《项目核心任务说明文档》中“前端任务5（交互式Web应用前端开发）”和《用例文档》，重点关注运维人员的核心操作场景（如集群状态查看、故障处理）；
2. 梳理登录、集群监控、故障管理、日志分析四大模块的核心功能：
   - 登录模块：账号密码验证、异常提示、页面跳转；
   - 集群监控模块：节点状态展示（在线/离线）、CPU/磁盘使用率趋势图；
   - 故障管理模块：故障列表筛选、故障详情查看、修复操作触发；
   - 日志分析模块：日志筛选（时间/节点）、AI分析提交；
3. 用手绘或ProcessOn制作《前端功能模块思维导图》，标注每个模块的核心交互逻辑（如“集群监控页→点击刷新按钮→获取最新节点数据”）。
- 交付物：个人版《前端功能模块思维导图》

### 20:00-21:00：用例场景拆解（聚焦登录）
1. 拆解“登录”用例完整交互流程：
   - 第一步：运维人员访问登录地址，前端展示账号、密码输入框及“登录”按钮；
   - 第二步：输入账号（如admin）、密码（如123456@abc），点击“登录”按钮；
   - 第三步：前端做表单验证（账号非空、密码≥6位），验证不通过则提示对应错误；
   - 第四步：验证通过后，前端携带账号密码调用后端`/api/user/login`接口；
   - 第五步：接口返回成功→存储Token到localStorage，跳转至集群监控页；
   - 第六步：接口返回失败→根据错误类型提示（如“账号或密码错误”“账号已禁用”）；
2. 记录关键交互细节：Token有效期8小时，过期后前端自动清除Token并跳转登录页；密码输入框支持“显示/隐藏”密码功能；
3. 整理文字版《登录用例交互清单》，标注每个步骤的前端处理逻辑（如“步骤三：用Element Plus表单校验规则实现非空校验”）。
- 交付物：登录用例交互清单（文字版）

### 21:00-22:00：技术栈初步认知
1. 浏览Vue 3官方文档“快速上手”章节：
   - 理解Vue组件的基本结构（`<template>`模板、`<script setup>`逻辑、`<style>`样式）；
   - 掌握`v-bind`（绑定属性）、`v-on`（绑定事件）等基础指令用法；
   - 了解响应式数据（`ref`定义基本类型、`reactive`定义对象类型）；
2. 打开Element Plus官网“快速开始”页面：
   - 查看组件引入方式（全局引入vs按需引入，新手优先全局引入简化操作）；
   - 熟悉Button（按钮）、Form（表单）、Table（表格）组件的基础示例代码；
   - 记录组件使用步骤（如“引入Element Plus样式文件→在组件中使用`<el-button>`标签”）；
3. 撰写约500字的《技术栈核心概念笔记》，重点标注：
   - Vue组件创建步骤（新建`.vue`文件→编写模板/逻辑/样式→在路由中配置）；
   - Element组件引入流程（安装依赖→在`main.js`中导入并使用）；
   - 新手易混淆点（如Vue 3的`<script setup>`语法与Vue 2的差异）。
- 交付物：技术栈核心概念笔记（约500字）


## 周二
### 19:00-20:00：本地环境搭建（Node.js + npm）
1. 下载Node.js：
   - 打开Node.js官网（https://nodejs.org/），选择LTS版本（如v18.17.0），根据操作系统（Windows/macOS）下载对应安装包；
   - 双击安装包，按向导步骤完成安装（Windows需勾选“Add to PATH”，macOS默认配置）；
2. 验证安装：
   - Windows打开“命令提示符”，macOS打开“终端”，执行`node -v`，若显示“v18.17.0”（或对应版本号）则Node安装成功；
   - 执行`npm -v`，显示版本号（如9.6.7）则npm安装成功；
3. 配置npm国内镜像：
   - 执行命令`npm config set registry https://registry.npmmirror.com`，解决后续下载依赖速度慢的问题；
   - 执行`npm config get registry`，若返回“https://registry.npmmirror.com/”则配置生效。
- 交付物：终端显示Node、npm版本号的截图（需包含`node -v`和`npm -v`命令及输出结果）

### 20:00-21:00：项目初始化（Vite + Vue 3）
1. 创建Vue项目：
   - 终端执行命令`npm create vite@latest hadoop-fault-front -- --template vue`；
   - 按提示操作：项目名称默认“hadoop-fault-front”→框架选择“Vue”→变体选择“JavaScript”，等待项目骨架生成；
2. 安装依赖：
   - 执行`cd hadoop-fault-front`，进入项目根目录；
   - 执行`npm install`，安装项目所需基础依赖（耐心等待，网络不稳定时可重试，直至终端显示“added xxx packages”）；
3. 启动项目：
   - 执行`npm run dev`，终端显示“VITE v4.5.0 ready in 300 ms”及访问地址（默认`http://localhost:5173`）；
   - 打开浏览器，输入访问地址，若看到Vue默认页面（含“Hello Vue 3 + Vite”文字）则项目启动成功。
- 交付物：本地成功启动Vue项目的浏览器页面截图（需包含地址栏和默认页面内容）

### 21:00-22:00：目录结构初始化
1. 创建核心目录：
   - 打开项目中的`src`文件夹，新建5个文件夹：
     - `api`：用于存放接口封装文件（如用户接口、集群接口）；
     - `components`：用于存放公共组件（如布局组件、加载组件）；
     - `views`：用于存放页面组件（如登录页、集群监控页）；
     - `router`：用于存放路由配置文件；
     - `utils`：用于存放工具函数（如请求封装、时间格式化）；
2. 创建基础文件：
   - 在`router`目录下新建`index.js`文件（后续配置路由规则）；
   - 在`utils`目录下新建`request.js`文件（后续封装Axios请求）；
3. 验证目录结构：
   - 用VS Code打开项目，查看`src`目录下是否有上述5个文件夹及2个基础文件；
   - 截图保存目录结构（需清晰展示`src`下的目录和文件层级）。
- 交付物：规范化目录结构的截图（需包含VS Code的文件管理器界面）


## 周三
### 19:00-20:00：工具链配置（ESLint）
1. 安装ESLint依赖：
   - 终端进入项目根目录，执行`npm install eslint -D`（`-D`表示开发环境依赖）；
   - 等待安装完成，终端显示“added xxx packages”则安装成功；
2. 初始化ESLint配置：
   - 执行`npx eslint --init`，按终端提示依次选择：
     - 选择“To check syntax and find problems”（检查语法和问题）；
     - 选择“Vue.js”（项目使用的框架）；
     - 选择“JavaScript modules (import/export)”（项目模块系统）；
     - 选择“None”（不使用TypeScript）；
     - 选择“Node”（项目运行环境）；
     - 选择“JavaScript”（配置文件格式）；
     - 确认“Would you like to install them now?”→选择“Yes”，自动安装所需依赖；
3. 验证ESLint生效：
   - 在`src`目录下新建`test.js`文件，写入错误代码：`const a = 1; a = 2;`（const声明的变量不可修改）；
   - 终端执行`npx eslint src`，若显示“'a' is assigned a value but never used”“Assignment to constant variable”等报错信息，则ESLint配置生效。
- 交付物：ESLint初始化成功的终端报错截图（需包含`npx eslint src`命令及报错结果）

### 20:00-21:00：工具链配置（Prettier）
1. 安装Prettier及集成依赖：
   - 终端执行命令`npm install prettier eslint-config-prettier eslint-plugin-prettier -D`；
   - 等待安装完成，确保无“error”提示；
2. 配置ESLint与Prettier兼容：
   - 打开项目根目录的`.eslintrc.cjs`文件，找到`extends`数组，添加`'plugin:prettier/recommended'`，修改后如下：
     ```javascript
     extends: [
       'eslint:recommended',
       'plugin:vue/vue3-recommended',
       'plugin:prettier/recommended'
     ]
     ```
   - 保存文件，实现ESLint语法校验与Prettier格式美化的规则兼容；
3. 配置Prettier格式规则：
   - 在项目根目录新建`.prettierrc`文件，写入配置：`{ "semi": false, "singleQuote": true }`（表示不加分号、使用单引号）；
   - 测试自动格式化：在`test.js`中写入`const name = "hadoop"`，保存文件后，Prettier会自动将双引号改为单引号，删除多余分号。
- 交付物：保存代码后自动格式化的效果截图（需对比保存前后的代码差异，如双引号变单引号）

### 21:00-22:00：基础组件初探（登录页雏形）
1. 创建登录页文件：
   - 在`views`目录下新建`Login`文件夹，在该文件夹下新建`Index.vue`文件；
2. 引入Element Plus按钮组件：
   - 打开Element Plus官网“Button组件”页面（https://element-plus.org/zh-CN/component/button.html），复制“默认按钮”示例代码：
     ```vue
     <template>
       <el-button type="primary">登录</el-button>
     </template>
     ```
   - 将代码粘贴到`Index.vue`的`<template>`标签中，补充Vue组件基础结构：
     ```vue
     <template>
       <div class="login-btn-container">
         <el-button type="primary">登录</el-button>
       </div>
     </template>

     <script setup>
     // 后续添加逻辑
     </script>

     <style scoped>
     .login-btn-container {
       margin: 20px;
     }
     </style>
     ```
3. 全局引入Element Plus（新手简化操作）：
   - 打开`src/main.js`文件，添加Element Plus引入代码：
     ```javascript
     import { createApp } from 'vue'
     import ElementPlus from 'element-plus'
     import 'element-plus/dist/index.css'
     import App from './App.vue'

     createApp(App).use(ElementPlus).mount('#app')
     ```
4. 验证登录页雏形：
   - 终端执行`npm run dev`，启动项目；
   - 打开浏览器访问`http://localhost:5173`，修改`App.vue`的`<template>`为`<Login />`（需先在`App.vue`中导入`import Login from './views/Login/Index.vue'`）；
   - 确认页面显示“登录”按钮，点击按钮无报错（控制台无红色错误信息）。
- 交付物：登录页显示可点击“登录”按钮的浏览器页面截图（需包含按钮和控制台无报错的界面）


## 周四
### 19:00-20:00：跨域与环境变量配置
1. 配置跨域代理：
   - 打开项目根目录的`vite.config.js`文件，在`defineConfig`函数的`server`选项中添加跨域代理配置：
     ```javascript
     import { defineConfig } from 'vite'
     import vue from '@vitejs/plugin-vue'

     export default defineConfig({
       plugins: [vue()],
       server: {
         proxy: {
           '/api': {
             target: 'http://localhost:8000', // 后端开发环境接口地址（与后端确认）
             changeOrigin: true, // 允许跨域（模拟请求来源为后端地址）
             rewrite: (path) => path.replace(/^\/api/, '') // 移除请求路径中的“/api”前缀（若后端接口无该前缀）
           }
         }
       }
     })
     ```
2. 配置环境变量：
   - 在项目根目录新建`.env.development`文件（开发环境专用配置），添加接口基础地址：
     ```env
     # 开发环境接口基础地址（与跨域代理的“/api”对应）
     VITE_API_BASE_URL = '/api'
     ```
   - 注意：环境变量需以“VITE_”开头，否则Vite无法识别；
3. 验证配置：
   - 保存`vite.config.js`和`.env.development`文件；
   - 终端执行`npm run dev`重启项目，确保启动无报错（终端无“error”提示）。
- 交付物：`vite.config.js`和`.env.development`文件的代码截图（需清晰展示配置内容）

### 20:00-21:00：接口请求封装（Axios）
1. 安装Axios依赖：
   - 终端执行`npm install axios`，安装用于发送HTTP请求的Axios库；
   - 等待安装完成，终端显示“added axios@xxx”则成功；
2. 封装Axios实例：
   - 打开`src/utils/request.js`文件，写入封装代码：
     ```javascript
     // 导入Axios
     import axios from 'axios'

     // 创建Axios实例
     const request = axios.create({
       baseURL: import.meta.env.VITE_API_BASE_URL, // 从环境变量获取接口基础地址
       timeout: 30000 // 请求超时时间（30秒，适配AI分析等耗时接口）
     })

     // 请求拦截器：添加Token（后续登录后使用）
     request.interceptors.request.use(
       (config) => {
         // 从localStorage获取Token，若存在则添加到请求头
         const token = localStorage.getItem('token')
         if (token) {
           config.headers.Authorization = `Bearer ${token}`
         }
         return config
       },
       (error) => {
         // 请求错误时的处理（如网络错误）
         console.error('请求拦截器错误：', error)
         return Promise.reject(error)
       }
     )

     // 响应拦截器：统一处理错误
     request.interceptors.response.use(
       (response) => {
         // 直接返回响应体（简化后续调用）
         return response.data
       },
       (error) => {
         // 处理常见错误（如401 Token过期）
         if (error.response?.status === 401) {
           // Token过期：清除Token并跳转登录页（后续需配合路由实现）
           localStorage.removeItem('token')
           window.location.href = '/login'
         }
         console.error('响应拦截器错误：', error)
         return Promise.reject(error)
       }
     )

     // 导出封装后的实例
     export default request
     ```
3. 验证封装：
   - 在`src/api`目录下新建`user.js`文件，导入`request`实例：
     ```javascript
     import request from '@/utils/request'

     // 封装登录接口（后续联调使用）
     export const login = (data) => {
       return request({
         url: '/user/login',
         method: 'post',
         data // 账号密码数据（{ username: '', password: '' }）
       })
     }
     ```
   - 保存文件，确保无语法错误（VS Code无红色波浪线）。
- 交付物：`utils/request.js`和`api/user.js`文件的代码截图（需清晰展示封装逻辑）

### 21:00-22:00：需求与技术方案整合
1. 整理本周关键成果：
   - 需求层面：前端功能模块思维导图、登录用例交互清单；
   - 技术层面：本地环境（Node.js + Vue 3）、工具链（ESLint + Prettier）、基础配置（跨域、Axios封装）；
   - 组件层面：登录页雏形（含Element Plus按钮）、规范化目录结构；
2. 撰写《前端第一周进展总结》（Markdown格式）：
   - 标题：前端第一周进展总结（Hadoop故障检测项目）；
   - 内容分三部分：
     1. 已完成工作：按“需求分析→环境搭建→配置开发→组件雏形”罗列，附关键交付物说明；
     2. 遇到的问题：记录新手易踩坑点（如Node安装未配置PATH、ESLint初始化选项选错）及解决方法；
     3. 下周计划方向：完成登录页表单开发、配置路由、联调登录接口、启动集群监控页开发；
3. 优化总结文档：
   - 用列表清晰展示内容，关键步骤附简单说明（如“跨域配置：解决开发环境调用后端接口的跨域问题”）；
   - 确保文档逻辑连贯，便于项目组同步进度。
- 交付物：《前端第一周进展总结》（Markdown格式，可提供文字内容或文件截图）


## 周五
### 19:00-20:30：周任务复盘与调整
1. 复盘本周任务完成情况：
   - 已完成：需求分析（思维导图、用例清单）、环境搭建（Node.js、Vue项目）、工具链配置（ESLint、Prettier）、基础配置（跨域、Axios封装）、登录页雏形；
   - 待优化：登录页未实现表单（仅按钮）、Axios拦截器未配合路由跳转、集群监控页未启动；
   - 问题记录：如“ESLint初始化时选错模块系统，导致配置报错，重新执行`npx eslint --init`解决”；
2. 调整下周具体任务（聚焦核心优先级）：
   - 周一：完成登录页表单开发（Element Plus Form组件）、配置Vue Router路由；
   - 周二：联调登录接口（调用`api/user.js`的`login`函数）、实现Token存储与页面跳转；
   - 周三：启动集群监控页开发（节点列表静态渲染、ECharts初始化）；
   - 周四：封装集群状态接口、实现集群监控页数据加载；
   - 周五：优化登录页交互（如加载动画、错误提示）、复盘下周任务；
3. 输出《前端第二周任务计划》（文字版）：
   - 按天划分任务，每个任务明确“核心目标”和“关键步骤”（如“周一核心目标：登录页表单开发，关键步骤：引入Element Form组件→编写校验规则→绑定提交事件”）。
- 交付物：《前端第二周任务计划》（文字版，需明确每天核心目标与关键步骤）

### 20:30-22:00：新手学习加餐（Vue基础强化）
1. 学习Vue 3组件通信基础：
   - 浏览Vue 3官方文档“组件基础-Prop传递数据”章节：
     - 理解Prop的作用（父组件向子组件传递数据）；
     - 掌握Prop的定义方式（如`const props = defineProps({ name: String })`）；
     - 记录示例代码（父组件通过`<Child name="hadoop" />`传值，子组件用`{{ name }}`渲染）；
2. 学习Vue Router基础：
   - 浏览Vue Router官网“快速开始”章节（https://router.vuejs.org/zh/guide/）：
     - 理解路由的作用（页面跳转与URL映射）；
     - 掌握路由安装（`npm install vue-router@4`）与基础配置（`router/index.js`定义路由规则）；
     - 记录示例代码（配置“登录页”路由：`{ path: '/login', component: () => import('@/views/Login/Index.vue') }`）；
3. 整理学习笔记：
   - 撰写约300字的《Vue基础强化笔记》，重点标注：
     - 组件Prop传递的注意事项（Prop只读，子组件不可修改父组件数据）；
     - Vue Router的核心概念（`router-link`跳转、`router-view`渲染组件）；
     - 下周学习应用场景（如用Vue Router实现登录页与集群监控页的跳转）。
- 交付物：《Vue基础强化笔记》（约300字，文字版或截图）