<script setup>
import { computed, onMounted, ref } from 'vue'
import { CalendarClock, CalendarDays, Check, Clock3, Plus, Stethoscope, Trash2, Users, X } from 'lucide-vue-next'
import { listAll, request } from '../../services/api'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const activeTab = ref('agendas')
const agendas = ref([])
const appointments = ref([])
const showForm = ref(false)
const saving = ref(false)
const notice = ref(null)
const form = ref({ dias_semana: 0, hora_inicio_expediente: '08:00', hora_fim_expediente: '12:00', quantidade_vagas_dia: 4 })
const weekdays = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
const totalAvailable = computed(() => agendas.value.reduce((total, agenda) => total + agenda.horarios.filter((slot) => slot.status === 'DISPONIVEL').length, 0))

function shortTime(value) { return value?.slice(0, 5) }

async function load() {
  try {
    ;[agendas.value, appointments.value] = await Promise.all([
      listAll('/agendamentos/agendas/'),
      listAll('/agendamentos/consultas/'),
    ])
  } catch (error) {
    notice.value = { type: 'error', text: error.message }
  }
}

async function createAgenda() {
  saving.value = true
  notice.value = null
  try {
    await request('/agendamentos/agendas/', { method: 'POST', body: JSON.stringify({
      ...form.value,
      hora_inicio_expediente: `${form.value.hora_inicio_expediente}:00`,
      hora_fim_expediente: `${form.value.hora_fim_expediente}:00`,
    }) })
    notice.value = { type: 'success', text: 'Agenda criada e horários gerados para os próximos 30 dias.' }
    showForm.value = false
    await load()
  } catch (error) {
    notice.value = { type: 'error', text: error.message }
  } finally { saving.value = false }
}

async function removeAgenda(agenda) {
  if (!window.confirm(`Desativar a agenda de ${weekdays[agenda.dias_semana]}? Os horários disponíveis deixarão de aparecer.`)) return
  try {
    await request(`/agendamentos/agendas/${agenda.id}/`, { method: 'DELETE' })
    notice.value = { type: 'success', text: 'Agenda desativada com sucesso.' }
    await load()
  } catch (error) { notice.value = { type: 'error', text: error.message } }
}

onMounted(load)
</script>

<template>
  <div class="dashboard-content">
    <div class="dashboard-welcome specialist-welcome"><div><span class="eyebrow">Área do especialista</span><h1>Olá, Dr(a). {{ session.profile?.nome?.split(' ')[0] }}.</h1><p>Organize sua disponibilidade e acompanhe seus atendimentos.</p></div><span class="welcome-icon"><Stethoscope /></span></div>
    <div class="stats-grid">
      <article><span class="stat-icon"><CalendarClock /></span><div><strong>{{ agendas.length }}</strong><span>agendas ativas</span></div></article>
      <article><span class="stat-icon"><Clock3 /></span><div><strong>{{ totalAvailable }}</strong><span>horários disponíveis</span></div></article>
      <article><span class="stat-icon"><Users /></span><div><strong>{{ appointments.length }}</strong><span>consultas reservadas</span></div></article>
    </div>
    <div class="dashboard-tabs" role="tablist"><button :class="{ active: activeTab === 'agendas' }" @click="activeTab = 'agendas'"><CalendarDays :size="18" /> Minhas agendas</button><button :class="{ active: activeTab === 'consultas' }" @click="activeTab = 'consultas'"><Users :size="18" /> Consultas</button></div>
    <p v-if="notice" :class="['alert', notice.type === 'success' ? 'alert-success' : 'alert-error']"><Check v-if="notice.type === 'success'" :size="18" />{{ notice.text }}<button type="button" @click="notice = null"><X :size="17" /></button></p>
    <section v-if="activeTab === 'agendas'" class="dashboard-panel">
      <div class="panel-title"><div><h2>Minha disponibilidade</h2><p>Cada agenda gera automaticamente as vagas dos próximos 30 dias.</p></div><button class="button button-primary" @click="showForm = !showForm"><Plus :size="18" /> Nova agenda</button></div>
      <form v-if="showForm" class="inline-form agenda-form" @submit.prevent="createAgenda">
        <label><span>Dia da semana</span><select v-model.number="form.dias_semana"><option v-for="(day, index) in weekdays" :key="day" :value="index">{{ day }}</option></select></label>
        <label><span>Início</span><input v-model="form.hora_inicio_expediente" type="time" required /></label>
        <label><span>Fim</span><input v-model="form.hora_fim_expediente" type="time" required /></label>
        <label><span>Vagas por dia</span><input v-model.number="form.quantidade_vagas_dia" type="number" min="1" required /></label>
        <div class="form-actions"><button type="button" class="button button-ghost" @click="showForm = false">Cancelar</button><button class="button button-primary" :disabled="saving">{{ saving ? 'Criando…' : 'Criar agenda' }}</button></div>
      </form>
      <div v-if="agendas.length" class="agenda-list">
        <article v-for="agenda in agendas" :key="agenda.id" class="agenda-item">
          <span class="day-tile">{{ weekdays[agenda.dias_semana].slice(0, 3).toUpperCase() }}</span>
          <div class="agenda-main"><strong>{{ weekdays[agenda.dias_semana] }}</strong><span>{{ shortTime(agenda.hora_inicio_expediente) }} às {{ shortTime(agenda.hora_fim_expediente) }}</span></div>
          <div class="agenda-meta"><span><strong>{{ agenda.quantidade_vagas_dia }}</strong> vagas/dia</span><span><strong>{{ agenda.horarios.filter((item) => item.status === 'DISPONIVEL').length }}</strong> livres</span></div>
          <button class="icon-button danger" title="Desativar agenda" aria-label="Desativar agenda" @click="removeAgenda(agenda)"><Trash2 :size="18" /></button>
        </article>
      </div>
      <div v-else class="empty-state"><CalendarClock :size="34" /><strong>Nenhuma agenda configurada</strong><span>Crie sua primeira grade para disponibilizar horários.</span></div>
    </section>
    <section v-else class="dashboard-panel">
      <div class="panel-title"><div><h2>Consultas reservadas</h2><p>Pacientes que agendaram horários nas suas agendas.</p></div></div>
      <div v-if="appointments.length" class="table-wrap"><table><thead><tr><th>Paciente</th><th>Data e horário</th><th>Status</th></tr></thead><tbody><tr v-for="item in appointments" :key="item.id"><td><span class="table-person"><span class="avatar">{{ item.nome_paciente?.[0] }}</span><strong>{{ item.nome_paciente }}</strong></span></td><td>{{ item.data_hora }}</td><td><span class="status-pill success"><span></span> Confirmada</span></td></tr></tbody></table></div>
      <div v-else class="empty-state"><Users :size="34" /><strong>Nenhuma consulta reservada</strong><span>As reservas aparecerão aqui assim que um paciente escolher uma vaga.</span></div>
    </section>
  </div>
</template>
