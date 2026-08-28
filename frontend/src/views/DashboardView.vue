<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, LayoutDashboard } from 'lucide-vue-next'
import InternalDashboard from '../components/dashboards/InternalDashboard.vue'
import PatientDashboard from '../components/dashboards/PatientDashboard.vue'
import SpecialistDashboard from '../components/dashboards/SpecialistDashboard.vue'
import { useSessionStore } from '../stores/session'

const session = useSessionStore()
const router = useRouter()
const loading = ref(!session.profile)
const error = ref('')

const roleComponent = computed(() => ({
  PACIENTE: PatientDashboard,
  ESPECIALISTA: SpecialistDashboard,
  INTERNO: InternalDashboard,
}[session.role]))

onMounted(async () => {
  if (!session.profile) {
    try {
      await session.loadProfile()
    } catch (requestError) {
      session.logout()
      router.replace('/entrar')
      return
    } finally {
      loading.value = false
    }
  }
  if (!roleComponent.value) error.value = 'Este usuário não possui um perfil de acesso configurado.'
})
</script>

<template>
  <main class="dashboard-page section-pad">
    <div v-if="loading" class="dashboard-loading"><LayoutDashboard :size="28" /><span>Preparando seu painel…</span></div>
    <div v-else-if="error" class="empty-state large"><AlertTriangle :size="36" /><strong>Acesso não configurado</strong><span>{{ error }}</span></div>
    <component :is="roleComponent" v-else />
  </main>
</template>
