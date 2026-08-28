<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { BookOpen, Check, ClipboardPlus, Plus, Search, Stethoscope, Trash2, UserPlus, Users, X } from 'lucide-vue-next'
import { listAll, request } from '../../services/api'
import { useSessionStore } from '../../stores/session'
import { maskCpf, maskPhone } from '../../utils/masks'

const session = useSessionStore()
const activeTab = ref('especialidades')
const specialties = ref([])
const specialists = ref([])
const patients = ref([])
const appointments = ref([])
const search = ref('')
const formKind = ref('')
const saving = ref(false)
const notice = ref(null)
const specialtyName = ref('')
const specialistForm = reactive({ username: '', password: '', first_name: '', last_name: '', email: '', cpf: '', telefone: '', crm: '', especialidade: '' })
const patientForm = reactive({ username: '', password: '', first_name: '', last_name: '', email: '', cpf: '', telefone: '' })

const tabs = [
  { id: 'especialidades', label: 'Especialidades', icon: BookOpen },
  { id: 'especialistas', label: 'Especialistas', icon: Stethoscope },
  { id: 'pacientes', label: 'Pacientes', icon: Users },
  { id: 'consultas', label: 'Consultas', icon: ClipboardPlus },
]
const filteredSpecialties = computed(() => specialties.value.filter((item) => item.nome_especialidade.toLowerCase().includes(search.value.toLowerCase())))
const filteredSpecialists = computed(() => specialists.value.filter((item) => `${item.nome} ${item.crm} ${item.especialidade_detalhe?.nome_especialidade}`.toLowerCase().includes(search.value.toLowerCase())))
const filteredPatients = computed(() => patients.value.filter((item) => `${item.nome} ${item.telefone || ''}`.toLowerCase().includes(search.value.toLowerCase())))

async function load() {
  try {
    ;[specialties.value, specialists.value, patients.value, appointments.value] = await Promise.all([
      listAll('/agendamentos/especialidades/'),
      listAll('/usuarios/especialistas/'),
      listAll('/usuarios/pacientes/'),
      listAll('/agendamentos/consultas/'),
    ])
  } catch (error) { notice.value = { type: 'error', text: error.message } }
}

function userPayload(form) {
  return {
    username: form.username,
    password: form.password,
    first_name: form.first_name,
    last_name: form.last_name,
    email: form.email,
    cpf: form.cpf || null,
    telefone: form.telefone || null,
  }
}

function resetForm(form) { Object.keys(form).forEach((key) => { form[key] = '' }) }

function applyMask(form, field, mask, event) {
  const maskedValue = mask(event.target.value)
  form[field] = maskedValue
  event.target.value = maskedValue
}

async function createSpecialty() {
  saving.value = true
  try {
    await request('/agendamentos/especialidades/', { method: 'POST', body: JSON.stringify({ nome_especialidade: specialtyName.value }) })
    specialtyName.value = ''
    formKind.value = ''
    notice.value = { type: 'success', text: 'Especialidade cadastrada com sucesso.' }
    await load()
  } catch (error) { notice.value = { type: 'error', text: error.message } }
  finally { saving.value = false }
}

async function createSpecialist() {
  saving.value = true
  try {
    await request('/usuarios/especialistas/', { method: 'POST', body: JSON.stringify({ usuario: userPayload(specialistForm), crm: specialistForm.crm, especialidade: Number(specialistForm.especialidade) }) })
    resetForm(specialistForm)
    formKind.value = ''
    notice.value = { type: 'success', text: 'Especialista credenciado e acesso criado.' }
    await load()
  } catch (error) { notice.value = { type: 'error', text: error.message } }
  finally { saving.value = false }
}

async function createPatient() {
  saving.value = true
  try {
    await request('/usuarios/pacientes/', { method: 'POST', body: JSON.stringify({ usuario: userPayload(patientForm) }) })
    resetForm(patientForm)
    formKind.value = ''
    notice.value = { type: 'success', text: 'Paciente cadastrado e acesso criado.' }
    await load()
  } catch (error) { notice.value = { type: 'error', text: error.message } }
  finally { saving.value = false }
}

async function deactivate(resource, id, label) {
  if (!window.confirm(`Desativar ${label}? Esta ação remove o registro das listagens ativas.`)) return
  try {
    await request(`${resource}${id}/`, { method: 'DELETE' })
    notice.value = { type: 'success', text: 'Registro desativado com sucesso.' }
    await load()
  } catch (error) { notice.value = { type: 'error', text: error.message } }
}

function changeTab(id) { activeTab.value = id; search.value = ''; formKind.value = '' }
onMounted(load)
</script>

<template>
  <div class="dashboard-content internal-dashboard">
    <div class="dashboard-welcome internal-welcome"><div><span class="eyebrow">Gestão interna</span><h1>Olá, {{ session.profile?.nome?.split(' ')[0] }}.</h1><p>Credencie pessoas e mantenha a operação da clínica organizada.</p></div><span class="welcome-icon"><ClipboardPlus /></span></div>
    <div class="stats-grid four-cols"><article><span class="stat-icon"><BookOpen /></span><div><strong>{{ specialties.length }}</strong><span>especialidades</span></div></article><article><span class="stat-icon"><Stethoscope /></span><div><strong>{{ specialists.length }}</strong><span>especialistas</span></div></article><article><span class="stat-icon"><Users /></span><div><strong>{{ patients.length }}</strong><span>pacientes</span></div></article><article><span class="stat-icon"><ClipboardPlus /></span><div><strong>{{ appointments.length }}</strong><span>consultas</span></div></article></div>

    <div class="dashboard-tabs internal-tabs" role="tablist"><button v-for="tab in tabs" :key="tab.id" :class="{ active: activeTab === tab.id }" @click="changeTab(tab.id)"><component :is="tab.icon" :size="18" /> {{ tab.label }}</button></div>
    <p v-if="notice" :class="['alert', notice.type === 'success' ? 'alert-success' : 'alert-error']"><Check v-if="notice.type === 'success'" :size="18" />{{ notice.text }}<button type="button" @click="notice = null"><X :size="17" /></button></p>

    <section class="dashboard-panel">
      <div class="panel-title">
        <div><h2>{{ tabs.find((tab) => tab.id === activeTab)?.label }}</h2><p v-if="activeTab === 'especialidades'">Áreas de atendimento oferecidas pela clínica.</p><p v-else-if="activeTab === 'especialistas'">Profissionais credenciados e suas especialidades.</p><p v-else-if="activeTab === 'pacientes'">Pessoas autorizadas a reservar consultas.</p><p v-else>Visão consolidada de todos os atendimentos.</p></div>
        <button v-if="activeTab !== 'consultas'" class="button button-primary" @click="formKind = formKind ? '' : activeTab"><Plus :size="18" /> {{ activeTab === 'especialidades' ? 'Nova especialidade' : activeTab === 'especialistas' ? 'Credenciar especialista' : 'Cadastrar paciente' }}</button>
      </div>

      <form v-if="formKind === 'especialidades'" class="inline-form specialty-form" @submit.prevent="createSpecialty"><label><span>Nome da especialidade</span><input v-model.trim="specialtyName" required placeholder="Ex.: Cardiologia" /></label><div class="form-actions"><button type="button" class="button button-ghost" @click="formKind = ''">Cancelar</button><button class="button button-primary" :disabled="saving">{{ saving ? 'Salvando…' : 'Cadastrar' }}</button></div></form>

      <form v-if="formKind === 'especialistas'" class="credential-form" @submit.prevent="createSpecialist">
        <div class="form-section-title"><UserPlus /><div><strong>Dados do especialista</strong><span>O usuário e a senha serão usados para acessar o painel profissional.</span></div></div>
        <div class="form-grid"><label><span>Nome *</span><input v-model.trim="specialistForm.first_name" required /></label><label><span>Sobrenome</span><input v-model.trim="specialistForm.last_name" /></label><label><span>Usuário *</span><input v-model.trim="specialistForm.username" required autocomplete="off" /></label><label><span>Senha *</span><input v-model="specialistForm.password" type="password" required minlength="8" autocomplete="new-password" /></label><label><span>E-mail</span><input v-model.trim="specialistForm.email" type="email" /></label><label><span>Telefone</span><input :value="specialistForm.telefone" type="tel" inputmode="numeric" maxlength="15" autocomplete="tel" placeholder="(11) 99999-9999" @input="applyMask(specialistForm, 'telefone', maskPhone, $event)" /></label><label><span>CPF</span><input :value="specialistForm.cpf" inputmode="numeric" maxlength="14" placeholder="000.000.000-00" @input="applyMask(specialistForm, 'cpf', maskCpf, $event)" /></label><label><span>CRM *</span><input v-model.trim="specialistForm.crm" required placeholder="CRM-SP 12345" /></label><label class="span-two"><span>Especialidade *</span><select v-model="specialistForm.especialidade" required><option value="" disabled>Selecione</option><option v-for="item in specialties" :key="item.id" :value="item.id">{{ item.nome_especialidade }}</option></select></label></div>
        <div class="form-actions"><button type="button" class="button button-ghost" @click="formKind = ''">Cancelar</button><button class="button button-primary" :disabled="saving">{{ saving ? 'Credenciando…' : 'Credenciar especialista' }}</button></div>
      </form>

      <form v-if="formKind === 'pacientes'" class="credential-form" @submit.prevent="createPatient">
        <div class="form-section-title"><UserPlus /><div><strong>Dados do paciente</strong><span>Crie as credenciais que darão acesso à agenda online.</span></div></div>
        <div class="form-grid"><label><span>Nome *</span><input v-model.trim="patientForm.first_name" required /></label><label><span>Sobrenome</span><input v-model.trim="patientForm.last_name" /></label><label><span>Usuário *</span><input v-model.trim="patientForm.username" required autocomplete="off" /></label><label><span>Senha *</span><input v-model="patientForm.password" type="password" required minlength="8" autocomplete="new-password" /></label><label><span>E-mail</span><input v-model.trim="patientForm.email" type="email" /></label><label><span>Telefone</span><input :value="patientForm.telefone" type="tel" inputmode="numeric" maxlength="15" autocomplete="tel" placeholder="(11) 99999-9999" @input="applyMask(patientForm, 'telefone', maskPhone, $event)" /></label><label class="span-two"><span>CPF</span><input :value="patientForm.cpf" inputmode="numeric" maxlength="14" placeholder="000.000.000-00" @input="applyMask(patientForm, 'cpf', maskCpf, $event)" /></label></div>
        <div class="form-actions"><button type="button" class="button button-ghost" @click="formKind = ''">Cancelar</button><button class="button button-primary" :disabled="saving">{{ saving ? 'Cadastrando…' : 'Cadastrar paciente' }}</button></div>
      </form>

      <label v-if="activeTab !== 'consultas'" class="search-box"><Search :size="18" /><input v-model="search" :placeholder="`Buscar ${tabs.find((tab) => tab.id === activeTab)?.label.toLowerCase()}…`" /></label>

      <div v-if="activeTab === 'especialidades'" class="management-grid"><article v-for="item in filteredSpecialties" :key="item.id" class="management-card"><span class="management-icon"><BookOpen /></span><div><strong>{{ item.nome_especialidade }}</strong><span>{{ specialists.filter((doctor) => doctor.especialidade === item.id).length }} especialista(s)</span></div><button class="icon-button danger" aria-label="Desativar especialidade" @click="deactivate('/agendamentos/especialidades/', item.id, item.nome_especialidade)"><Trash2 :size="18" /></button></article></div>

      <div v-else-if="activeTab === 'especialistas'" class="table-wrap"><table><thead><tr><th>Profissional</th><th>Especialidade</th><th>CRM</th><th></th></tr></thead><tbody><tr v-for="item in filteredSpecialists" :key="item.id"><td><span class="table-person"><span class="avatar">{{ item.nome?.[0] }}</span><strong>Dr(a). {{ item.nome }}</strong></span></td><td>{{ item.especialidade_detalhe?.nome_especialidade }}</td><td>{{ item.crm }}</td><td><button class="icon-button danger" aria-label="Desativar especialista" @click="deactivate('/usuarios/especialistas/', item.id, item.nome)"><Trash2 :size="17" /></button></td></tr></tbody></table></div>

      <div v-else-if="activeTab === 'pacientes'" class="table-wrap"><table><thead><tr><th>Paciente</th><th>Telefone</th><th>Cadastro</th><th></th></tr></thead><tbody><tr v-for="item in filteredPatients" :key="item.id"><td><span class="table-person"><span class="avatar">{{ item.nome?.[0] }}</span><strong>{{ item.nome }}</strong></span></td><td>{{ item.telefone ? maskPhone(item.telefone) : 'Não informado' }}</td><td>{{ new Intl.DateTimeFormat('pt-BR').format(new Date(item.criado_em)) }}</td><td><button class="icon-button danger" aria-label="Desativar paciente" @click="deactivate('/usuarios/pacientes/', item.id, item.nome)"><Trash2 :size="17" /></button></td></tr></tbody></table></div>

      <div v-else class="table-wrap"><table><thead><tr><th>Paciente</th><th>Especialista</th><th>Especialidade</th><th>Data e horário</th></tr></thead><tbody><tr v-for="item in appointments" :key="item.id"><td><span class="table-person"><span class="avatar">{{ item.nome_paciente?.[0] }}</span><strong>{{ item.nome_paciente }}</strong></span></td><td>Dr(a). {{ item.nome_especialista }}</td><td>{{ item.especialidade }}</td><td>{{ item.data_hora }}</td></tr></tbody></table></div>
    </section>
  </div>
</template>
