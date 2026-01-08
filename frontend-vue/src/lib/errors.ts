export function formatError(
  e: any,
  defaultMsg: string,
  options?: { mode?: "diagnosis" | "clusterList" }
): string {
  const mode = options?.mode || "diagnosis";
  if (mode === "clusterList") {
    if (e?.response) {
      const s = e.response.status;
      const d = e.response.data;
      let detail = "";
      if (d?.detail) {
        if (typeof d.detail === "string") detail = d.detail;
        else if (Array.isArray(d.detail?.errors)) {
          detail = d.detail.errors
            .map((x: any) => {
              let msg = x?.message || "未知错误";
              if (x?.field) msg = `[${x.field}] ${msg}`;
              return msg;
            })
            .join(", ");
        }
      }
      return detail || `请求异常 (${s})`;
    }
    return e?.message || defaultMsg;
  }

  if (e instanceof Error && !(e as any).response) {
    return e.message || "网络请求异常";
  }
  const r = e?.response;
  const s = r?.status;
  const d = r?.data;
  const detail = typeof d?.detail === "string" ? d.detail : "";
  const msgs: string[] = [];
  if (s) msgs.push(`HTTP ${s}`);
  if (detail) msgs.push(detail);
  if (!msgs.length) msgs.push(r ? defaultMsg : "网络连接异常");
  return msgs.join(" | ");
}

