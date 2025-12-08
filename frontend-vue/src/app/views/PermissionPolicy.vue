<template>
  <section class="layout__section" aria-labelledby="perm-policy-title">
    <header class="layout__page-header">
      <div>
        <h2 id="perm-policy-title" class="layout__page-title">权限策略（原型）</h2>
        <p class="layout__page-subtitle">配置资源访问策略与规则</p>
      </div>
      <div class="layout__page-actions">
        <button class="btn btn--primary" disabled title="功能待实现">保存策略</button>
      </div>
    </header>

    <article class="layout__card">
      <div class="layout__card-header"><h3 class="layout__card-title">策略列表（占位数据）</h3></div>
      <div class="layout__card-body u-p-0">
        <div class="u-overflow-x-auto">
          <table class="dashboard__table">
            <thead class="dashboard__table-head">
              <tr>
                <th class="dashboard__table-th" scope="col">策略名称</th>
                <th class="dashboard__table-th" scope="col">资源</th>
                <th class="dashboard__table-th" scope="col">操作</th>
                <th class="dashboard__table-th" scope="col">效果</th>
              </tr>
            </thead>
            <tbody>
              <tr class="dashboard__table-row">
                <td class="dashboard__table-td">allow-read-logs</td>
                <td class="dashboard__table-td">logs/*</td>
                <td class="dashboard__table-td">read</td>
                <td class="dashboard__table-td"><span class="u-text-success">allow</span></td>
              </tr>
              <tr class="dashboard__table-row">
                <td class="dashboard__table-td">deny-delete-nodes</td>
                <td class="dashboard__table-td">nodes/*</td>
                <td class="dashboard__table-td">delete</td>
                <td class="dashboard__table-td"><span class="u-text-error">deny</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </article>
  </section>
</template>
