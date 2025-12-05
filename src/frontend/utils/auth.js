/**
 * 简易前端权限与认证管理
 * - 统一登录与注册事件
 * - 角色：admin / operator / observer
 * - 路由白名单与页面元素显示控制
 */
(function () {
  class AuthManager {
    constructor() {
      this.user = null; // { username, role }
      this.approvalQueue = []; // 注册审批队列（前端占位）
      this.users = [];
      this._confirmCb = null;
      this.restore();
      this.bindForms();
      this.bootstrapApprovals();
      this.bootstrapUsers();
      this.initUserManagement();
      this.bindConfirmModal();
    }

    // 状态持久化
    restore() {
      try {
        const raw = localStorage.getItem('cm_user');
        if (raw) this.user = JSON.parse(raw);
        const rawUsers = localStorage.getItem('cm_users_list');
        if (rawUsers) this.users = JSON.parse(rawUsers);
      } catch (e) {}
    }
    persist() {
      if (this.user) {
        localStorage.setItem('cm_user', JSON.stringify(this.user));
      } else {
        localStorage.removeItem('cm_user');
      }
      if (Array.isArray(this.users)) {
        localStorage.setItem('cm_users_list', JSON.stringify(this.users));
      }
    }

    isAuthenticated() {
      return !!(this.user && this.user.username && this.user.role);
    }

    getRole() {
      return this.user?.role || null;
    }

    getDefaultPage() {
      const role = this.getRole();
      if (role === 'admin') return 'cluster-list';
      if (role === 'operator') return 'cluster-list';
      if (role === 'observer') return 'cluster-list';
      return 'login';
    }

    // 路由访问控制
    allowRoute(page) {
      // 公共页
      const publicPages = ['login', 'register'];
      if (publicPages.includes(page)) return true;

      const role = this.getRole();
      if (!role) return false;

      const basePages = [
        'cluster-list', 'dashboard', 'logs', 'diagnosis',
        'fault-center', 'exec-logs', 'flume-config', 'alert-config', 'llm-config',
        'profile', 'account', 'audit-logs'
      ];

      if (role === 'admin') {
        return basePages.concat(['user-management', 'role-assignment', 'permission-policy']).includes(page);
      }
      if (role === 'operator') {
        // 操作者可见基础监控与故障管理 + 个人主页/账号管理
        const operatorPages = ['cluster-list', 'dashboard', 'logs', 'diagnosis', 'fault-center', 'exec-logs', 'profile', 'account'];
        return operatorPages.includes(page);
      }
      if (role === 'observer' || role === 'user') {
        const observerPages = ['cluster-list', 'dashboard', 'logs', 'fault-center', 'exec-logs', 'profile', 'account'];
        return observerPages.includes(page);
      }
      return false;
    }

    // 登录与注册
    login(username, password) {
      // 演示账号
      const demo = {
        admin: { u: 'admin', p: 'admin123', role: 'admin' },
        ops: { u: 'ops', p: 'ops123', role: 'operator' },
        obs: { u: 'obs', p: 'obs123', role: 'observer' },
      };

      const matched = Object.values(demo).find(d => d.u === username && d.p === password);
      if (matched) {
        this.user = { username, role: matched.role };
        this.persist();
        return { ok: true, role: matched.role };
      }
      return { ok: false, message: '账号或密码错误' };
    }

    logout() {
      this.user = null;
      this.persist();
      this.toggleAuthUI();
    }

    register({ username, password, confirm, contact, role }) {
      if (!username || !password || !confirm || !contact) {
        return { ok: false, message: '请填写所有必填字段' };
      }
      if (password !== confirm) {
        return { ok: false, message: '两次密码不一致' };
      }
      // 进入审批队列（前端占位）
      const item = { username, role: role || 'operator', contact, status: 'pending' };
      this.approvalQueue.push(item);
      this.renderApprovalQueue();
      return { ok: true };
    }

    // 根据角色应用界面权限
    applyRolePermissions() {
      const role = this.getRole();

      // 侧边栏与管理员专属元素
      const sidebar = document.querySelector('.sidebar');
      document.querySelectorAll('[data-role="admin-only"]').forEach(el => {
        el.style.display = (role === 'admin') ? '' : 'none';
      });
      if (sidebar) {
        sidebar.style.display = (role === 'admin') ? '' : 'none';
      }

      // 禁用编辑操作：
      // - 观察者：仅在故障中心可编辑，其他页面禁用
      // - 操作者：仅在允许页面启用编辑
      const isObserver = role === 'observer';
      const isOperator = role === 'operator';
      const current = window.navigationManager?.getCurrentPage();
      const operatorEditable = ['dashboard', 'diagnosis', 'fault-center', 'exec-logs'];
      document.querySelectorAll('[data-requires-edit="true"]').forEach(el => {
        if (isObserver && current !== 'fault-center') {
          el.setAttribute('disabled', 'true');
          el.title = '观察者在当前页面不可执行变更';
        } else if (isOperator && !operatorEditable.includes(current)) {
          el.setAttribute('disabled', 'true');
          el.title = '操作者在当前页面不可执行变更';
        } else {
          el.removeAttribute('disabled');
          el.removeAttribute('title');
        }
      });

      // 观察者页面：隐藏仪表板中的节点操作按钮
      const nodeOpButtons = document.querySelectorAll('[data-action="start-node"],[data-action="stop-node"],[data-action="delete-node"]');
      nodeOpButtons.forEach(el => {
        if (isObserver) {
          el.style.display = 'none';
        } else {
          el.style.display = '';
        }
      });

      // 日志筛选项可见性：根据角色显示不同筛选（演示）
      const show = (id, visible) => { const el = document.getElementById(id); if (el) el.parentElement.style.display = visible ? '' : 'none'; };
      if (role === 'admin') {
        show('log-level', true); show('source-cluster', true); show('source-node', true);
        show('op-type', true); show('user-id', true); show('time-range', true);
      } else if (role === 'operator') {
        show('log-level', true); show('source-cluster', true); show('source-node', true);
        show('op-type', true); show('user-id', false); show('time-range', true);
      } else if (role === 'observer' || role === 'user') {
        // 去掉用户ID筛选项
        show('log-level', true); show('source-cluster', true); show('source-node', true);
        show('op-type', true); show('user-id', false); show('time-range', true);
      }

      // 观察者删除故障诊断页面入口（仅隐藏导航项）
      const diagNav = document.querySelector('.header__nav a[data-page="diagnosis"]');
      if (diagNav) {
        diagNav.style.display = (role === 'observer') ? 'none' : '';
      }
    }

    // 登录/注册页与用户菜单显示切换
    toggleAuthUI() {
      const isAuthed = this.isAuthenticated();
      const userMenu = document.querySelector('.header__user-menu');
      const headerNav = document.querySelector('.header__nav');
      const headerSearch = document.querySelector('.header__search');
      if (userMenu) userMenu.style.display = isAuthed ? '' : 'none';
      if (headerNav) headerNav.style.display = isAuthed ? '' : 'none';
      if (headerSearch) headerSearch.style.display = isAuthed ? '' : 'none';
    }

    // 绑定表单与按钮事件
    bindForms() {
      // 登录
      const loginForm = document.getElementById('login-form');
      const goRegister = document.getElementById('go-register');
      if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const username = document.getElementById('login-account')?.value.trim();
          const password = document.getElementById('login-password')?.value.trim();
          const res = this.login(username, password);
          const msgBox = this.ensureMsgBox('login');
          if (res.ok) {
            msgBox.textContent = `登录成功，角色：${res.role}`;
            this.toggleAuthUI();
            const target = this.getDefaultPage();
            window.location.hash = `#${target}`;
            window.navigationManager?.switchPage(target);
          } else {
            msgBox.textContent = res.message || '登录失败';
          }
        });
      }
      if (goRegister) {
        goRegister.addEventListener('click', () => {
          window.location.hash = '#register';
          window.navigationManager?.switchPage('register');
        });
      }

      // 注册
      const regForm = document.getElementById('register-form');
      if (regForm) {
        regForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const payload = {
            username: document.getElementById('reg-username')?.value.trim(),
            password: document.getElementById('reg-password')?.value.trim(),
            confirm: document.getElementById('reg-password-confirm')?.value.trim(),
            contact: document.getElementById('reg-contact')?.value.trim(),
            role: document.getElementById('reg-role')?.value,
          };
          const res = this.register(payload);
          const msgBox = this.ensureMsgBox('register');
          if (res.ok) {
            msgBox.textContent = '提交成功，已进入审批队列';
            window.location.hash = '#login';
            window.navigationManager?.switchPage('login');
          } else {
            msgBox.textContent = res.message || '提交失败';
          }
        });
      }
    }

    renderProfile() {
      const role = this.getRole();
      const usernameMap = { admin: 'admin', operator: 'ops', observer: 'obs' };
      const emailMap = { admin: 'admin@example.com', operator: 'ops@example.com', observer: 'obs@example.com' };
      const roleNameMap = { admin: '管理员', operator: '操作员', observer: '观察员' };
      const u = usernameMap[role] || '-';
      const e = emailMap[role] || '-';
      const r = roleNameMap[role] || '-';
      const unEl = document.getElementById('profile-username');
      const emEl = document.getElementById('profile-email');
      const rlEl = document.getElementById('profile-role');
      if (unEl) unEl.textContent = u;
      if (emEl) emEl.textContent = e;
      if (rlEl) rlEl.textContent = r;
    }

    ensureMsgBox(pageId) {
      const section = document.getElementById(pageId);
      if (!section) return { textContent: '' };
      let box = section.querySelector('.auth-msg');
      if (!box) {
        box = document.createElement('div');
        box.className = 'auth-msg u-mt-2 u-text-sm u-text-gray-700';
        section.appendChild(box);
      }
      return box;
    }

    // 渲染审批队列（管理员页）
    renderApprovalQueue() {
      const tbody = document.getElementById('admin-approval-tbody');
      if (!tbody) return;
      tbody.innerHTML = '';
      this.approvalQueue.forEach((item, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'dashboard__table-row';
        tr.innerHTML = `
          <td class="dashboard__table-td">${item.username}</td>
          <td class="dashboard__table-td">${item.role}</td>
          <td class="dashboard__table-td">${item.contact}</td>
          <td class="dashboard__table-td">
            <button class="btn u-text-sm" data-action="approve" data-idx="${idx}" data-requires-edit="true">通过</button>
            <button class="btn u-text-sm u-ml-2" data-action="reject" data-idx="${idx}" data-requires-edit="true">拒绝</button>
          </td>`;
        tbody.appendChild(tr);
      });

      // 绑定审批按钮事件（委托）
      const table = document.getElementById('admin-approval-table');
      if (table && !table.__binded) {
        table.__binded = true;
        table.addEventListener('click', (e) => {
          const btn = e.target.closest('button[data-action]');
          if (!btn) return;
          const action = btn.getAttribute('data-action');
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          const item = this.approvalQueue[idx];
          if (!item) return;
          if (action === 'approve') {
            item.status = 'approved';
            this.approvalQueue.splice(idx, 1);
            this.renderApprovalQueue();
          } else if (action === 'reject') {
            item.status = 'rejected';
            this.approvalQueue.splice(idx, 1);
            this.renderApprovalQueue();
          }
        });
      }
    }

    bootstrapApprovals() {
      if (!Array.isArray(this.approvalQueue)) this.approvalQueue = [];
      if (this.approvalQueue.length === 0) {
        this.approvalQueue = [
          { username: 'new-ops', role: 'operator', contact: 'ops.candidate@example.com', status: 'pending' },
          { username: 'new-obs', role: 'observer', contact: 'obs.candidate@example.com', status: 'pending' },
          { username: 'new-admin', role: 'admin', contact: 'admin.candidate@example.com', status: 'pending' }
        ];
        this.renderApprovalQueue();
      }
    }

    bootstrapUsers() {
      if (!Array.isArray(this.users) || this.users.length === 0) {
        this.users = [
          { username: 'alice', email: 'alice@example.com', role: 'admin', status: 'enabled' },
          { username: 'bob', email: 'bob@example.com', role: 'observer', status: 'pending' }
        ];
        this.persist();
      }
    }

    renderUsersList() {
      const table = document.getElementById('admin-user-table');
      if (!table) return;
      const tbody = table.querySelector('tbody');
      if (!tbody) return;
      tbody.innerHTML = '';
      (this.users || []).forEach(u => {
        const tr = document.createElement('tr');
        tr.className = 'dashboard__table-row';
        tr.innerHTML = `
          <td class="dashboard__table-td">${u.username}</td>
          <td class="dashboard__table-td">${u.email}</td>
          <td class="dashboard__table-td">${this.roleName(u.role)}</td>
          <td class="dashboard__table-td">${this.statusBadge(u.status)}</td>
          <td class="dashboard__table-td">
            <button class="btn u-text-sm" data-action="ban" data-username="${u.username}" data-requires-edit="true">封禁</button>
            <button class="btn u-text-sm u-ml-2" data-action="unban" data-username="${u.username}" data-requires-edit="true">解禁</button>
            <button class="btn u-text-sm u-ml-2" data-action="delete" data-username="${u.username}" data-requires-edit="true">删除</button>
          </td>`;
        tbody.appendChild(tr);
      });
    }

    roleName(r) {
      if (r === 'admin') return '管理员';
      if (r === 'operator') return '操作员';
      if (r === 'observer') return '观察员';
      return r || '';
    }

    statusBadge(s) {
      if (s === 'enabled') return '<span class="u-text-success">启用</span>';
      if (s === 'pending') return '<span class="u-text-warning">待审核</span>';
      if (s === 'disabled') return '<span class="u-text-error">禁用</span>';
      return s || '';
    }

    initUserManagement() {
      this.renderUsersList();
      const addBtn = document.getElementById('admin-add-user');
      const modal = document.getElementById('admin-add-user-modal');
      const form = document.getElementById('admin-add-user-form');
      const cancel = document.getElementById('admin-add-user-cancel');
      const err = document.getElementById('admin-add-user-error');
      const userTable = document.getElementById('admin-user-table');
      if (modal && userTable) {
        const userArticle = userTable.closest('article');
        const parent = userArticle?.parentElement;
        if (parent && userArticle) {
          parent.insertBefore(modal, userArticle);
        }
      }
      if (addBtn && modal) {
        addBtn.addEventListener('click', () => {
          modal.style.display = '';
        });
      }
      if (cancel && modal) {
        cancel.addEventListener('click', () => {
          modal.style.display = 'none';
          if (err) { err.style.display = 'none'; err.textContent = ''; }
          form?.reset();
        });
      }
      if (form) {
        form.addEventListener('submit', (e) => {
          e.preventDefault();
          const username = document.getElementById('new-user-username')?.value.trim();
          const email = document.getElementById('new-user-email')?.value.trim();
          const role = document.getElementById('new-user-role')?.value;
          const status = document.getElementById('new-user-status')?.value;
          if (!username || !email || !role || !status) {
            if (err) { err.style.display = ''; err.textContent = '请填写完整信息'; }
            return;
          }
          if ((this.users || []).some(u => u.username === username)) {
            if (err) { err.style.display = ''; err.textContent = '用户名已存在'; }
            return;
          }
          this.users.push({ username, email, role, status });
          this.persist();
          this.renderUsersList();
          modal.style.display = 'none';
          if (err) { err.style.display = 'none'; err.textContent = ''; }
          form.reset();
        });
      }
      if (userTable && !userTable.__binded) {
        userTable.__binded = true;
        userTable.addEventListener('click', (e) => {
          const btn = e.target.closest('button[data-action]');
          if (!btn) return;
          const action = btn.getAttribute('data-action');
          const username = btn.getAttribute('data-username');
          const idx = (this.users || []).findIndex(u => u.username === username);
          if (idx === -1) return;
          if (action === 'ban') {
            this.showConfirm(`确认封禁用户 ${username} ?`, () => {
              this.users[idx].status = 'disabled';
              this.persist();
              this.renderUsersList();
            });
          } else if (action === 'unban') {
            this.showConfirm(`确认解禁用户 ${username} ?`, () => {
              this.users[idx].status = 'enabled';
              this.persist();
              this.renderUsersList();
            });
          } else if (action === 'delete') {
            this.showConfirm(`确认删除用户 ${username} ?`, () => {
              this.users.splice(idx, 1);
              this.persist();
              this.renderUsersList();
            });
          }
        });
      }
    }

    bindConfirmModal() {
      const modal = document.getElementById('confirm-modal');
      const msg = document.getElementById('confirm-modal-message');
      const ok = document.getElementById('confirm-modal-ok');
      const cancel = document.getElementById('confirm-modal-cancel');
      if (!modal || !msg || !ok || !cancel) return;
      cancel.addEventListener('click', () => {
        modal.style.display = 'none';
        this._confirmCb = null;
      });
      ok.addEventListener('click', () => {
        const cb = this._confirmCb;
        modal.style.display = 'none';
        this._confirmCb = null;
        if (typeof cb === 'function') cb();
      });
    }

    showConfirm(message, onOk) {
      const modal = document.getElementById('confirm-modal');
      const msg = document.getElementById('confirm-modal-message');
      if (!modal || !msg) return;
      msg.textContent = message || '';
      this._confirmCb = onOk;
      modal.style.display = '';
    }
  }

  window.authManager = new AuthManager();
})();
