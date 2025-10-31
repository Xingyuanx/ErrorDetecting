/**
 * 导航管理工具类
 * 负责页面导航、下拉菜单和用户交互
 */
class NavigationManager {
    constructor() {
        this.currentPage = 'dashboard'; // 当前激活的页面
        this.init();
    }

    /**
     * 初始化导航功能
     */
    init() {
        // 等待 DOM 加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.bindEvents();
            });
        } else {
            this.bindEvents();
        }
    }

    /**
     * 绑定所有事件监听器
     */
    bindEvents() {
        this.bindNavigationEvents();
        this.bindDropdownEvents();
        this.bindUserMenuEvents();
        this.bindGlobalClickEvents();
        this.bindSearchEvents();
    }

    /**
     * 绑定主导航事件
     */
    bindNavigationEvents() {
        // 获取所有导航项
        const navItems = document.querySelectorAll('.header__nav-item[data-page]');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPage = item.getAttribute('data-page');
                this.switchPage(targetPage);
            });
        });
    }

    /**
     * 页面切换功能
     * @param {string} pageName - 目标页面名称
     */
    switchPage(pageName) {
        // 隐藏所有页面
        const allSections = document.querySelectorAll('.layout__section, #dashboard');
        allSections.forEach(section => {
            section.classList.add('u-hidden');
        });

        // 显示目标页面
        const targetSection = document.getElementById(pageName);
        if (targetSection) {
            targetSection.classList.remove('u-hidden');
        }

        // 更新导航项激活状态
        this.updateActiveNavItem(pageName);
        
        // 更新当前页面
        this.currentPage = pageName;

        // 触发页面切换事件
        this.onPageSwitch(pageName);
    }

    /**
     * 更新导航项激活状态
     * @param {string} activePage - 激活的页面名称
     */
    updateActiveNavItem(activePage) {
        // 移除所有激活状态
        const navItems = document.querySelectorAll('.header__nav-item');
        navItems.forEach(item => {
            item.classList.remove('header__nav-item--active');
            item.removeAttribute('aria-current');
        });

        // 添加新的激活状态
        const activeItem = document.querySelector(`[data-page="${activePage}"]`);
        if (activeItem) {
            activeItem.classList.add('header__nav-item--active');
            activeItem.setAttribute('aria-current', 'page');
        }
    }

    /**
     * 页面切换回调
     * @param {string} pageName - 切换到的页面名称
     */
    onPageSwitch(pageName) {
        // 根据页面执行特定操作
        switch (pageName) {
            case 'dashboard':
                // 刷新图表数据
                if (window.chartManager) {
                    window.chartManager.resizeAllCharts();
                }
                break;
            case 'logs':
                // 可以在这里加载日志数据
                console.log('切换到日志查询页面');
                break;
            case 'diagnosis':
                // 可以在这里初始化诊断功能
                console.log('切换到故障诊断页面');
                break;
            case 'repair':
                // 可以在这里加载修复建议
                console.log('切换到自动修复页面');
                break;
        }
    }

    /**
     * 绑定下拉菜单事件
     */
    bindDropdownEvents() {
        // 系统配置下拉菜单
        const configDropdown = document.querySelector('.header__dropdown');
        if (configDropdown) {
            const trigger = configDropdown.querySelector('.header__dropdown-trigger');
            const menu = configDropdown.querySelector('.header__dropdown-menu');
            
            if (trigger && menu) {
                trigger.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggleDropdown(configDropdown, trigger, menu);
                });
            }
        }

        // 日志级别下拉菜单
        this.bindSelectDropdown('log-level');
        
        // 来源节点下拉菜单
        this.bindSelectDropdown('source-node');
        
        // 时间范围下拉菜单
        this.bindSelectDropdown('time-range');
    }

    /**
     * 切换下拉菜单显示状态
     * @param {Element} dropdown - 下拉菜单容器
     * @param {Element} trigger - 触发按钮
     * @param {Element} menu - 菜单内容
     */
    toggleDropdown(dropdown, trigger, menu) {
        const isOpen = trigger.getAttribute('aria-expanded') === 'true';
        
        // 关闭所有其他下拉菜单
        this.closeAllDropdowns();
        
        if (!isOpen) {
            // 打开当前下拉菜单
            trigger.setAttribute('aria-expanded', 'true');
            menu.classList.add('header__dropdown-menu--show');
            dropdown.classList.add('header__dropdown--active');
        }
    }

    /**
     * 绑定选择框下拉菜单
     * @param {string} selectId - 选择框ID
     */
    bindSelectDropdown(selectId) {
        const select = document.getElementById(selectId);
        if (select) {
            select.addEventListener('change', (e) => {
                console.log(`${selectId} 选择变更:`, e.target.value);
                // 可以在这里添加选择变更的处理逻辑
            });
        }
    }

    /**
     * 绑定用户菜单事件
     */
    bindUserMenuEvents() {
        const userMenu = document.querySelector('.header__user-menu');
        if (userMenu) {
            const avatar = userMenu.querySelector('.header__user-avatar');
            const dropdown = userMenu.querySelector('.header__user-dropdown');
            
            if (avatar && dropdown) {
                avatar.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggleUserMenu(avatar, dropdown);
                });
            }
        }
    }

    /**
     * 切换用户菜单显示状态
     * @param {Element} avatar - 用户头像按钮
     * @param {Element} dropdown - 下拉菜单
     */
    toggleUserMenu(avatar, dropdown) {
        const isOpen = avatar.getAttribute('aria-expanded') === 'true';
        
        // 关闭所有其他下拉菜单
        this.closeAllDropdowns();
        
        if (!isOpen) {
            // 打开用户菜单
            avatar.setAttribute('aria-expanded', 'true');
            dropdown.classList.add('header__user-dropdown--show');
        }
    }

    /**
     * 关闭所有下拉菜单
     */
    closeAllDropdowns() {
        // 关闭系统配置下拉菜单
        const configTriggers = document.querySelectorAll('.header__dropdown-trigger');
        const configMenus = document.querySelectorAll('.header__dropdown-menu');
        const configDropdowns = document.querySelectorAll('.header__dropdown');
        
        configTriggers.forEach(trigger => {
            trigger.setAttribute('aria-expanded', 'false');
        });
        
        configMenus.forEach(menu => {
            menu.classList.remove('header__dropdown-menu--show');
        });
        
        configDropdowns.forEach(dropdown => {
            dropdown.classList.remove('header__dropdown--active');
        });

        // 关闭用户菜单
        const userAvatars = document.querySelectorAll('.header__user-avatar');
        const userDropdowns = document.querySelectorAll('.header__user-dropdown');
        
        userAvatars.forEach(avatar => {
            avatar.setAttribute('aria-expanded', 'false');
        });
        
        userDropdowns.forEach(dropdown => {
            dropdown.classList.remove('header__user-dropdown--show');
        });
    }

    /**
     * 绑定全局点击事件
     */
    bindGlobalClickEvents() {
        document.addEventListener('click', (e) => {
            // 如果点击的不是下拉菜单相关元素，则关闭所有下拉菜单
            const isDropdownClick = e.target.closest('.header__dropdown') || 
                                  e.target.closest('.header__user-menu');
            
            if (!isDropdownClick) {
                this.closeAllDropdowns();
            }
        });

        // ESC 键关闭下拉菜单
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllDropdowns();
            }
        });
    }

    /**
     * 绑定搜索事件
     */
    bindSearchEvents() {
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            // 搜索输入事件
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                if (query.length > 2) {
                    this.performSearch(query);
                }
            });

            // 回车键搜索
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const query = e.target.value.trim();
                    if (query) {
                        this.performSearch(query);
                    }
                }
            });
        }

        // 日志搜索表单
        const logSearchForm = document.querySelector('form[role="search"]');
        if (logSearchForm) {
            logSearchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performLogSearch();
            });
        }
    }

    /**
     * 执行全局搜索
     * @param {string} query - 搜索查询
     */
    performSearch(query) {
        console.log('执行全局搜索:', query);
        // 这里可以实现实际的搜索逻辑
        // 例如：搜索节点、日志、配置等
    }

    /**
     * 执行日志搜索
     */
    performLogSearch() {
        const logLevel = document.getElementById('log-level')?.value;
        const sourceNode = document.getElementById('source-node')?.value;
        const timeRange = document.getElementById('time-range')?.value;

        console.log('执行日志搜索:', {
            logLevel,
            sourceNode,
            timeRange
        });

        // 这里可以实现实际的日志搜索逻辑
        // 例如：向后端发送搜索请求，更新日志表格等
    }

    /**
     * 获取当前页面
     * @returns {string} 当前页面名称
     */
    getCurrentPage() {
        return this.currentPage;
    }
}

// 创建全局导航管理器实例
window.navigationManager = new NavigationManager();