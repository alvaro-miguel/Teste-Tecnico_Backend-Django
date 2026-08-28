import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/entrar', name: 'login', component: LoginView, meta: { guest: true } },
    { path: '/painel', name: 'dashboard', component: DashboardView, meta: { auth: true } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  const loggedIn = Boolean(localStorage.getItem('clinica.access'))
  if (to.meta.auth && !loggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guest && loggedIn) return { name: 'dashboard' }
})

export default router
