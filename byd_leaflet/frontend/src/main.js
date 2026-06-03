import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import { createI18n } from 'vue-i18n'
import './assets/main.css'
import App from './App.vue'
import Home from './views/Home.vue'
import Quiz from './views/Quiz.vue'
import Chat from './views/Chat.vue'
import Result from './views/Result.vue'
import en from './locales/en.json'
import th from './locales/th.json'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/',       component: Home },
    { path: '/quiz',   component: Quiz },
    { path: '/chat',   component: Chat },
    { path: '/result', component: Result },
  ]
})

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en, th }
})

createApp(App).use(router).use(i18n).mount('#app')
