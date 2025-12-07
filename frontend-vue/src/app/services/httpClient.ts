export type RequestInitEx = { method?: string; headers?: Record<string,string>; body?: any; timeout?: number; token?: string }

export async function request(url: string, init: RequestInitEx = {}) {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), init.timeout || 10000)
  const headers: Record<string,string> = { 'Content-Type': 'application/json', ...(init.headers || {}) }
  if (init.token) headers['Authorization'] = 'Bearer ' + init.token
  const res = await fetch(url, { method: init.method || 'GET', headers, body: init.body ? JSON.stringify(init.body) : undefined, signal: controller.signal })
  clearTimeout(id)
  let data: unknown = undefined
  try { data = await res.json() } catch {}
  if (!res.ok) throw { status: res.status, data }
  return data as any
}
