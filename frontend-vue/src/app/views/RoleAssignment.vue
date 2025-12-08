<template>
  <section class="layout__section" aria-labelledby="role-assign-title">
    <header class="layout__page-header">
      <div>
        <h2 id="role-assign-title" class="layout__page-title">角色分配（原型）</h2>
        <p class="layout__page-subtitle">为用户分配系统角色与权限范围</p>
      </div>
      <div class="layout__page-actions">
        <button class="btn btn--primary" disabled title="功能待实现">保存分配</button>
      </div>
    </header>

    <article class="layout__card">
      <div class="layout__card-header">
        <h3 class="layout__card-title">用户角色（占位数据）</h3>
      </div>
      <div class="layout__card-body">
        <div class="layout__grid layout__grid--2">
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">选择用户</label>
            <select class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option>alice</option>
              <option>bob</option>
              <option>charlie</option>
            </select>
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">选择角色</label>
            <select class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option>管理员</option>
              <option>操作员</option>
              <option>观察员</option>
            </select>
          </div>
        </div>
      </div>
    </article>
  </section>
</template>
