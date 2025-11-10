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
      this.restore();
      this.bindForms();
    }

    // 状态持久化
    restore() {
      try {
        const raw = localStorage.getItem('cm_user');
        if (raw) this.user = JSON.parse(raw);
      } catch (e) {}
    }
    persist() {
      if (this.user) {
        localStorage.setItem('cm_user', JSON.stringify(this.user));
      } else {
        localStorage.removeItem('cm_user');
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
      if (role === 'admin') return 'dashboard';
      if (role === 'operator') return 'node-mgmt';
      if (role === 'observer') return 'dashboard';
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
        'dashboard', 'logs', 'diagnosis', 'repair',
        'fault-center', 'exec-logs', 'flume-config', 'alert-config', 'llm-config',
        'profile', 'account', 'clusters', 'audit-logs'
      ];

      if (role === 'admin') {
        return basePages.concat(['user-management', 'role-assignment', 'permission-policy', 'node-mgmt']).includes(page);
      }
      if (role === 'operator') {
        // 操作者可见基础监控页 + 节点管理，隐藏用户管理相关
        const operatorPages = ['dashboard', 'logs', 'diagnosis', 'repair', 'fault-center', 'exec-logs', 'node-mgmt'];
        return operatorPages.includes(page);
      }
      if (role === 'observer') {
        // 观察者仅监控相关：dashboard、logs（读取）、fault-center（查看）
        const observerPages = ['dashboard', 'logs', 'fault-center'];
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

      // 侧边栏条目：仅管理员可见
      document.querySelectorAll('[data-role="admin-only"]').forEach(el => {
        el.style.display = (role === 'admin') ? '' : 'none';
      });

      // 禁用编辑操作：观察者全部禁用，操作者仅在非节点管理页禁用编辑
      const isObserver = role === 'observer';
      const isOperator = role === 'operator';
      const current = window.navigationManager?.getCurrentPage();
      document.querySelectorAll('[data-requires-edit="true"]').forEach(el => {
        if (isObserver) {
          el.setAttribute('disabled', 'true');
          el.title = '观察者不可修改配置';
        } else if (isOperator && current !== 'node-mgmt') {
          el.setAttribute('disabled', 'true');
          el.title = '操作者仅可在节点管理内执行变更';
        } else {
          el.removeAttribute('disabled');
          el.removeAttribute('title');
        }
      });
    }

    // 登录/注册页与用户菜单显示切换
    toggleAuthUI() {
      const isAuthed = this.isAuthenticated();
      const userMenu = document.querySelector('.header__user-menu');
      const headerNav = document.querySelector('.header__nav');
      if (userMenu) userMenu.style.display = isAuthed ? '' : 'none';
      if (headerNav) headerNav.style.display = isAuthed ? '' : 'none';
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
  }

  window.authManager = new AuthManager();
})();