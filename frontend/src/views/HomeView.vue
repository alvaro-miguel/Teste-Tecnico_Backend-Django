<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  CalendarCheck,
  CheckCircle2,
  Clock3,
  HeartPulse,
  Search,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  UserRoundCheck,
} from 'lucide-vue-next'
import { listAll } from '../services/api'
import { useSessionStore } from '../stores/session'

const router = useRouter()
const session = useSessionStore()
const specialists = ref([])
const specialties = ref([])
const slots = ref([])
const selectedSpecialty = ref('')
const selectedSpecialist = ref('')
const selectedDate = ref('')
const loading = ref(true)
const error = ref('')

const filteredSpecialists = computed(() => specialists.value.filter((item) => (
  !selectedSpecialty.value || String(item.especialidade) === selectedSpecialty.value
)))

const filteredSlots = computed(() => slots.value.filter((slot) => {
  const specialistMatches = !selectedSpecialist.value || String(slot.especialista) === selectedSpecialist.value
  const dateMatches = !selectedDate.value || slot.data === selectedDate.value
  const specialtyMatches = !selectedSpecialty.value || filteredSpecialists.value.some((item) => item.id === slot.especialista)
  return specialistMatches && dateMatches && specialtyMatches
}).slice(0, 8))

function formatDate(value) {
  return new Intl.DateTimeFormat('pt-BR', { weekday: 'short', day: '2-digit', month: 'short' })
    .format(new Date(`${value}T12:00:00`))
    .replace('.', '')
}

function shortTime(value) {
  return value?.slice(0, 5)
}

function chooseSpecialty(id) {
  selectedSpecialty.value = String(id)
  selectedSpecialist.value = ''
  document.querySelector('#horarios')?.scrollIntoView({ behavior: 'smooth' })
}

function book(slot) {
  const query = { horario: slot.id }
  if (session.isAuthenticated) router.push({ name: 'dashboard', query })
  else router.push({ name: 'login', query: { ...query, redirect: '/painel' } })
}

onMounted(async () => {
  try {
    ;[specialists.value, specialties.value, slots.value] = await Promise.all([
      listAll('/usuarios/especialistas/'),
      listAll('/agendamentos/especialidades/'),
      listAll('/agendamentos/horarios/?status=DISPONIVEL'),
    ])
  } catch (requestError) {
    error.value = 'Não foi possível carregar a agenda agora. Confirme se a API está em execução.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main>
    <section class="hero section-pad">
      <div class="hero-copy">
        <span class="eyebrow"><Sparkles :size="15" /> Cuidado que cabe na sua rotina</span>
        <h1>Seu cuidado começa com o <em>tempo certo.</em></h1>
        <p>
          Encontre o especialista ideal, escolha um horário disponível e agende sua consulta em poucos passos.
        </p>
        <div class="hero-actions">
          <a href="#horarios" class="button button-primary">Agendar consulta <ArrowRight :size="18" /></a>
          <a href="#especialistas" class="button button-ghost">Conhecer especialistas</a>
        </div>
        <div class="trust-row">
          <span><ShieldCheck :size="18" /> Dados protegidos</span>
          <span><CalendarCheck :size="18" /> Confirmação imediata</span>
        </div>
      </div>
      <div class="hero-visual" aria-label="Resumo de agendamento online">
        <div class="visual-orbit orbit-one"></div>
        <div class="visual-orbit orbit-two"></div>
        <div class="hero-card hero-card-main">
          <div class="hero-card-top">
            <span class="avatar avatar-lg"><HeartPulse :size="27" /></span>
            <div><small>Próximo passo</small><strong>Escolha seu especialista</strong></div>
          </div>
          <div class="progress-track"><span></span></div>
          <div class="mini-calendar">
            <span v-for="day in ['SEG', 'TER', 'QUA', 'QUI', 'SEX']" :key="day">{{ day }}</span>
            <button v-for="date in [12, 13, 14, 15, 16]" :key="date" :class="{ active: date === 14 }">{{ date }}</button>
          </div>
          <div class="availability-pill"><span></span> Horários disponíveis esta semana</div>
        </div>
        <div class="floating-note note-top"><CheckCircle2 :size="19" /><span><strong>Reserva segura</strong>sem duplicidade</span></div>
        <div class="floating-note note-bottom"><Clock3 :size="19" /><span><strong>Rápido e simples</strong>em poucos minutos</span></div>
      </div>
    </section>

    <section class="benefit-strip" aria-label="Benefícios">
      <div><span class="benefit-icon"><Search /></span><p><strong>Encontre</strong> profissionais por especialidade</p></div>
      <div><span class="benefit-icon"><Clock3 /></span><p><strong>Escolha</strong> o melhor dia e horário</p></div>
      <div><span class="benefit-icon"><CalendarCheck /></span><p><strong>Confirme</strong> sua consulta na hora</p></div>
    </section>

    <section id="especialistas" class="section section-pad specialties-section">
      <div class="section-heading split-heading">
        <div>
          <span class="eyebrow">Especialidades</span>
          <h2>Cuidado especializado para cada momento</h2>
        </div>
        <p>Profissionais credenciados e uma agenda transparente para você decidir com tranquilidade.</p>
      </div>
      <div v-if="specialties.length" class="specialty-grid">
        <button v-for="(item, index) in specialties.slice(0, 6)" :key="item.id" class="specialty-card" @click="chooseSpecialty(item.id)">
          <span class="specialty-number">0{{ index + 1 }}</span>
          <span class="specialty-icon"><Stethoscope v-if="index % 2 === 0" /><HeartPulse v-else /></span>
          <strong>{{ item.nome_especialidade }}</strong>
          <span>{{ specialists.filter((doctor) => doctor.especialidade === item.id).length }} profissional(is)</span>
          <ArrowRight :size="18" class="card-arrow" />
        </button>
      </div>
      <div v-else-if="!loading" class="empty-state compact">Nenhuma especialidade cadastrada ainda.</div>
    </section>

    <section id="horarios" class="section section-pad booking-section">
      <div class="section-heading centered-heading">
        <span class="eyebrow">Agenda online</span>
        <h2>Encontre seu próximo horário</h2>
        <p>Filtre como preferir e veja somente as vagas realmente disponíveis.</p>
      </div>

      <div class="booking-panel">
        <div class="filters-row">
          <label>
            <span>Especialidade</span>
            <select v-model="selectedSpecialty" @change="selectedSpecialist = ''">
              <option value="">Todas as especialidades</option>
              <option v-for="item in specialties" :key="item.id" :value="String(item.id)">{{ item.nome_especialidade }}</option>
            </select>
          </label>
          <label>
            <span>Profissional</span>
            <select v-model="selectedSpecialist">
              <option value="">Todos os especialistas</option>
              <option v-for="item in filteredSpecialists" :key="item.id" :value="String(item.id)">{{ item.nome }}</option>
            </select>
          </label>
          <label>
            <span>Data</span>
            <input v-model="selectedDate" type="date" />
          </label>
        </div>

        <p v-if="error" class="alert alert-error">{{ error }}</p>
        <div v-if="loading" class="slot-grid skeleton-grid"><span v-for="item in 4" :key="item"></span></div>
        <div v-else-if="filteredSlots.length" class="slot-grid">
          <article v-for="slot in filteredSlots" :key="slot.id" class="slot-card">
            <div class="slot-date"><strong>{{ formatDate(slot.data) }}</strong><span>{{ shortTime(slot.horario_inicio) }} – {{ shortTime(slot.horario_fim) }}</span></div>
            <div class="slot-doctor"><span class="avatar">{{ slot.nome_especialista?.[0] }}</span><div><strong>Dr(a). {{ slot.nome_especialista }}</strong><span>{{ slot.especialidade }}</span></div></div>
            <button class="button button-primary button-block" type="button" @click="book(slot)">Escolher horário <ArrowRight :size="17" /></button>
          </article>
        </div>
        <div v-else class="empty-state">
          <CalendarCheck :size="32" />
          <strong>Nenhum horário encontrado</strong>
          <span>Tente remover algum filtro ou escolher outra data.</span>
        </div>
      </div>
    </section>

    <section class="cta-section section-pad">
      <div>
        <span class="eyebrow eyebrow-light"><UserRoundCheck :size="15" /> Acesso personalizado</span>
        <h2>Uma agenda simples para quem cuida e para quem é cuidado.</h2>
      </div>
      <RouterLink :to="session.isAuthenticated ? '/painel' : '/entrar'" class="button button-light">
        {{ session.isAuthenticated ? 'Abrir meu painel' : 'Acessar minha conta' }} <ArrowRight :size="18" />
      </RouterLink>
    </section>
  </main>
</template>
