import { test, expect } from "@playwright/test";

test("dev server 返回 index.html", async ({ request }) => {
  const res = await request.get("/");
  expect(res.status()).toBe(200);
  const html = await res.text();
  expect(html).toContain('id="app"');
});

