// 通用组件库

// 模态框组件
class Modal {
    constructor(options = {}) {
        this.options = {
            title: '提示',
            content: '',
            width: '500px',
            height: 'auto',
            closable: true,
            maskClosable: true,
            showFooter: true,
            confirmText: '确定',
            cancelText: '取消',
            onConfirm: null,
            onCancel: null,
            onClose: null,
            ...options
        };
        
        this.element = null;
        this.isVisible = false;
        this.create();
    }

    create() {
        this.element = document.createElement('div');
        this.element.className = 'modal-overlay';
        this.element.innerHTML = `
            <div class="modal-container" style="width: ${this.options.width}; height: ${this.options.height};">
                <div class="modal-header">
                    <h3 class="modal-title">${this.options.title}</h3>
                    ${this.options.closable ? '<button class="modal-close"><i class="icon-x"></i></button>' : ''}
                </div>
                <div class="modal-body">
                    ${this.options.content}
                </div>
                ${this.options.showFooter ? `
                    <div class="modal-footer">
                        <button class="btn btn-secondary modal-cancel">${this.options.cancelText}</button>
                        <button class="btn btn-primary modal-confirm">${this.options.confirmText}</button>
                    </div>
                ` : ''}
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        // 关闭按钮
        const closeBtn = this.element.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // 遮罩点击关闭
        if (this.options.maskClosable) {
            this.element.addEventListener('click', (e) => {
                if (e.target === this.element) {
                    this.close();
                }
            });
        }

        // 确定按钮
        const confirmBtn = this.element.querySelector('.modal-confirm');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                if (this.options.onConfirm) {
                    const result = this.options.onConfirm();
                    if (result !== false) {
                        this.close();
                    }
                } else {
                    this.close();
                }
            });
        }

        // 取消按钮
        const cancelBtn = this.element.querySelector('.modal-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                if (this.options.onCancel) {
                    this.options.onCancel();
                }
                this.close();
            });
        }

        // ESC键关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isVisible) {
                this.close();
            }
        });
    }

    show() {
        if (!this.isVisible) {
            document.body.appendChild(this.element);
            this.isVisible = true;
            
            // 添加动画
            setTimeout(() => {
                this.element.classList.add('show');
            }, 10);
        }
        return this;
    }

    close() {
        if (this.isVisible) {
            this.element.classList.remove('show');
            
            setTimeout(() => {
                if (this.element.parentElement) {
                    document.body.removeChild(this.element);
                }
                this.isVisible = false;
                
                if (this.options.onClose) {
                    this.options.onClose();
                }
            }, 300);
        }
        return this;
    }

    setContent(content) {
        const body = this.element.querySelector('.modal-body');
        if (body) {
            body.innerHTML = content;
        }
        return this;
    }

    setTitle(title) {
        const titleElement = this.element.querySelector('.modal-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
        return this;
    }
}

// 加载组件
class Loading {
    constructor(container = document.body, options = {}) {
        this.container = container;
        this.options = {
            text: '加载中...',
            size: 'medium',
            overlay: true,
            ...options
        };
        
        this.element = null;
        this.isVisible = false;
        this.create();
    }

    create() {
        this.element = document.createElement('div');
        this.element.className = `loading-container ${this.options.size}`;
        
        if (this.options.overlay) {
            this.element.classList.add('loading-overlay');
        }

        this.element.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                </div>
                ${this.options.text ? `<div class="loading-text">${this.options.text}</div>` : ''}
            </div>
        `;
    }

    show() {
        if (!this.isVisible) {
            this.container.appendChild(this.element);
            this.isVisible = true;
            
            setTimeout(() => {
                this.element.classList.add('show');
            }, 10);
        }
        return this;
    }

    hide() {
        if (this.isVisible) {
            this.element.classList.remove('show');
            
            setTimeout(() => {
                if (this.element.parentElement) {
                    this.container.removeChild(this.element);
                }
                this.isVisible = false;
            }, 300);
        }
        return this;
    }

    setText(text) {
        const textElement = this.element.querySelector('.loading-text');
        if (textElement) {
            textElement.textContent = text;
        }
        return this;
    }
}

// 通知组件
class Notification {
    static container = null;
    static notifications = [];

    static init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        }
    }

    static show(message, type = 'info', options = {}) {
        this.init();

        const config = {
            duration: 3000,
            closable: true,
            ...options
        };

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const id = Utils.generateId();
        notification.setAttribute('data-id', id);

        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon icon-${this.getIcon(type)}"></i>
                <span class="notification-message">${message}</span>
                ${config.closable ? '<button class="notification-close"><i class="icon-x"></i></button>' : ''}
            </div>
        `;

        // 绑定关闭事件
        if (config.closable) {
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => {
                this.remove(id);
            });
        }

        this.container.appendChild(notification);
        this.notifications.push({ id, element: notification });

        // 添加显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // 自动移除
        if (config.duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, config.duration);
        }

        return id;
    }

    static remove(id) {
        const index = this.notifications.findIndex(n => n.id === id);
        if (index !== -1) {
            const notification = this.notifications[index];
            notification.element.classList.remove('show');
            
            setTimeout(() => {
                if (notification.element.parentElement) {
                    this.container.removeChild(notification.element);
                }
                this.notifications.splice(index, 1);
            }, 300);
        }
    }

    static getIcon(type) {
        const icons = {
            success: 'check',
            error: 'x',
            warning: 'warning',
            info: 'info'
        };
        return icons[type] || 'info';
    }

    static success(message, options) {
        return this.show(message, 'success', options);
    }

    static error(message, options) {
        return this.show(message, 'error', options);
    }

    static warning(message, options) {
        return this.show(message, 'warning', options);
    }

    static info(message, options) {
        return this.show(message, 'info', options);
    }
}

// 确认对话框
class Confirm {
    static show(message, options = {}) {
        return new Promise((resolve) => {
            const config = {
                title: '确认',
                confirmText: '确定',
                cancelText: '取消',
                type: 'warning',
                ...options
            };

            const modal = new Modal({
                title: config.title,
                content: `
                    <div class="confirm-content">
                        <i class="confirm-icon icon-${config.type}"></i>
                        <div class="confirm-message">${message}</div>
                    </div>
                `,
                confirmText: config.confirmText,
                cancelText: config.cancelText,
                onConfirm: () => {
                    resolve(true);
                },
                onCancel: () => {
                    resolve(false);
                },
                onClose: () => {
                    resolve(false);
                }
            });

            modal.show();
        });
    }
}

// 提示框
class Alert {
    static show(message, type = 'info', options = {}) {
        return new Promise((resolve) => {
            const config = {
                title: '提示',
                confirmText: '确定',
                ...options
            };

            const modal = new Modal({
                title: config.title,
                content: `
                    <div class="alert-content">
                        <i class="alert-icon icon-${type}"></i>
                        <div class="alert-message">${message}</div>
                    </div>
                `,
                showFooter: true,
                confirmText: config.confirmText,
                cancelText: '',
                onConfirm: () => {
                    resolve(true);
                },
                onClose: () => {
                    resolve(true);
                }
            });

            // 隐藏取消按钮
            modal.show();
            const cancelBtn = modal.element.querySelector('.modal-cancel');
            if (cancelBtn) {
                cancelBtn.style.display = 'none';
            }
        });
    }

    static success(message, options) {
        return this.show(message, 'success', options);
    }

    static error(message, options) {
        return this.show(message, 'error', options);
    }

    static warning(message, options) {
        return this.show(message, 'warning', options);
    }

    static info(message, options) {
        return this.show(message, 'info', options);
    }
}

// 工具提示组件
class Tooltip {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            content: '',
            placement: 'top',
            trigger: 'hover',
            delay: 100,
            ...options
        };
        
        this.tooltip = null;
        this.isVisible = false;
        this.init();
    }

    init() {
        this.create();
        this.bindEvents();
    }

    create() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = `tooltip tooltip-${this.options.placement}`;
        this.tooltip.innerHTML = `
            <div class="tooltip-content">${this.options.content}</div>
            <div class="tooltip-arrow"></div>
        `;
        document.body.appendChild(this.tooltip);
    }

    bindEvents() {
        if (this.options.trigger === 'hover') {
            this.element.addEventListener('mouseenter', () => {
                this.showDelay();
            });
            
            this.element.addEventListener('mouseleave', () => {
                this.hide();
            });
        } else if (this.options.trigger === 'click') {
            this.element.addEventListener('click', () => {
                this.toggle();
            });
        }
    }

    showDelay() {
        setTimeout(() => {
            this.show();
        }, this.options.delay);
    }

    show() {
        if (!this.isVisible) {
            this.updatePosition();
            this.tooltip.classList.add('show');
            this.isVisible = true;
        }
    }

    hide() {
        if (this.isVisible) {
            this.tooltip.classList.remove('show');
            this.isVisible = false;
        }
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    updatePosition() {
        const rect = this.element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch (this.options.placement) {
            case 'top':
                top = rect.top - tooltipRect.height - 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 8;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 8;
                break;
        }

        this.tooltip.style.top = `${top}px`;
        this.tooltip.style.left = `${left}px`;
    }

    setContent(content) {
        const contentElement = this.tooltip.querySelector('.tooltip-content');
        if (contentElement) {
            contentElement.innerHTML = content;
        }
    }

    destroy() {
        if (this.tooltip && this.tooltip.parentElement) {
            document.body.removeChild(this.tooltip);
        }
    }
}

// 下拉菜单组件
class Dropdown {
    constructor(trigger, options = {}) {
        this.trigger = trigger;
        this.options = {
            items: [],
            placement: 'bottom-start',
            trigger: 'click',
            ...options
        };
        
        this.dropdown = null;
        this.isVisible = false;
        this.init();
    }

    init() {
        this.create();
        this.bindEvents();
    }

    create() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'dropdown-menu';
        
        const itemsHtml = this.options.items.map(item => {
            if (item.divider) {
                return '<div class="dropdown-divider"></div>';
            }
            
            return `
                <div class="dropdown-item ${item.disabled ? 'disabled' : ''}" data-value="${item.value || ''}">
                    ${item.icon ? `<i class="dropdown-icon ${item.icon}"></i>` : ''}
                    <span class="dropdown-text">${item.text}</span>
                </div>
            `;
        }).join('');
        
        this.dropdown.innerHTML = itemsHtml;
        document.body.appendChild(this.dropdown);
    }

    bindEvents() {
        // 触发器事件
        if (this.options.trigger === 'click') {
            this.trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggle();
            });
        } else if (this.options.trigger === 'hover') {
            this.trigger.addEventListener('mouseenter', () => {
                this.show();
            });
            
            this.trigger.addEventListener('mouseleave', () => {
                setTimeout(() => {
                    if (!this.dropdown.matches(':hover')) {
                        this.hide();
                    }
                }, 100);
            });
            
            this.dropdown.addEventListener('mouseleave', () => {
                this.hide();
            });
        }

        // 点击菜单项
        this.dropdown.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item && !item.classList.contains('disabled')) {
                const value = item.getAttribute('data-value');
                if (this.options.onSelect) {
                    this.options.onSelect(value, item);
                }
                this.hide();
            }
        });

        // 点击外部关闭
        document.addEventListener('click', (e) => {
            if (!this.trigger.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hide();
            }
        });
    }

    show() {
        if (!this.isVisible) {
            this.updatePosition();
            this.dropdown.classList.add('show');
            this.isVisible = true;
        }
    }

    hide() {
        if (this.isVisible) {
            this.dropdown.classList.remove('show');
            this.isVisible = false;
        }
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    updatePosition() {
        const rect = this.trigger.getBoundingClientRect();
        
        let top, left;
        
        switch (this.options.placement) {
            case 'bottom-start':
                top = rect.bottom + 4;
                left = rect.left;
                break;
            case 'bottom-end':
                top = rect.bottom + 4;
                left = rect.right - this.dropdown.offsetWidth;
                break;
            case 'top-start':
                top = rect.top - this.dropdown.offsetHeight - 4;
                left = rect.left;
                break;
            case 'top-end':
                top = rect.top - this.dropdown.offsetHeight - 4;
                left = rect.right - this.dropdown.offsetWidth;
                break;
        }

        this.dropdown.style.top = `${top}px`;
        this.dropdown.style.left = `${left}px`;
    }

    destroy() {
        if (this.dropdown && this.dropdown.parentElement) {
            document.body.removeChild(this.dropdown);
        }
    }
}

// 导出组件
window.Modal = Modal;
window.Loading = Loading;
window.Notification = Notification;
window.Confirm = Confirm;
window.Alert = Alert;
window.Tooltip = Tooltip;
window.Dropdown = Dropdown;