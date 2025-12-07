/**
 * 导航管理工具类
 * 负责页面导航、下拉菜单和用户交互
 */
class NavigationManager {
    constructor() {
        this.currentPage = 'cluster-list';
        this.logOriginal = [];
        this.logFiltered = [];
        this.logPage = 1;
        this.logPageSize = 10;
        this.logDebounce = null;
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
                this.applyInitialRoute();
                this.bindHashChange();
            });
        } else {
            this.bindEvents();
            this.applyInitialRoute();
            this.bindHashChange();
        }
    }

    /**
     * 绑定所有事件监听器
     */
    bindEvents() {
        this.bindNavigationEvents();
        this.bindSidebarEvents();
        this.bindDropdownEvents();
        this.bindUserMenuEvents();
        this.bindGlobalClickEvents();
        this.bindSearchEvents();
        this.bindClusterListEvents();
        this.bindLogPaginationEvents();
        this.bindSidebarToggle();
        this.bindClusterRegister();
    }

    /**
     * 根据 URL 哈希初始化页面
     */
    applyInitialRoute() {
        const hash = window.location.hash?.replace('#', '') || '';
        const validSection = document.getElementById(hash);
        const auth = window.authManager;
        // 未登录时仅允许进入登录或注册页
        if (auth && !auth.isAuthenticated()) {
            const target = (hash === 'register') ? 'register' : 'login';
            window.location.hash = `#${target}`;
            this.switchPage(target);
            auth.toggleAuthUI();
            return;
        }

        // 已登录则检查路由权限
        if (hash && validSection) {
            if (auth && !auth.allowRoute(hash)) {
                const fallback = auth.getDefaultPage();
                window.location.hash = `#${fallback}`;
                this.switchPage(fallback);
            } else {
                this.switchPage(hash);
            }
        } else {
            const fallback = auth ? auth.getDefaultPage() : 'cluster-list';
            window.location.hash = `#${fallback}`;
            this.switchPage(fallback);
        }
    }

    /**
     * 监听哈希变化以支持浏览器前进/后退
     */
    bindHashChange() {
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash?.replace('#', '') || '';
            if (!hash) return;
            const auth = window.authManager;
            if (auth && !auth.isAuthenticated()) {
                const target = (hash === 'register') ? 'register' : 'login';
                window.location.hash = `#${target}`;
                this.switchPage(target);
                auth.toggleAuthUI();
                return;
            }
            if (auth && !auth.allowRoute(hash)) {
                const fallback = auth.getDefaultPage();
                window.location.hash = `#${fallback}`;
                this.switchPage(fallback);
                return;
            }
            this.switchPage(hash);
        });
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
                if (targetPage) {
                    const auth = window.authManager;
                    if (auth && !auth.isAuthenticated()) {
                        window.location.hash = '#login';
                        this.switchPage('login');
                        auth.toggleAuthUI();
                        return;
                    }
                    if (auth && !auth.allowRoute(targetPage)) {
                        const fallback = auth.getDefaultPage();
                        window.location.hash = `#${fallback}`;
                        this.switchPage(fallback);
                        return;
                    }
                    // 同步哈希，支持刷新与分享链接
                    window.location.hash = `#${targetPage}`;
                    this.switchPage(targetPage);
                }
            });
        });
    }

    /**
     * 绑定侧边栏导航事件
     */
    bindSidebarEvents() {
        const sidebarLinks = document.querySelectorAll('.sidebar__link[href^="#"]');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href') || '';
                const targetPage = href.replace('#', '');
                if (targetPage) {
                    const auth = window.authManager;
                    if (auth && !auth.isAuthenticated()) {
                        window.location.hash = '#login';
                        this.switchPage('login');
                        auth.toggleAuthUI();
                        return;
                    }
                    if (auth && !auth.allowRoute(targetPage)) {
                        const fallback = auth.getDefaultPage();
                        window.location.hash = `#${fallback}`;
                        this.switchPage(fallback);
                        return;
                    }
                    window.location.hash = `#${targetPage}`;
                    this.switchPage(targetPage);
                }
            });
        });
    }

    /**
     * 页面切换功能
     * @param {string} pageName - 目标页面名称
     */
    switchPage(pageName) {
        const auth = window.authManager;
        if (auth && !auth.isAuthenticated()) {
            pageName = (pageName === 'register') ? 'register' : 'login';
        }
        if (auth && !auth.allowRoute(pageName)) {
            pageName = auth.getDefaultPage();
        }
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
        this.updateActiveSidebarItem(pageName);
        
        // 更新当前页面
        this.currentPage = pageName;

        // 触发页面切换事件
        this.onPageSwitch(pageName);

        // 如果存在响应式管理器，切换页面后关闭侧边栏（在移动端体验更好）
        if (window.responsiveManager && typeof window.responsiveManager.closeSidebar === 'function') {
            window.responsiveManager.closeSidebar();
        }

        // 切换后根据角色刷新可见性
        if (auth && typeof auth.applyRolePermissions === 'function') {
            auth.applyRolePermissions();
            auth.toggleAuthUI();
        }
    }

    /**
     * 更新导航项激活状态
     * @param {string} activePage - 激活的页面名称
     */
    updateActiveNavItem(activePage) {
        // 仅当目标页面存在于顶部导航时才更新激活状态
        const activeItem = document.querySelector(`[data-page="${activePage}"]`);
        if (activeItem) {
            // 移除所有激活状态
            const navItems = document.querySelectorAll('.header__nav-item');
            navItems.forEach(item => {
                item.classList.remove('header__nav-item--active');
                item.removeAttribute('aria-current');
            });

            // 添加新的激活状态
            activeItem.classList.add('header__nav-item--active');
            activeItem.setAttribute('aria-current', 'page');
        }
    }

    /**
     * 更新侧边栏激活状态
     * @param {string} activePage - 激活的页面名称
     */
    updateActiveSidebarItem(activePage) {
        const links = document.querySelectorAll('.sidebar__link');
        links.forEach(link => {
            link.classList.remove('sidebar__link--active');
            link.removeAttribute('aria-current');
        });

        const activeLink = document.querySelector(`.sidebar__link[href="#${activePage}"]`);
        if (activeLink) {
            activeLink.classList.add('sidebar__link--active');
            activeLink.setAttribute('aria-current', 'page');
        }
    }

    /**
     * 绑定顶部隐藏侧边栏按钮
     */
    bindSidebarToggle() {
        const btn = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        if (!btn || !sidebar) return;
        btn.addEventListener('click', () => {
            const collapsed = sidebar.classList.toggle('sidebar--collapsed');
            btn.textContent = collapsed ? '显示侧边栏' : '隐藏侧边栏';
            btn.setAttribute('aria-pressed', collapsed ? 'true' : 'false');
        });
    }

    /**
     * 页面切换回调
     * @param {string} pageName - 切换到的页面名称
     */
    onPageSwitch(pageName) {
        // 根据页面执行特定操作
        switch (pageName) {
            case 'dashboard':
                if (window.chartManager) {
                    window.chartManager.resizeAllCharts();
                }
                this.updateDashboardClusterMeta();
                break;
            case 'logs':
                this.captureLogDataset();
                this.applyLogSearch();
                break;
            case 'diagnosis':
                this.initDiagnosisTriplePane();
                this.bindDiagnosisDnD();
                this.bindDiagnosisTreeEvents();
                break;
            case 'profile':
                if (window.authManager && typeof window.authManager.renderProfile === 'function') {
                    window.authManager.renderProfile();
                }
                break;
            case 'cluster-list':
                console.log('切换到 集群列表页面');
                break;
            case 'alert-config':
                this.bindAlertConfig();
                break;
            case 'fault-center':
                this.bindFaultCenterFilters();
                break;
            case 'exec-logs':
                console.log('切换到 执行日志页面');
                break;
        }
    }

    bindFaultCenterFilters() {
        const form = document.getElementById('fault-filter-form');
        const clusterSel = document.getElementById('fault-filter-cluster');
        const nodeSel = document.getElementById('fault-filter-node');
        const timeSel = document.getElementById('fault-filter-time');
        const tbody = document.getElementById('fault-center-tbody');
        if (!tbody) return;
        const apply = () => {
            const c = clusterSel?.value || '';
            const n = nodeSel?.value || '';
            const t = timeSel?.value || '';
            const now = Date.now();
            const toMs = (v) => v==='1h'?3600000:v==='6h'?21600000:v==='24h'?86400000:v==='7d'?604800000:0;
            const range = toMs(t);
            const rows = Array.from(tbody.querySelectorAll('tr.dashboard__table-row'));
            rows.forEach(row => {
                const rc = row.getAttribute('data-cluster') || '';
                const rn = row.getAttribute('data-node') || '';
                const rt = row.getAttribute('data-time') || '';
                let ok = true;
                if (c && rc !== c) ok = false;
                if (ok && n && rn !== n) ok = false;
                if (ok && range) {
                    const ts = Date.parse(rt);
                    if (isNaN(ts) || (now - ts) > range) ok = false;
                }
                row.style.display = ok ? '' : 'none';
            });
        };
        ['change','input'].forEach(evt => {
            clusterSel?.addEventListener(evt, apply);
            nodeSel?.addEventListener(evt, apply);
            timeSel?.addEventListener(evt, apply);
        });
        apply();
    }

    bindAlertConfig() {
        const addBtn = document.getElementById('alert-add-rule');
        const modal = document.getElementById('alert-add-modal');
        const form = document.getElementById('alert-add-form');
        const cancel = document.getElementById('alert-rule-cancel');
        const err = document.getElementById('alert-add-error');
        const tbody = document.getElementById('alert-rules-tbody');
        const table = document.getElementById('alert-rules-table');
        if (addBtn && modal) {
            addBtn.addEventListener('click', () => { modal.style.display = ''; });
        }
        if (cancel && modal) {
            cancel.addEventListener('click', () => {
                modal.style.display = 'none';
                if (err) { err.style.display = 'none'; err.textContent = ''; }
                form?.reset();
            });
        }
        if (form && tbody) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const name = document.getElementById('alert-rule-name')?.value.trim();
                const cond = document.getElementById('alert-rule-cond')?.value.trim();
                const level = document.getElementById('alert-rule-level')?.value;
                const channel = document.getElementById('alert-rule-channel')?.value;
                if (!name || !cond) {
                    if (err) { err.style.display = ''; err.textContent = '请填写规则名称与条件'; }
                    return;
                }
                if (Array.from(tbody.querySelectorAll('tr')).some(tr => tr.querySelector('td')?.textContent === name)) {
                    if (err) { err.style.display = ''; err.textContent = '规则名称已存在'; }
                    return;
                }
                const tr = document.createElement('tr');
                tr.className = 'dashboard__table-row';
                tr.innerHTML = `
                    <td class="dashboard__table-td">${name}</td>
                    <td class="dashboard__table-td">${cond}</td>
                    <td class="dashboard__table-td"><span class="u-text-${level==='WARN'?'warning':level==='ERROR'?'error':'primary'}">${level}</span></td>
                    <td class="dashboard__table-td">${channel}</td>
                    <td class="dashboard__table-td">
                        <button class="btn u-text-sm" data-action="rule-edit" data-name="${name}" data-requires-edit="true">编辑</button>
                        <button class="btn u-text-sm u-ml-1" data-action="rule-delete" data-name="${name}" data-requires-edit="true">删除</button>
                    </td>`;
                tbody.appendChild(tr);
                modal.style.display = 'none';
                if (err) { err.style.display = 'none'; err.textContent = ''; }
                form.reset();
            });
        }
        if (table && !table.__binded) {
            table.__binded = true;
            table.addEventListener('click', (e) => {
                const btn = e.target.closest('button[data-action]');
                if (!btn) return;
                const action = btn.getAttribute('data-action');
                const name = btn.getAttribute('data-name') || '';
                if (action === 'rule-delete') {
                    const row = btn.closest('tr');
                    if (row) row.remove();
                } else if (action === 'rule-edit') {
                    if (modal && form) {
                        const row = btn.closest('tr');
                        const cells = row ? row.querySelectorAll('td') : null;
                        if (cells && cells.length >= 4) {
                            document.getElementById('alert-rule-name').value = cells[0].textContent || '';
                            document.getElementById('alert-rule-cond').value = cells[1].textContent || '';
                            document.getElementById('alert-rule-level').value = (cells[2].textContent || '').trim();
                            document.getElementById('alert-rule-channel').value = cells[3].textContent || '';
                            modal.style.display = '';
                            form.addEventListener('submit', (ev) => {
                                ev.preventDefault();
                                cells[0].textContent = document.getElementById('alert-rule-name').value.trim();
                                cells[1].textContent = document.getElementById('alert-rule-cond').value.trim();
                                const lvl = document.getElementById('alert-rule-level').value;
                                cells[2].innerHTML = `<span class="u-text-${lvl==='WARN'?'warning':lvl==='ERROR'?'error':'primary'}">${lvl}</span>`;
                                cells[3].textContent = document.getElementById('alert-rule-channel').value;
                                modal.style.display = 'none';
                                if (err) { err.style.display = 'none'; err.textContent = ''; }
                                form.reset();
                            }, { once: true });
                        }
                    }
                }
            });
        }
    }

    /**
     * 初始化故障诊断页面分割布局，支持拖动调整左右面板宽度
     */
    initDiagnosisTriplePane() {
        const left = document.getElementById('diag-left');
        const mid = document.getElementById('diag-middle');
        const right = document.getElementById('diag-right');
        const d1 = document.getElementById('diag-divider-1');
        const d2 = document.getElementById('diag-divider-2');
        if (!left || !mid || !right || !d1 || !d2) return;
        let drag1 = false, drag2 = false, startX1 = 0, startX2 = 0;
        let leftW = left.getBoundingClientRect().width;
        let midW = mid.getBoundingClientRect().width;
        let rightW = right.getBoundingClientRect().width;
        const minLeft = 240, minMid = 300, minRight = 320;
        const onMove1 = (e) => {
            if (!drag1) return;
            const dx = e.clientX - startX1;
            const newLeft = Math.max(minLeft, leftW + dx);
            const delta = newLeft - leftW;
            const newMid = Math.max(minMid, midW - delta);
            left.style.width = `${newLeft}px`;
            mid.style.width = `${newMid}px`;
        };
        const onUp1 = () => {
            drag1 = false;
            leftW = left.getBoundingClientRect().width;
            midW = mid.getBoundingClientRect().width;
            document.removeEventListener('mousemove', onMove1);
            document.removeEventListener('mouseup', onUp1);
        };
        d1.addEventListener('mousedown', (e) => {
            drag1 = true;
            startX1 = e.clientX;
            leftW = left.getBoundingClientRect().width;
            midW = mid.getBoundingClientRect().width;
            document.addEventListener('mousemove', onMove1);
            document.addEventListener('mouseup', onUp1);
        });
        const onMove2 = (e) => {
            if (!drag2) return;
            const dx = startX2 - e.clientX;
            const newRight = Math.max(minRight, rightW + dx);
            const delta = newRight - rightW;
            const newMid = Math.max(minMid, midW - delta);
            right.style.width = `${newRight}px`;
            mid.style.width = `${newMid}px`;
        };
        const onUp2 = () => {
            drag2 = false;
            rightW = right.getBoundingClientRect().width;
            midW = mid.getBoundingClientRect().width;
            document.removeEventListener('mousemove', onMove2);
            document.removeEventListener('mouseup', onUp2);
        };
        d2.addEventListener('mousedown', (e) => {
            drag2 = true;
            startX2 = e.clientX;
            rightW = right.getBoundingClientRect().width;
            midW = mid.getBoundingClientRect().width;
            document.addEventListener('mousemove', onMove2);
            document.addEventListener('mouseup', onUp2);
        });
    }

    /**
     * 绑定左侧日志/节点到右侧聊天框的拖拽交互
     */
    bindDiagnosisDnD() {
        const chatInput = document.getElementById('chat-input');
        if (!chatInput) return;
        chatInput.addEventListener('dragover', (e) => { e.preventDefault(); });
        chatInput.addEventListener('drop', (e) => {
            e.preventDefault();
            const data = e.dataTransfer?.getData('text/plain') || '';
            chatInput.value = `${chatInput.value}\n${data}`.trim();
        });
        const left = document.getElementById('diag-left');
        if (left) {
            left.addEventListener('dragstart', (e) => {
                const t = e.target;
                if (!t) return;
                const log = t.getAttribute('data-log');
                const node = t.getAttribute('data-node');
                const text = log || node || '';
                if (text && e.dataTransfer) e.dataTransfer.setData('text/plain', text);
            });
        }
    }

    bindDiagnosisTreeEvents() {
        const tree = document.getElementById('diag-tree');
        const search = document.getElementById('diag-tree-search');
        const list = document.getElementById('diag-live-logs-list');
        if (!tree) return;
        const render = (rows) => {
            const content = document.getElementById('diag-preview-content');
            const ld = document.getElementById('diag-preview-loading');
            const err = document.getElementById('diag-preview-error');
            if (!content) return;
            if (ld) ld.style.display = 'none';
            if (err) err.style.display = 'none';
            content.textContent = rows.length ? rows.map(r => r.message || '').join('\n\n') : '无相关日志';
        };
        const renderList = (rows) => {
            if (!list) return;
            list.innerHTML = rows.length ? rows.map((r, i) => {
                const t = (r.time || '').split('T')[1] || r.time;
                const head = (r.message || '').split('\n')[0].slice(0, 100);
                return `<button class="btn diag-log-btn" draggable="true" data-diag-idx="${i}" data-log="${r.message || ''}">[${r.level.toUpperCase()}] ${r.node} ${t} - ${head}</button>`;
            }).join('') : '<div class="u-text-sm u-text-gray-500">无相关日志</div>';
        };
        const ensureDataset = () => {
            if (!(this.logOriginal && this.logOriginal.length)) {
                const body = document.getElementById('logs-tbody');
                if (body) {
                    const rows = Array.from(body.querySelectorAll('tr.dashboard__table-row'));
                    this.logOriginal = rows.map(r => ({
                        time: r.querySelector('time')?.getAttribute('datetime') || '',
                        level: (r.querySelector('.u-font-medium')?.textContent || '').toLowerCase(),
                        cluster: r.getAttribute('data-cluster') || '',
                        node: r.getAttribute('data-node') || '',
                        message: r.querySelectorAll('td.dashboard__table-td')?.[6]?.textContent || ''
                    }));
                } else {
                    this.logOriginal = [];
                }
            }
        };
        tree.addEventListener('click', (e) => {
            const arrow = e.target.closest('.cluster-toggle-icon');
            const cBtn = e.target.closest('[data-cluster]');
            const nItem = e.target.closest('[data-node]');
            ensureDataset();
            if (arrow && cBtn) {
                const li = cBtn.parentElement;
                const nodes = li ? li.querySelector('.diag-node-list') : null;
                if (nodes) {
                    const collapsed = nodes.classList.toggle('diag-node-list--collapsed');
                    arrow.classList.remove('fa-chevron-right','fa-chevron-down');
                    arrow.classList.add(collapsed ? 'fa-chevron-right' : 'fa-chevron-down');
                }
                e.preventDefault();
                return;
            }
            if (cBtn) {
                const uuid = cBtn.getAttribute('data-cluster') || '';
                const rows = (this.logOriginal||[]).filter(x => x.cluster === uuid);
                this.diagFiltered = rows;
                renderList(rows);
                return;
            }
            if (nItem) {
                const nid = nItem.getAttribute('data-node') || '';
                const rows = (this.logOriginal||[]).filter(x => x.node === nid);
                this.diagFiltered = rows;
                renderList(rows);
            }
        });
        if (list && !list.__binded) {
            list.__binded = true;
            list.addEventListener('click', (e) => {
                const btn = e.target.closest('.diag-log-btn');
                if (!btn) return;
                const idx = parseInt(btn.getAttribute('data-diag-idx') || '-1', 10);
                const rows = this.diagFiltered || [];
                const item = rows[idx];
                if (!item) return;
                const content = document.getElementById('diag-preview-content');
                if (content) content.textContent = item.message || '';
            });
        }
        if (search) {
            search.addEventListener('input', (e) => {
                const kw = (e.target.value||'').trim().toLowerCase();
                const clusters = tree.querySelectorAll('[data-cluster]');
                clusters.forEach(el => {
                    const v = (el.getAttribute('data-cluster')||'').toLowerCase();
                    const visible = !kw || v.includes(kw);
                    const li = el.parentElement;
                    if (li) li.style.display = visible ? '' : 'none';
                });
            });
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

                // 菜单项点击：切换页面并收起菜单
                const menuLinks = menu.querySelectorAll('a[href^="#"]');
                menuLinks.forEach(link => {
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        const targetPage = (link.getAttribute('href') || '').replace('#', '');
                        if (targetPage) {
                            const auth = window.authManager;
                            if (auth && !auth.isAuthenticated()) {
                                window.location.hash = '#login';
                                this.switchPage('login');
                                auth.toggleAuthUI();
                                return;
                            }
                            if (auth && !auth.allowRoute(targetPage)) {
                                const fallback = auth.getDefaultPage();
                                window.location.hash = `#${fallback}`;
                                this.switchPage(fallback);
                                return;
                            }
                            window.location.hash = `#${targetPage}`;
                            this.switchPage(targetPage);
                            // 收起下拉菜单
                            this.closeAllDropdowns();
                        }
                    });
                });
            }
        }

        // 日志级别下拉菜单
        this.bindSelectDropdown('log-level');
        
        // 来源节点下拉菜单
        this.bindSelectDropdown('source-node');
        
        // 时间范围下拉菜单
        this.bindSelectDropdown('time-range');
        // 来源集群下拉菜单
        this.bindSelectDropdown('source-cluster');
        // 操作类型下拉菜单
        this.bindSelectDropdown('op-type');
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

                // 用户菜单项点击：切换页面并收起菜单
                const menuLinks = dropdown.querySelectorAll('a[href^="#"]');
                menuLinks.forEach(link => {
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        const targetPage = (link.getAttribute('href') || '').replace('#', '');
                        if (targetPage) {
                            const auth = window.authManager;
                            if (targetPage === 'logout') {
                                if (auth && typeof auth.logout === 'function') {
                                    auth.logout();
                                }
                                window.location.hash = '#login';
                                this.switchPage('login');
                                avatar.setAttribute('aria-expanded', 'false');
                                dropdown.classList.remove('header__user-dropdown--show');
                                return;
                            }
                            if (auth && !auth.isAuthenticated()) {
                                window.location.hash = '#login';
                                this.switchPage('login');
                                avatar.setAttribute('aria-expanded', 'false');
                                dropdown.classList.remove('header__user-dropdown--show');
                                if (auth) auth.toggleAuthUI();
                                return;
                            }
                            if (auth && !auth.allowRoute(targetPage)) {
                                const fallback = auth.getDefaultPage();
                                window.location.hash = `#${fallback}`;
                                this.switchPage(fallback);
                                avatar.setAttribute('aria-expanded', 'false');
                                dropdown.classList.remove('header__user-dropdown--show');
                                return;
                            }
                            window.location.hash = `#${targetPage}`;
                            this.switchPage(targetPage);
                            // 收起用户菜单
                            avatar.setAttribute('aria-expanded', 'false');
                            dropdown.classList.remove('header__user-dropdown--show');
                        }
                    });
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
        const logSearchForm = document.getElementById('log-search-form');
        if (logSearchForm) {
            logSearchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performLogSearch();
            });
            // 实时搜索（防抖）
            ['log-level','source-cluster','source-node','op-type','user-id','time-range'].forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                const evt = (el.tagName === 'INPUT') ? 'input' : 'change';
                el.addEventListener(evt, () => this.applyLogSearch());
            });
            const clearBtn = document.getElementById('log-clear-filters');
            if (clearBtn) clearBtn.addEventListener('click', () => this.clearLogFilters());
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
        this.applyLogSearch(true);
    }

    /**
     * 获取并备份日志原始数据集
     */
    captureLogDataset() {
        if (this.logOriginal && this.logOriginal.length) return;
        const tbody = document.getElementById('logs-tbody');
        if (!tbody) return;
        const rows = Array.from(tbody.querySelectorAll('tr.dashboard__table-row'));
        this.logOriginal = rows.map(r => ({
            time: r.querySelector('time')?.getAttribute('datetime') || '',
            level: (r.querySelector('.u-font-medium')?.textContent || '').toLowerCase(),
            cluster: r.getAttribute('data-cluster') || '',
            node: r.getAttribute('data-node') || '',
            op: r.getAttribute('data-op') || '',
            user: r.getAttribute('data-user') || '',
            message: r.querySelectorAll('td.dashboard__table-td')?.[6]?.textContent || ''
        }));
        this.logFiltered = [...this.logOriginal];
    }

    /**
     * 应用筛选与搜索（支持防抖、权限过滤、脱敏、分页）
     * @param {boolean} manual - 是否人为触发
     */
    applyLogSearch(manual = false) {
        const start = Date.now();
        const setLoading = (v) => {
            const ld = document.getElementById('log-loading');
            if (ld) ld.style.display = v ? '' : 'none';
        };
        setLoading(true);
        if (this.logDebounce) clearTimeout(this.logDebounce);
        this.logDebounce = setTimeout(() => {
            const role = window.authManager?.getRole();
            const q = {
                level: document.getElementById('log-level')?.value || '',
                cluster: document.getElementById('source-cluster')?.value || '',
                node: document.getElementById('source-node')?.value || '',
                op: document.getElementById('op-type')?.value || '',
                user: (document.getElementById('user-id')?.value || '').trim().toLowerCase(),
            };
            let data = [...this.logOriginal];
            data = this.applyRoleLogScope(data, role);
            data = data.filter(item => (
                (!q.level || item.level === q.level)
                && (!q.cluster || item.cluster === q.cluster)
                && (!q.node || item.node === q.node)
                && (!q.op || item.op === q.op)
                && (!q.user || item.user.toLowerCase().includes(q.user))
            ));
            data = this.maskSensitiveForRole(data, role);
            this.logFiltered = data;
            this.logPage = 1;
            this.updateFilterSummary(q);
            this.renderLogs();
            setLoading(false);
            if (Date.now() - start > 2000) console.warn('搜索响应超过2秒');
        }, manual ? 0 : 300);
    }

    /**
     * 渲染日志列表（分页）
     */
    renderLogs() {
        const tbody = document.getElementById('logs-tbody');
        const pageInfo = document.getElementById('log-page-info');
        if (!tbody) return;
        const size = this.logPageSize;
        const begin = (this.logPage - 1) * size;
        const end = begin + size;
        const pageData = this.logFiltered.slice(begin, end);
        tbody.innerHTML = pageData.map(item => `
            <tr class="dashboard__table-row" data-cluster="${item.cluster}" data-node="${item.node}" data-op="${item.op}" data-user="${item.user}">
                <td class="dashboard__table-td"><time datetime="${item.time}">${(item.time || '').split('T')[1] || item.time}</time></td>
                <td class="dashboard__table-td"><span class="u-font-medium">${item.level.toUpperCase()}</span></td>
                <td class="dashboard__table-td"><code>${item.cluster}</code></td>
                <td class="dashboard__table-td">${item.node}</td>
                <td class="dashboard__table-td">${item.op}</td>
                <td class="dashboard__table-td">${item.user}</td>
                <td class="dashboard__table-td">${item.message}</td>
            </tr>
        `).join('');
        if (pageInfo) pageInfo.textContent = `第 ${this.logPage} 页`;
    }

    /**
     * 清除筛选并恢复原始数据
     */
    clearLogFilters() {
        ['log-level','source-cluster','source-node','op-type','user-id','time-range'].forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            if (el.tagName === 'SELECT') el.selectedIndex = 0; else el.value = '';
        });
        this.logFiltered = [...this.logOriginal];
        this.logPage = 1;
        this.updateFilterSummary({});
        this.renderLogs();
    }

    /**
     * 角色日志范围过滤
     * @param {Array} data - 原始日志列表
     * @param {string} role - 角色
     */
    applyRoleLogScope(data, role) {
        if (role === 'admin') return data;
        if (role === 'operator') {
            const visibleClusters = ['CL-1111-AAAA','CL-2222-BBBB'];
            return data.filter(d => visibleClusters.includes(d.cluster));
        }
        if (role === 'observer' || role === 'user') {
            const visibleClusters = ['CL-1111-AAAA'];
            return data.filter(d => visibleClusters.includes(d.cluster));
        }
        return [];
    }

    /**
     * 敏感信息脱敏
     * @param {Array} data - 日志列表
     * @param {string} role - 角色
     */
    maskSensitiveForRole(data, role) {
        const sensitiveOps = ['security'];
        if (role === 'admin') return data;
        return data.map(d => sensitiveOps.includes(d.op) ? { ...d, message: '***' } : d);
    }

    /**
     * 更新筛选摘要
     * @param {Object} q - 查询条件
     */
    updateFilterSummary(q) {
        const el = document.getElementById('log-filter-summary');
        if (!el) return;
        const parts = [];
        if (q.level) parts.push(`级别=${q.level}`);
        if (q.cluster) parts.push(`集群=${q.cluster}`);
        if (q.node) parts.push(`节点=${q.node}`);
        if (q.op) parts.push(`操作=${q.op}`);
        if (q.user) parts.push(`用户=${q.user}`);
        el.textContent = parts.length ? `当前筛选：${parts.join('，')}` : '当前筛选：无';
    }

    /**
     * 绑定分页事件
     */
    bindLogPaginationEvents() {
        const prev = document.getElementById('log-prev');
        const next = document.getElementById('log-next');
        const sizeSel = document.getElementById('log-page-size');
        if (prev) prev.addEventListener('click', () => {
            if (this.logPage > 1) { this.logPage -= 1; this.renderLogs(); }
        });
        if (next) next.addEventListener('click', () => {
            const maxPage = Math.max(1, Math.ceil(this.logFiltered.length / this.logPageSize));
            if (this.logPage < maxPage) { this.logPage += 1; this.renderLogs(); }
        });
        if (sizeSel) sizeSel.addEventListener('change', (e) => {
            this.logPageSize = parseInt(e.target.value, 10) || 10;
            this.logPage = 1;
            this.renderLogs();
        });
    }

    /**
     * 绑定集群列表事件：点击行进入详情页
     */
    bindClusterListEvents() {
        const table = document.getElementById('cluster-list-table');
        if (!table || table.__binded) return;
        table.__binded = true;
        table.addEventListener('click', (e) => {
            const btn = e.target.closest('button[data-action="unregister-cluster"]');
            if (btn) {
                e.stopPropagation();
                const uuid = btn.getAttribute('data-cluster-uuid') || '';
                const tr = btn.closest('tr');
                if (tr) tr.remove();
                return;
            }
            const tr = e.target.closest('tr[data-cluster-uuid]');
            if (!tr) return;
            const uuid = tr.getAttribute('data-cluster-uuid') || '';
            const host = tr.getAttribute('data-master-host') || '';
            const ip = tr.getAttribute('data-master-ip') || '';
            window.selectedCluster = { uuid, host, ip };
            window.location.hash = '#dashboard';
            this.switchPage('dashboard');
        });
    }

    bindClusterRegister() {
        const toggle = document.getElementById('cluster-register-toggle');
        const panel = document.getElementById('cluster-register-panel');
        const form = document.getElementById('cluster-register-form');
        const cancel = document.getElementById('cluster-register-cancel');
        const error = document.getElementById('cluster-register-error');
        const tbody = document.getElementById('cluster-list-tbody');
        if (toggle && panel) {
            toggle.addEventListener('click', () => {
                panel.style.display = panel.style.display === 'none' ? '' : 'none';
            });
        }
        if (cancel && panel && form) {
            cancel.addEventListener('click', () => {
                panel.style.display = 'none';
                if (error) { error.style.display = 'none'; error.textContent = ''; }
                form.reset();
            });
        }
        if (form && tbody) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const uuid = document.getElementById('reg-cluster-uuid')?.value.trim();
                const host = document.getElementById('reg-master-host')?.value.trim();
                const ip = document.getElementById('reg-master-ip')?.value.trim();
                const count = document.getElementById('reg-node-count')?.value.trim();
                const health = document.getElementById('reg-health')?.value;
                if (!uuid || !host || !ip || !count) {
                    if (error) { error.style.display = ''; error.textContent = '请填写完整信息'; }
                    return;
                }
                if (Array.from(tbody.querySelectorAll('tr')).some(tr => (tr.getAttribute('data-cluster-uuid') || '') === uuid)) {
                    if (error) { error.style.display = ''; error.textContent = '该集群UUID已存在'; }
                    return;
                }
                const tr = document.createElement('tr');
                tr.className = 'dashboard__table-row';
                tr.setAttribute('data-cluster-uuid', uuid);
                tr.setAttribute('data-master-host', host);
                tr.setAttribute('data-master-ip', ip);
                tr.innerHTML = `
                    <td class="dashboard__table-td"><code>${uuid}</code></td>
                    <td class="dashboard__table-td">${host}</td>
                    <td class="dashboard__table-td">${ip}</td>
                    <td class="dashboard__table-td">${count}</td>
                    <td class="dashboard__table-td">
                        <span class="dashboard__status-indicator">
                            <span class="dashboard__status-dot dashboard__status-dot--${health}" aria-hidden="true"></span>
                            <span class="dashboard__status-text">${health==='running'?'健康':health==='warning'?'警告':'异常'}</span>
                        </span>
                    </td>
                    <td class="dashboard__table-td">
                        <button class="btn u-text-sm" data-action="unregister-cluster" data-cluster-uuid="${uuid}" data-requires-edit="true">注销集群</button>
                    </td>`;
                tbody.appendChild(tr);
                panel.style.display = 'none';
                if (error) { error.style.display = 'none'; error.textContent = ''; }
                form.reset();
            });
        }
    }

    /**
     * 更新仪表板顶部当前集群元信息
     */
    updateDashboardClusterMeta() {
        const meta = window.selectedCluster || { uuid: '未选择', host: '-', ip: '-' };
        const uuidEl = document.getElementById('current-cluster-uuid');
        const hostEl = document.getElementById('current-cluster-master-host');
        const ipEl = document.getElementById('current-cluster-master-ip');
        if (uuidEl) uuidEl.textContent = meta.uuid || '未选择';
        if (hostEl) hostEl.textContent = meta.host || '-';
        if (ipEl) ipEl.textContent = meta.ip || '-';
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
