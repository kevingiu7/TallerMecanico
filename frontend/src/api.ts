const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export interface User {
  id: number
  nombre: string
  apellidos: string
  correo: string
  direccion: string
  telefono: string
  rol: string
  activo: boolean
  creado_en: string
}

interface AuthResult { access_token: string; token_type: string; user: User }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || 'No fue posible completar la solicitud')
  return data as T
}

export const authApi = {
  register: (data: Record<string, string>) => request<{ message: string }>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (correo: string, contrasena: string) => request<AuthResult>('/auth/login', { method: 'POST', body: JSON.stringify({ correo, contrasena }) }),
  forgotPassword: (correo: string) => request<{ message: string; reset_url?: string }>('/auth/forgot-password', { method: 'POST', body: JSON.stringify({ correo }) }),
  resetPassword: (token: string, contrasena: string) => request<{ message: string }>('/auth/reset-password', { method: 'POST', body: JSON.stringify({ token, contrasena }) }),
  me: (token: string) => request<User>('/auth/me', { headers: { Authorization: `Bearer ${token}` } }),
}
