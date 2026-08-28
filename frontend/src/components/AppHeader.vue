<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { CalendarDays, LogOut, UserRound } from 'lucide-vue-next'
import { useSessionStore } from '../stores/session'

const router = useRouter()
const session = useSessionStore()
const initials = computed(() => session.profile?.nome?.split(' ').slice(0, 2).map((name) => name[0]).join('') || '')

function logout() {
  session.logout()
  router.push('/')
}
</script>

<template>
  <header class="site-header">
    <RouterLink to="/" class="brand" aria-label="Clínica Agenda - início">
      <span class="brand-mark"><CalendarDays :size="21" stroke-width="2.2" /></span>
      <span>Clínica <strong>Agenda</strong></span>
    </RouterLink>

    <nav class="header-nav" aria-label="Navegação principal">
      <RouterLink to="/" class="nav-link">Início</RouterLink>
      <a href="/#especialistas" class="nav-link">Especialistas</a>
      <RouterLink v-if="!session.isAuthenticated" to="/entrar" class="button button-sm button-outline">
        <UserRound :size="17" /> Entrar
      </RouterLink>
      <template v-else>
        <RouterLink to="/painel" class="profile-chip" aria-label="Abrir painel">
          <span class="avatar">{{ initials }}</span>
          <span>{{ session.profile?.nome || 'Meu painel' }}</span>
        </RouterLink>
        <button class="icon-button" type="button" aria-label="Sair" title="Sair" @click="logout">
          <LogOut :size="19" />
        </button>
      </template>
    </nav>
  </header>
</template>
