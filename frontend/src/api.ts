export async function api(path: string, options: RequestInit = {}) {
  const response = await fetch('/api' + path, { ...options, headers: options.body instanceof FormData ? options.headers : { 'Content-Type': 'application/json', ...options.headers } })
  if (!response.ok) { const error = await response.json().catch(() => ({})); throw new Error(typeof error.detail === 'string' ? error.detail : '请求失败，请检查输入') }
  return response.json()
}
export const send = (method: string, body: unknown): RequestInit => ({ method, body: JSON.stringify(body) })
