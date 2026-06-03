<template>
  <div style="min-height:100vh; display:flex; flex-direction:column;">
    <nav class="ev-nav">
      <router-link to="/" style="display:flex; align-items:center; gap:12px; text-decoration:none;">
        <span style="font-family:'Bebas Neue',sans-serif; font-size:22px; color:var(--c-red); letter-spacing:0.05em;">BYD</span>
        <span style="width:1px; height:16px; background:var(--c-border);"></span>
        <span style="font-size:11px; color:var(--c-silver); letter-spacing:0.12em; text-transform:uppercase;">EV Finder</span>
      </router-link>

      <button
        @click="toggleLang"
        style="font-size:11px; color:var(--c-silver); letter-spacing:0.1em; text-transform:uppercase; background:transparent; border:1px solid var(--c-border); padding:5px 12px; border-radius:3px; cursor:pointer; transition:all 0.2s;"
        @mouseenter="e => { e.target.style.borderColor='var(--c-border-hi)'; e.target.style.color='var(--c-white)'; }"
        @mouseleave="e => { e.target.style.borderColor='var(--c-border)'; e.target.style.color='var(--c-silver)'; }"
      >
        {{ locale === 'en' ? 'TH' : 'EN' }}
      </button>
    </nav>

    <main style="flex:1; padding-top:56px;">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()
function toggleLang() { locale.value = locale.value === 'en' ? 'th' : 'en' }
</script>
