import { defineStore } from 'pinia'
import { request } from '../services/api'

export const useSessionStore = defineStore('session', {
  state: () => ({
    profile: JSON.parse(localStorage.getItem('clinica.profile') || 'null'),
    loading: false,
  }),
  getters: {
    isAuthenticated: () => Boolean(localStorage.getItem('clinica.access')),
    role: (state) => state.profile?.is_superuser ? 'INTERNO' : state.profile?.tipo_usuario,
  },
  actions: {
    async login(credentials) {
      this.loading = true
      try {
        const tokens = await request('/token/', {
          method: 'POST',
          body: JSON.stringify(credentials),
        })
        localStorage.setItem('clinica.access', tokens.access)
        localStorage.setItem('clinica.refresh', tokens.refresh)
        await this.loadProfile()
      } catch (error) {
        this.logout()
        throw error
      } finally {
        this.loading = false
      }
    },
    async loadProfile() {
      this.profile = await request('/usuarios/me/')
      localStorage.setItem('clinica.profile', JSON.stringify(this.profile))
    },
    logout() {
      localStorage.removeItem('clinica.access')
      localStorage.removeItem('clinica.refresh')
      localStorage.removeItem('clinica.profile')
      this.profile = null
    },
  },
})
