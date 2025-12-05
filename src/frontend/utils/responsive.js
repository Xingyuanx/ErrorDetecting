/**
 * 响应式交互管理工具类
 * 负责移动端菜单、侧边栏切换和响应式行为
 */
class ResponsiveManager {
    constructor() {
        this.isMobile = false;
        this.isTablet = false;
        this.sidebarOpen = false;
        this.mobileMenuOpen = false;
        
        this.init();
    }

    /**
     * 初始化响应式功能
     */
    init() {
        // 等待 DOM 加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setup();
            });
        } else {
            this.setup();
        }
    }

    /**
     * 设置响应式功能
     */
    setup() {
        this.createMobileElements();
        this.bindEvents();
        this.checkScreenSize();
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    /**
     * 创建移动端需要的元素
     */
    createMobileElements() {
        this.createMobileMenuButton();
        this.createSidebarOverlay();
    }

    /**
     * 创建移动端菜单按钮
     */
    createMobileMenuButton() {
        const headerLeft = document.querySelector('.header__left');
        if (!headerLeft) return;

        // 检查是否已存在
        if (document.querySelector('.header__mobile-menu-btn')) return;

        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.className = 'header__mobile-menu-btn';
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars" aria-hidden="true"></i>';
        mobileMenuBtn.setAttribute('aria-label', '打开导航菜单');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');

        // 插入到 logo 之后
        const logo = headerLeft.querySelector('.header__logo');
        if (logo && logo.nextSibling) {
            headerLeft.insertBefore(mobileMenuBtn, logo.nextSibling);
        } else {
            headerLeft.appendChild(mobileMenuBtn);
        }
    }

    /**
     * 创建侧边栏遮罩层
     */
    createSidebarOverlay() {
        const container = document.querySelector('.layout__container');
        if (!container) return;

        // 检查是否已存在
        if (document.querySelector('.sidebar-overlay')) return;

        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.setAttribute('aria-hidden', 'true');

        container.appendChild(overlay);
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 移动端菜单按钮
        const mobileMenuBtn = document.querySelector('.header__mobile-menu-btn');
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleMobileMenu();
            });
        }

        // 侧边栏遮罩层点击
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeSidebar();
            });
        }

        // ESC 键关闭菜单
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeMobileMenu();
                this.closeSidebar();
            }
        });

        // 导航项点击时关闭移动端菜单
        const navItems = document.querySelectorAll('.header__nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                if (this.isMobile) {
                    this.closeMobileMenu();
                }
            });
        });
    }

    /**
     * 检查屏幕尺寸
     */
    checkScreenSize() {
        const width = window.innerWidth;
        
        this.isMobile = width <= 768;
        this.isTablet = width > 768 && width <= 1024;
        
        // 根据屏幕尺寸调整布局
        this.adjustLayout();
    }

    /**
     * 处理窗口大小变化
     */
    handleResize() {
        const wasMobile = this.isMobile;
        this.checkScreenSize();
        
        // 如果从移动端切换到桌面端，关闭移动端菜单
        if (wasMobile && !this.isMobile) {
            this.closeMobileMenu();
            this.closeSidebar();
        }

        // 通知图表管理器调整大小
        if (window.chartManager) {
            setTimeout(() => {
                window.chartManager.resizeAllCharts();
            }, 300);
        }
    }

    /**
     * 调整布局
     */
    adjustLayout() {
        const body = document.body;
        
        // 添加屏幕尺寸类名
        body.classList.remove('is-mobile', 'is-tablet', 'is-desktop');
        
        if (this.isMobile) {
            body.classList.add('is-mobile');
        } else if (this.isTablet) {
            body.classList.add('is-tablet');
        } else {
            body.classList.add('is-desktop');
        }
    }

    /**
     * 切换移动端菜单
     */
    toggleMobileMenu() {
        if (this.mobileMenuOpen) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    /**
     * 打开移动端菜单
     */
    openMobileMenu() {
        const nav = document.querySelector('.header__nav');
        const btn = document.querySelector('.header__mobile-menu-btn');
        
        if (nav && btn) {
            nav.classList.add('header__nav--mobile-open');
            btn.setAttribute('aria-expanded', 'true');
            btn.innerHTML = '<i class="fas fa-times" aria-hidden="true"></i>';
            
            this.mobileMenuOpen = true;
            
            // 阻止背景滚动
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * 关闭移动端菜单
     */
    closeMobileMenu() {
        const nav = document.querySelector('.header__nav');
        const btn = document.querySelector('.header__mobile-menu-btn');
        
        if (nav && btn) {
            nav.classList.remove('header__nav--mobile-open');
            btn.setAttribute('aria-expanded', 'false');
            btn.innerHTML = '<i class="fas fa-bars" aria-hidden="true"></i>';
            
            this.mobileMenuOpen = false;
            
            // 恢复背景滚动
            document.body.style.overflow = '';
        }
    }

    /**
     * 切换侧边栏
     */
    toggleSidebar() {
        if (this.sidebarOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    /**
     * 打开侧边栏
     */
    openSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar && overlay) {
            sidebar.classList.add('sidebar--mobile-open');
            overlay.classList.add('sidebar-overlay--show');
            
            this.sidebarOpen = true;
            
            // 阻止背景滚动
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * 关闭侧边栏
     */
    closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar && overlay) {
            sidebar.classList.remove('sidebar--mobile-open');
            overlay.classList.remove('sidebar-overlay--show');
            
            this.sidebarOpen = false;
            
            // 恢复背景滚动
            document.body.style.overflow = '';
        }
    }

    /**
     * 获取当前屏幕类型
     * @returns {string} 屏幕类型：'mobile', 'tablet', 'desktop'
     */
    getScreenType() {
        if (this.isMobile) return 'mobile';
        if (this.isTablet) return 'tablet';
        return 'desktop';
    }

    /**
     * 检查是否为移动端
     * @returns {boolean}
     */
    isMobileDevice() {
        return this.isMobile;
    }

    /**
     * 检查是否为平板端
     * @returns {boolean}
     */
    isTabletDevice() {
        return this.isTablet;
    }

    /**
     * 检查是否为桌面端
     * @returns {boolean}
     */
    isDesktopDevice() {
        return !this.isMobile && !this.isTablet;
    }

    /**
     * 添加触摸手势支持
     */
    addTouchSupport() {
        let startX = 0;
        let startY = 0;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            if (!this.isMobile) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // 水平滑动距离大于垂直滑动距离，且滑动距离足够
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                // 从左边缘向右滑动，打开侧边栏
                if (startX < 50 && deltaX > 0 && !this.sidebarOpen) {
                    this.openSidebar();
                }
                // 向左滑动，关闭侧边栏
                else if (deltaX < -50 && this.sidebarOpen) {
                    this.closeSidebar();
                }
            }
        }, { passive: true });
    }
}

// 创建全局响应式管理器实例
window.responsiveManager = new ResponsiveManager();

// 添加触摸手势支持
window.responsiveManager.addTouchSupport();