<template>
  <section class="layout__section" aria-labelledby="audit-logs-title">
    <header class="layout__page-header">
      <div>
        <h2 id="audit-logs-title" class="layout__page-title">审计日志（原型）</h2>
        <p class="layout__page-subtitle">记录用户操作与系统事件</p>
      </div>
      <div class="layout__page-actions">
        <button class="btn btn--primary" disabled title="功能待实现">导出审计日志</button>
      </div>
    </header>

    <article class="layout__card">
      <div class="layout__card-header"><h3 class="layout__card-title">近期审计事件（占位数据）</h3></div>
      <div class="layout__card-body u-p-0">
        <div class="u-overflow-x-auto">
          <table class="dashboard__table">
            <thead class="dashboard__table-head">
              <tr>
                <th class="dashboard__table-th" scope="col">时间</th>
                <th class="dashboard__table-th" scope="col">用户</th>
                <th class="dashboard__table-th" scope="col">动作</th>
                <th class="dashboard__table-th" scope="col">详情</th>
              </tr>
            </thead>
            <tbody>
              <tr class="dashboard__table-row">
                <td class="dashboard__table-td"><time datetime="2023-10-15T14:31:00">14:31:00</time></td>
                <td class="dashboard__table-td">alice</td>
                <td class="dashboard__table-td">登录</td>
                <td class="dashboard__table-td">成功登录系统</td>
              </tr>
              <tr class="dashboard__table-row">
                <td class="dashboard__table-td"><time datetime="2023-10-15T14:29:00">14:29:00</time></td>
                <td class="dashboard__table-td">bob</td>
                <td class="dashboard__table-td">修改配置</td>
                <td class="dashboard__table-td">更新日志级别为 WARN</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </article>
  </section>
</template>
