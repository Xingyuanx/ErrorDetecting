import { test, expect } from "@playwright/test";

function seedAuth(storage: { role?: "admin" | "operator" | "observer" } = {}) {
  const role = storage.role ?? "admin";
  return (window: Window) => {
    window.localStorage.setItem(
      "cm_user",
      JSON.stringify({ id: 1, username: "e2e", role })
    );
    window.localStorage.setItem("cm_token", "e2e-token");
  };
}

test("未登录访问 diagnosis 会跳转到 login", async ({ page }) => {
  await page.goto("/#/diagnosis");
  await expect(page).toHaveURL(/#\/login/);
  await expect(page.getByText("登录", { exact: false })).toBeVisible();
});

test("已登录可打开 diagnosis 并完成一次聊天流式渲染", async ({ page }) => {
  await page.addInitScript(seedAuth({ role: "admin" }));

  await page.route("**/api/v1/ai/history**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [] }),
    });
  });

  await page.route("**/api/v1/clusters**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        clusters: [{ id: "c1", uuid: "c1", name: "cluster-1" }],
      }),
    });
  });

  await page.route("**/api/v1/nodes**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        nodes: [{ name: "node-1", status: "running" }],
      }),
    });
  });

  await page.route("**/api/v1/diagnosis/logs**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ logs: [] }),
    });
  });

  await page.route("**/api/v1/ai/chat**", async (route) => {
    const body =
      'data: {"content":"OK-1"}\n' + 'data: {"content":"OK-2"}\n' + "data: [DONE]\n";
    await route.fulfill({
      status: 200,
      headers: { "content-type": "text/event-stream" },
      body,
    });
  });

  await page.goto("/#/diagnosis");

  await expect(page.getByText("诊断助手")).toBeVisible();
  await page.getByPlaceholder("支持Markdown输入... Enter 发送").fill("hello");
  await page.getByRole("button", { name: "发送" }).click();

  await expect(page.getByText("OK-1")).toBeVisible();
  await expect(page.getByText("OK-2")).toBeVisible();
});

