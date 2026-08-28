<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CalendarCheck, CalendarDays, Check, Clock3, Search, Stethoscope, X } from 'lucide-vue-next'
import { listAll, request } from '../../services/api'
import { useSessionStore } from '../../stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()
const activeTab = ref('buscar')
const specialties = ref([])
const specialists = ref([])
const slots = ref([])
const appointments = ref([])
const specialty = ref('')
const specialist = ref('')
const date = ref('')
const loading = ref(true)
const saving = ref(false)
const selectedSlot = ref(null)
const notice = ref(null)

const availableSpecialists = computed(() => specialists.value.filter((item) => (
  !specialty.value || String(item.especialidade) === specialty.value
)))
const visibleSlots = computed(() => slots.value.filter((slot) => (
  (!specialist.value || String(slot.especialista) === specialist.value)
  && (!specialty.value || availableSpecialists.value.some((item) => item.id === slot.especialista))
  && (!date.value || slot.data === date.value)
)))

function formatDate(value, long = false) {
  return new Intl.DateTimeFormat('pt-BR', long
    ? { weekday: 'long', day: '2-digit', month: 'long' }
    : { day: '2-digit', month: 'short' })
    .format(new Date(`${value}T12:00:00`))
}

function shortTime(value) { return value?.slice(0, 5) }

async function load() {
  loading.value = true
  try {
    ;[specialties.value, specialists.value, slots.value, appointments.value] = await Promise.all([
      listAll('/agendamentos/especialidades/'),
      listAll('/usuarios/especialistas/'),
      listAll('/agendamentos/horarios/?status=DISPONIVEL'),
      listAll('/agendamentos/consultas/'),
    ])
    if (route.query.horario) {
      selectedSlot.value = slots.value.find((item) => String(item.id) === String(route.query.horario)) || null
      router.replace({ query: {} })
    }
  } catch (error) {
    notice.value = { type: 'error', text: error.message }
  } finally {
    loading.value = false
  }
}

async function reserve() {
  if (!selectedSlot.value) return
  saving.value = true
  try {
    await request('/agendamentos/consultas/', {
      method: 'POST',
      body: JSON.stringify({ horario_gerado: selectedSlot.value.id }),
    })
    notice.value = { type: 'success', text: 'Consulta agendada com sucesso. Seu horário já está reservado.' }
    selectedSlot.value = null
    await load()
    activeTab.value = 'consultas'
  } catch (error) {
    notice.value = { type: 'error', text: error.message }
    selectedSlot.value = null
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="dashboard-content">
    <div class="dashboard-welcome">
      <div><span class="eyebrow">Área do paciente</span><h1>Olá, {{ session.profile?.nome?.split(' ')[0] }}.</h1><p>Cuide da sua agenda e encontre seu próximo atendimento.</p></div>
      <span class="welcome-icon"><CalendarDays /></span>
    </div>

    <div class="dashboard-tabs" role="tablist">
      <button :class="{ active: activeTab === 'buscar' }" @click="activeTab = 'buscar'"><Search :size="18" /> Buscar horários</button>
      <button :class="{ active: activeTab === 'consultas' }" @click="activeTab = 'consultas'"><CalendarCheck :size="18" /> Minhas consultas <span class="count-badge">{{ appointments.length }}</span></button>
    </div>

    <p v-if="notice" :class="['alert', notice.type === 'success' ? 'alert-success' : 'alert-error']">
      <Check v-if="notice.type === 'success'" :size="18" />{{ notice.text }}
      <button type="button" aria-label="Fechar aviso" @click="notice = null"><X :size="17" /></button>
    </p>

    <section v-if="activeTab === 'buscar'" class="dashboard-panel">
      <div class="panel-title"><div><h2>Encontre um horário</h2><p>Selecione os filtros ou explore todas as vagas disponíveis.</p></div><span class="result-count">{{ visibleSlots.length }} vaga(s)</span></div>
      <div class="filters-row dashboard-filters">
        <label><span>Especialidade</span><select v-model="specialty" @change="specialist = ''"><option value="">Todas</option><option v-for="item in specialties" :key="item.id" :value="String(item.id)">{{ item.nome_especialidade }}</option></select></label>
        <label><span>Especialista</span><select v-model="specialist"><option value="">Todos</option><option v-for="item in availableSpecialists" :key="item.id" :value="String(item.id)">{{ item.nome }}</option></select></label>
        <label><span>Data</span><input v-model="date" type="date" /></label>
      </div>
      <div v-if="loading" class="skeleton-list"><span v-for="item in 4" :key="item"></span></div>
      <div v-else-if="visibleSlots.length" class="availability-list">
        <article v-for="slot in visibleSlots" :key="slot.id" class="availability-item">
          <div class="date-tile"><strong>{{ new Date(`${slot.data}T12:00:00`).getDate() }}</strong><span>{{ formatDate(slot.data).split(' ')[1] }}</span></div>
          <div class="availability-doctor"><span class="avatar"><Stethoscope :size="19" /></span><div><strong>Dr(a). {{ slot.nome_especialista }}</strong><span>{{ slot.especialidade }}</span></div></div>
          <div class="availability-time"><Clock3 :size="17" /><strong>{{ shortTime(slot.horario_inicio) }}</strong><span>até {{ shortTime(slot.horario_fim) }}</span></div>
          <button class="button button-primary button-sm" @click="selectedSlot = slot">Agendar</button>
        </article>
      </div>
      <div v-else class="empty-state"><CalendarDays :size="32" /><strong>Não há vagas com estes filtros</strong><span>Altere a data ou escolha outra especialidade.</span></div>
    </section>

    <section v-else class="dashboard-panel">
      <div class="panel-title"><div><h2>Minhas consultas</h2><p>Acompanhe todos os atendimentos vinculados à sua conta.</p></div></div>
      <div v-if="appointments.length" class="appointment-grid">
        <article v-for="appointment in appointments" :key="appointment.id" class="appointment-card">
          <div class="appointment-card-head"><span class="status-pill success"><span></span> Confirmada</span><small>#{{ appointment.id }}</small></div>
          <span class="appointment-icon"><Stethoscope /></span>
          <h3>Dr(a). {{ appointment.nome_especialista }}</h3>
          <p>{{ appointment.especialidade }}</p>
          <div class="appointment-info"><CalendarDays :size="18" /><span>{{ appointment.data_hora }}</span></div>
        </article>
      </div>
      <div v-else class="empty-state"><CalendarCheck :size="34" /><strong>Você ainda não possui consultas</strong><span>Encontre um horário disponível para fazer seu primeiro agendamento.</span><button class="button button-primary" @click="activeTab = 'buscar'">Buscar horário</button></div>
    </section>

    <div v-if="selectedSlot" class="modal-backdrop" @click.self="selectedSlot = null">
      <section class="modal-card" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
        <button class="modal-close" type="button" aria-label="Fechar" @click="selectedSlot = null"><X /></button>
        <span class="modal-icon"><CalendarCheck /></span>
        <span class="eyebrow">Confirmar agendamento</span>
        <h2 id="confirm-title">Este horário funciona para você?</h2>
        <div class="confirm-summary">
          <strong>Dr(a). {{ selectedSlot.nome_especialista }}</strong><span>{{ selectedSlot.especialidade }}</span>
          <hr />
          <p><CalendarDays :size="18" /> {{ formatDate(selectedSlot.data, true) }}</p>
          <p><Clock3 :size="18" /> {{ shortTime(selectedSlot.horario_inicio) }} às {{ shortTime(selectedSlot.horario_fim) }}</p>
        </div>
        <button class="button button-primary button-block button-lg" :disabled="saving" @click="reserve">{{ saving ? 'Reservando…' : 'Confirmar consulta' }}</button>
        <button class="button button-ghost button-block" @click="selectedSlot = null">Escolher outro horário</button>
      </section>
    </div>
  </div>
</template>
