// 主应用程序
class ErrorDetectingApp {
    constructor() {
        this.currentPage = 'login';
        this.isLoggedIn = false;
        this.sidebarCollapsed = false;
        this.darkMode = false;
        this.init();
    }

    // 初始化应用
    init() {
        this.loadStoredSettings();
        this.bindEvents();
        this.initializeRouter();
        this.loadPageComponents();
        this.checkAuthStatus();
    }

    // 加载存储的设置
    loadStoredSettings() {
        const darkMode = localStorage.getItem('darkMode');
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed');
        
        if (darkMode === 'true') {
            this.toggleDarkMode(true);
        }
        
        if (sidebarCollapsed === 'true') {
            this.toggleSidebar(true);
        }
    }

    // 绑定事件
    bindEvents() {
        // 侧边栏切换
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // 主题切换
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleDarkMode());
        }

        // 导航菜单点击
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.navigateTo(page);
            }
        });

        // 登录表单提交
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // 退出登录
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // 窗口大小变化
        window.addEventListener('resize', () => this.handleResize());
    }

    // 加载页面组件
    async loadPageComponents() {
        try {
            // 加载登录页面内容
            await this.loadPageContent('views/Login/Login.html', '.login-page-wrapper');
            
            // 加载布局组件
            await this.loadPageContent('components/Layout/Header.html', '#header');
            await this.loadPageContent('components/Layout/Sidebar.html', '#sidebar');
            
            // 加载其他页面内容
            await this.loadPageContent('views/ClusterMonitor/ClusterMonitor.html', '#clusterMonitorPage');
            await this.loadPageContent('views/FaultManage/FaultManage.html', '#faultManagePage');
            await this.loadPageContent('views/LogAnalysis/LogAnalysis.html', '#logAnalysisPage');
            
        } catch (error) {
            console.error('加载页面组件失败:', error);
        }
    }

    // 初始化路由
    initializeRouter() {
        // 监听浏览器前进后退
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.showPage(e.state.page, false);
            }
        });

        // 初始页面路由
        const hash = window.location.hash.slice(1);
        if (hash) {
            this.navigateTo(hash, false);
        } else {
            this.navigateTo('login', false);
        }
    }

    // 检查认证状态
    checkAuthStatus() {
        const token = localStorage.getItem('authToken');
        if (token) {
            // 这里应该验证token的有效性
            this.isLoggedIn = true;
            if (this.currentPage === 'login') {
                this.navigateTo('dashboard');
            }
        } else {
            this.isLoggedIn = false;
            if (this.currentPage !== 'login') {
                this.navigateTo('login');
            }
        }
    }

    // 导航到指定页面
    navigateTo(page, pushState = true) {
        // 检查是否需要登录
        if (!this.isLoggedIn && page !== 'login') {
            this.navigateTo('login');
            return;
        }

        this.showPage(page, pushState);
    }

    // 显示页面
    showPage(page, pushState = true) {
        // 隐藏所有页面
        const pages = document.querySelectorAll('.page-view');
        pages.forEach(p => p.style.display = 'none');

        // 显示目标页面
        const targetPage = document.getElementById(page + 'Page');
        if (targetPage) {
            targetPage.style.display = 'block';
            this.currentPage = page;

            // 更新导航状态
            this.updateNavigation(page);

            // 更新浏览器历史
            if (pushState) {
                const url = page === 'login' ? '/' : `/#${page}`;
                history.pushState({ page }, '', url);
            }

            // 更新页面标题
            this.updatePageTitle(page);

            // 触发页面加载事件
            this.onPageLoad(page);
        }

        // 控制布局显示
        const appLayout = document.getElementById('appLayout');
        const loginContainer = document.getElementById('loginContainer');
        
        if (page === 'login') {
            if (appLayout) appLayout.style.display = 'none';
            if (loginContainer) loginContainer.style.display = 'flex';
        } else {
            if (appLayout) appLayout.style.display = 'flex';
            if (loginContainer) loginContainer.style.display = 'none';
        }
    }

    // 更新导航状态
    updateNavigation(page) {
        // 移除所有活动状态
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => item.classList.remove('active'));

        // 添加当前页面的活动状态
        const currentNavItem = document.querySelector(`[data-page="${page}"]`);
        if (currentNavItem) {
            currentNavItem.closest('.nav-item').classList.add('active');
        }

        // 更新面包屑
        this.updateBreadcrumb(page);
    }

    // 更新面包屑导航
    updateBreadcrumb(page) {
        const breadcrumb = document.getElementById('breadcrumb');
        if (!breadcrumb) return;

        const pageNames = {
            'dashboard': '概览仪表板',
            'cluster-monitor': '集群监控',
            'fault-manage': '故障管理',
            'log-analysis': '日志分析',
            'system-config': '系统配置',
            'user-manage': '用户管理',
            'system-monitor': '系统监控',
            'help': '帮助中心'
        };

        const pageName = pageNames[page] || '未知页面';
        breadcrumb.innerHTML = `
            <span class="breadcrumb-item">
                <i class="icon-home"></i>
                <span>首页</span>
            </span>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-item active">${pageName}</span>
        `;
    }

    // 更新页面标题
    updatePageTitle(page) {
        const titles = {
            'login': '登录 - 错误检测系统',
            'dashboard': '概览仪表板 - 错误检测系统',
            'cluster-monitor': '集群监控 - 错误检测系统',
            'fault-manage': '故障管理 - 错误检测系统',
            'log-analysis': '日志分析 - 错误检测系统',
            'system-config': '系统配置 - 错误检测系统',
            'user-manage': '用户管理 - 错误检测系统',
            'system-monitor': '系统监控 - 错误检测系统',
            'help': '帮助中心 - 错误检测系统'
        };

        document.title = titles[page] || '错误检测系统';
    }

    // 页面加载事件
    onPageLoad(page) {
        switch (page) {
            case 'cluster-monitor':
                this.initClusterMonitor();
                break;
            case 'fault-manage':
                this.initFaultManage();
                break;
            case 'log-analysis':
                this.initLogAnalysis();
                break;
            case 'dashboard':
                this.initDashboard();
                break;
        }
    }

    // 切换侧边栏
    toggleSidebar(force = null) {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        
        if (!sidebar || !mainContent) return;

        if (force !== null) {
            this.sidebarCollapsed = force;
        } else {
            this.sidebarCollapsed = !this.sidebarCollapsed;
        }

        if (this.sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        } else {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('sidebar-collapsed');
        }

        localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
    }

    // 切换深色模式
    toggleDarkMode(force = null) {
        if (force !== null) {
            this.darkMode = force;
        } else {
            this.darkMode = !this.darkMode;
        }

        if (this.darkMode) {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }

        localStorage.setItem('darkMode', this.darkMode);

        // 更新主题切换按钮图标
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = this.darkMode ? 'icon-sun' : 'icon-moon';
            }
        }
    }

    // 处理登录
    handleLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const captcha = document.getElementById('captcha').value;

        // 简单的登录验证（实际项目中应该调用API）
        if (username && password && captcha) {
            // 模拟登录成功
            this.isLoggedIn = true;
            localStorage.setItem('authToken', 'mock-token-' + Date.now());
            localStorage.setItem('username', username);
            
            // 显示登录成功消息
            this.showNotification('登录成功！', 'success');
            
            // 跳转到仪表板
            setTimeout(() => {
                this.navigateTo('dashboard');
            }, 1000);
        } else {
            this.showNotification('请填写完整的登录信息', 'error');
        }
    }

    // 处理退出登录
    handleLogout() {
        this.isLoggedIn = false;
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
        
        this.showNotification('已退出登录', 'info');
        this.navigateTo('login');
    }

    // 处理窗口大小变化
    handleResize() {
        const width = window.innerWidth;
        
        // 在小屏幕上自动收起侧边栏
        if (width < 768 && !this.sidebarCollapsed) {
            this.toggleSidebar(true);
        }
    }

    // 显示通知
    showNotification(message, type = 'info', duration = 3000) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon icon-${type === 'success' ? 'check' : type === 'error' ? 'x' : 'info'}"></i>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="icon-x"></i>
                </button>
            </div>
        `;

        // 添加到页面
        let container = document.getElementById('notificationContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        container.appendChild(notification);

        // 自动移除
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }

    // 初始化仪表板
    initDashboard() {
        // 仪表板页面已在HTML中定义，这里可以添加动态数据加载
        console.log('仪表板页面初始化完成');
    }

    // 初始化集群监控
    initClusterMonitor() {
        const container = document.getElementById('clusterMonitorPage');
        if (container && !container.hasChildNodes()) {
            // 动态加载集群监控页面内容
            this.loadPageContent('views/ClusterMonitor/ClusterMonitor.html', container);
        }
    }

    // 初始化故障管理
    initFaultManage() {
        const container = document.getElementById('faultManagePage');
        if (container && !container.hasChildNodes()) {
            // 动态加载故障管理页面内容
            this.loadPageContent('views/FaultManage/FaultManage.html', container);
        }
    }

    // 初始化日志分析
    initLogAnalysis() {
        const container = document.getElementById('logAnalysisPage');
        if (container && !container.hasChildNodes()) {
            // 动态加载日志分析页面内容
            this.loadPageContent('views/LogAnalysis/LogAnalysis.html', container);
        }
    }

    // 动态加载页面内容的辅助方法
    async loadPageContent(url, containerSelector) {
        try {
            const container = document.querySelector(containerSelector);
            if (!container) {
                console.warn(`容器不存在: ${containerSelector}`);
                return;
            }
            
            const response = await fetch(url);
            if (response.ok) {
                const html = await response.text();
                container.innerHTML = html;
            } else {
                console.warn(`无法加载页面内容: ${url}`);
                container.innerHTML = '<div class="error-message">页面加载失败</div>';
            }
        } catch (error) {
            console.error(`加载页面内容时出错: ${url}`, error);
            const container = document.querySelector(containerSelector);
            if (container) {
                container.innerHTML = '<div class="error-message">页面加载出错</div>';
            }
        }
    }
}

// 工具函数
const Utils = {
    // 格式化时间
    formatTime(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
        const date = new Date(timestamp);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');

        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },

    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 节流函数
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // 生成随机ID
    generateId(length = 8) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    },

    // 深拷贝
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const clonedObj = {};
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    clonedObj[key] = this.deepClone(obj[key]);
                }
            }
            return clonedObj;
        }
    }
};

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ErrorDetectingApp();
});

// 导出到全局
window.ErrorDetectingApp = ErrorDetectingApp;
window.Utils = Utils;