<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, CalendarCheck, Eye, EyeOff, LockKeyhole } from 'lucide-vue-next'
import { useSessionStore } from '../stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await session.login({ username: username.value, password: password.value })
    const destination = typeof route.query.redirect === 'string' ? route.query.redirect : '/painel'
    router.push({ path: destination, query: route.query.horario ? { horario: route.query.horario } : {} })
  } catch (requestError) {
    error.value = requestError.status === 401
      ? 'Usuário ou senha inválidos. Confira os dados e tente novamente.'
      : requestError.message
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-story">
      <RouterLink to="/" class="back-link"><ArrowLeft :size="18" /> Voltar ao início</RouterLink>
      <div class="story-content">
        <span class="eyebrow eyebrow-light">Clínica Agenda</span>
        <h1>Bem-vindo de volta.</h1>
        <p>Acesse sua agenda, acompanhe consultas e mantenha seu cuidado sempre por perto.</p>
        <div class="story-feature"><CalendarCheck /><span><strong>Tudo em um só lugar</strong>Horários, consultas e gestão de atendimentos.</span></div>
      </div>
      <div class="story-shape shape-a"></div>
      <div class="story-shape shape-b"></div>
    </section>
    <section class="login-form-wrap">
      <form class="login-form" @submit.prevent="submit">
        <span class="login-icon"><LockKeyhole :size="24" /></span>
        <h2>Acesse sua conta</h2>
        <p>Use as credenciais fornecidas no seu cadastro.</p>
        <p v-if="error" class="alert alert-error">{{ error }}</p>
        <label class="field">
          <span>Usuário</span>
          <input v-model.trim="username" autocomplete="username" required placeholder="seu.usuario" />
        </label>
        <label class="field">
          <span>Senha</span>
          <span class="password-field">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" required placeholder="••••••••" />
            <button type="button" :aria-label="showPassword ? 'Ocultar senha' : 'Mostrar senha'" @click="showPassword = !showPassword">
              <EyeOff v-if="showPassword" :size="19" /><Eye v-else :size="19" />
            </button>
          </span>
        </label>
        <button class="button button-primary button-block button-lg" :disabled="session.loading" type="submit">
          {{ session.loading ? 'Entrando…' : 'Entrar na plataforma' }}
        </button>
        <small>Não possui acesso? Solicite seu cadastro à equipe interna da clínica.</small>
      </form>
    </section>
  </main>
</template>
