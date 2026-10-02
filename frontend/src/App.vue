<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { authApi, type User } from './api'

type View = 'login' | 'register' | 'forgot' | 'reset' | 'profile'
const view = ref<View>('login')
const message = ref('')
const resetUrl = ref('')
const error = ref('')
const busy = ref(false)
const user = ref<User | null>(null)
const loginForm = reactive({ correo: '', contrasena: '' })
const registerForm = reactive({ nombre: '', apellidos: '', correo: '', direccion: '', telefono: '', contrasena: '', confirmar: '' })
const forgotForm = reactive({ correo: '' })
const resetForm = reactive({ contrasena: '', confirmar: '' })
const passwordHint = 'Mínimo 8 caracteres, con mayúscula, minúscula, número y símbolo.'
const roleLabel = computed(() => user.value?.rol.replaceAll('_', ' ') || '')

function clearNotice() { message.value = ''; error.value = ''; resetUrl.value = '' }
function setView(next: View) { clearNotice(); view.value = next }
function passwordValid(password: string) { return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$/.test(password) }
function checkPassword(password: string, confirmation: string) {
  if (!passwordValid(password)) { error.value = passwordHint; return false }
  if (password !== confirmation) { error.value = 'Las contraseñas no coinciden.'; return false }
  return true
}

async function submitLogin() {
  clearNotice(); busy.value = true
  try {
    const result = await authApi.login(loginForm.correo, loginForm.contrasena)
    localStorage.setItem('taller_token', result.access_token)
    user.value = result.user
    view.value = 'profile'
  } catch (e) { error.value = (e as Error).message } finally { busy.value = false }
}
async function submitRegister() {
  clearNotice()
  if (!checkPassword(registerForm.contrasena, registerForm.confirmar)) return
  busy.value = true
  try {
    const { confirmar, ...data } = registerForm
    const result = await authApi.register(data)
    message.value = result.message
    loginForm.correo = registerForm.correo
    registerForm.contrasena = ''; registerForm.confirmar = ''
    view.value = 'login'
  } catch (e) { error.value = (e as Error).message } finally { busy.value = false }
}
async function submitForgot() {
  clearNotice(); busy.value = true
  try {
    const result = await authApi.forgotPassword(forgotForm.correo)
    message.value = result.message
    resetUrl.value = result.reset_url || ''
  } catch (e) { error.value = (e as Error).message } finally { busy.value = false }
}
async function submitReset() {
  clearNotice()
  if (!checkPassword(resetForm.contrasena, resetForm.confirmar)) return
  const token = new URLSearchParams(window.location.search).get('reset_token')
  if (!token) { error.value = 'El enlace de recuperación no es válido.'; return }
  busy.value = true
  try {
    message.value = (await authApi.resetPassword(token, resetForm.contrasena)).message
    history.replaceState({}, '', window.location.pathname)
    view.value = 'login'
  } catch (e) { error.value = (e as Error).message } finally { busy.value = false }
}
function logout() { localStorage.removeItem('taller_token'); user.value = null; setView('login') }

onMounted(async () => {
  if (new URLSearchParams(window.location.search).has('reset_token')) { view.value = 'reset'; return }
  const token = localStorage.getItem('taller_token')
  if (!token) return
  try { user.value = await authApi.me(token); view.value = 'profile' } catch { localStorage.removeItem('taller_token') }
})
</script>

<template>
  <main class="shell">
    <section class="brand-panel">
      <div class="brand-mark">TM</div>
      <p class="eyebrow">Taller Mecánico</p>
      <h1>Tu vehículo,<br><em>siempre en buenas manos.</em></h1>
      <p class="brand-copy">Consulta cada etapa del servicio de tu vehículo desde un solo lugar.</p>
      <div class="steps"><span>01</span><i></i><span>02</span><i></i><span>03</span></div>
      <p class="steps-copy">Registro · Servicio · Seguimiento</p>
    </section>

    <section class="auth-panel">
      <div class="card" v-if="view !== 'profile'">
        <div class="heading">
          <p class="eyebrow">{{ view === 'register' ? 'Nueva cuenta' : view === 'forgot' ? 'Recuperación' : view === 'reset' ? 'Nueva contraseña' : 'Bienvenido' }}</p>
          <h2>{{ view === 'register' ? 'Crea tu acceso' : view === 'forgot' ? 'Recupera tu acceso' : view === 'reset' ? 'Elige una contraseña segura' : 'Ingresa a tu cuenta' }}</h2>
          <p v-if="view === 'forgot'">Te enviaremos las instrucciones al correo asociado a tu cuenta.</p>
        </div>
        <div v-if="message" class="notice success" role="status">{{ message }}</div>
        <a v-if="resetUrl" class="dev-reset" :href="resetUrl">Continuar con la recuperación</a>
        <div v-if="error" class="notice error" role="alert">{{ error }}</div>

        <form v-if="view === 'login'" @submit.prevent="submitLogin">
          <label>Correo electrónico<input v-model.trim="loginForm.correo" type="email" autocomplete="email" required placeholder="nombre@correo.com"></label>
          <label>Contraseña<input v-model="loginForm.contrasena" type="password" autocomplete="current-password" required placeholder="••••••••"></label>
          <button class="link" type="button" @click="setView('forgot')">¿Olvidaste tu contraseña?</button>
          <button class="primary" :disabled="busy">{{ busy ? 'Validando…' : 'Iniciar sesión' }}</button>
          <p class="switch">¿Aún no tienes cuenta? <button type="button" @click="setView('register')">Regístrate</button></p>
        </form>

        <form v-else-if="view === 'register'" @submit.prevent="submitRegister">
          <div class="two-columns"><label>Nombre<input v-model.trim="registerForm.nombre" required minlength="2"></label><label>Apellidos<input v-model.trim="registerForm.apellidos" required minlength="2"></label></div>
          <label>Correo electrónico<input v-model.trim="registerForm.correo" type="email" autocomplete="email" required></label>
          <label>Dirección<input v-model.trim="registerForm.direccion" required minlength="5"></label>
          <label>Teléfono<input v-model.trim="registerForm.telefono" type="tel" required placeholder="55 1234 5678"></label>
          <div class="two-columns"><label>Contraseña<input v-model="registerForm.contrasena" type="password" autocomplete="new-password" required></label><label>Confirmar contraseña<input v-model="registerForm.confirmar" type="password" autocomplete="new-password" required></label></div>
          <p class="hint">{{ passwordHint }}</p>
          <button class="primary" :disabled="busy">{{ busy ? 'Creando cuenta…' : 'Crear cuenta' }}</button>
          <p class="switch">¿Ya tienes cuenta? <button type="button" @click="setView('login')">Inicia sesión</button></p>
        </form>

        <form v-else-if="view === 'forgot'" @submit.prevent="submitForgot">
          <label>Correo electrónico<input v-model.trim="forgotForm.correo" type="email" autocomplete="email" required placeholder="nombre@correo.com"></label>
          <button class="primary" :disabled="busy">{{ busy ? 'Enviando…' : 'Enviar instrucciones' }}</button>
          <p class="switch"><button type="button" @click="setView('login')">Volver a iniciar sesión</button></p>
        </form>

        <form v-else @submit.prevent="submitReset">
          <label>Nueva contraseña<input v-model="resetForm.contrasena" type="password" autocomplete="new-password" required></label>
          <label>Confirmar contraseña<input v-model="resetForm.confirmar" type="password" autocomplete="new-password" required></label>
          <p class="hint">{{ passwordHint }}</p>
          <button class="primary" :disabled="busy">{{ busy ? 'Guardando…' : 'Actualizar contraseña' }}</button>
        </form>
      </div>

      <div class="card profile" v-else>
        <div class="avatar">{{ user?.nombre.slice(0, 1) }}{{ user?.apellidos.slice(0, 1) }}</div>
        <p class="eyebrow">Sesión activa</p>
        <h2>Hola, {{ user?.nombre }}</h2>
        <p>Tu cuenta está lista para consultar el estado de tus servicios.</p>
        <dl><div><dt>Correo</dt><dd>{{ user?.correo }}</dd></div><div><dt>Rol</dt><dd class="role">{{ roleLabel }}</dd></div></dl>
        <button class="primary" @click="logout">Cerrar sesión</button>
      </div>
    </section>
  </main>
</template>
