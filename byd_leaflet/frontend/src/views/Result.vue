<template>
  <div v-if="result" class="result-wrap anim-fade-in">

    <!-- Hero -->
    <div class="result-hero">
      <!-- Car image or typographic fallback -->
      <div class="hero-img-wrap">
        <img
          v-if="model.image_url && !imgError"
          :src="model.image_url"
          :alt="model.name"
          class="hero-img"
          @error="imgError = true"
        />
        <div v-else class="hero-fallback">
          <span class="hero-fallback-type">{{ model.type }}</span>
          <span class="hero-fallback-name">{{ model.name }}</span>
        </div>
        <!-- Diagonal red overlay bottom -->
        <div class="hero-overlay"></div>
      </div>

      <!-- Badges row -->
      <div class="hero-badges">
        <span class="badge-match">{{ $t('result.match_label') }}</span>
        <span class="badge-type">{{ model.type }}</span>
      </div>

      <!-- Name + tagline -->
      <div class="hero-text">
        <h1 class="hero-name">{{ model.name }}</h1>
        <p class="hero-tagline">"{{ tagline[$i18n.locale] || tagline.en }}"</p>
        <div class="hero-specs">
          <span>{{ $t('result.price_label') }} <strong>฿{{ formatNum(model.price_thb) }}</strong></span>
          <span class="spec-sep"></span>
          <span>{{ $t('result.range_label') }} <strong>{{ model.range_km }} km</strong></span>
          <span class="spec-sep"></span>
          <span>{{ model.seats }} seats</span>
        </div>
      </div>
    </div>

    <!-- Savings -->
    <section class="result-section anim-fade-up-1">
      <div class="section-eyebrow">
        <div class="slash"></div>
        <span>{{ $t('result.savings_title') }}</span>
      </div>

      <div class="savings-bars">
        <div class="savings-row">
          <div class="savings-meta">
            <span class="savings-label">{{ $t('result.ice_label') }}</span>
            <span class="savings-val dim">฿{{ formatNum(savings.ice_annual_cost_thb) }}</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill dim-fill" style="width:100%;"></div>
          </div>
        </div>
        <div class="savings-row">
          <div class="savings-meta">
            <span class="savings-label">{{ $t('result.ev_label') }}</span>
            <span class="savings-val red">฿{{ formatNum(savings.ev_annual_cost_thb) }}</span>
          </div>
          <div class="bar-track">
            <div
              class="bar-fill red-fill savings-bar-fill"
              :style="{ width: `${Math.round((savings.ev_annual_cost_thb / savings.ice_annual_cost_thb) * 100)}%` }"
            ></div>
          </div>
        </div>
      </div>

      <div class="savings-summary">
        <div class="summary-card red-card">
          <span class="summary-num">฿{{ formatNum(savings.annual_savings_thb) }}</span>
          <span class="summary-label">{{ $t('result.savings_label') }} {{ $t('result.per_year') }}</span>
        </div>
        <div class="summary-card green-card">
          <span class="summary-num green">{{ formatNum(savings.co2_saved_kg) }} kg</span>
          <span class="summary-label">{{ $t('result.co2_label') }}</span>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="result-section anim-fade-up-2">
      <div class="section-eyebrow">
        <div class="slash"></div>
        <span>{{ $t('result.features_title') }}</span>
      </div>
      <ul class="features-list">
        <li v-for="(feat, i) in model.features" :key="i" class="feature-item">
          <span class="feature-dot"></span>
          <span>{{ feat }}</span>
        </li>
      </ul>
    </section>

    <!-- Alternatives -->
    <section v-if="result.alternatives?.length" class="result-section anim-fade-up-3">
      <div class="section-eyebrow">
        <div class="slash"></div>
        <span>{{ $t('result.alternatives_title') }}</span>
      </div>
      <div class="alts-list">
        <div v-for="alt in result.alternatives" :key="alt.id" class="alt-row">
          <div>
            <p class="alt-name">{{ alt.name }}</p>
            <p class="alt-meta">{{ alt.type }} &middot; {{ alt.range_km }} km range</p>
          </div>
          <span class="alt-price">฿{{ formatNum(alt.price_thb) }}</span>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <div class="result-cta anim-fade-up-4">
      <a :href="model.reverautomotive_url" target="_blank" rel="noopener" class="btn-red" style="flex:1; text-align:center;">
        {{ $t('result.cta') }}
      </a>
      <router-link to="/" class="btn-ghost" style="flex:1; text-align:center;">
        {{ $t('result.restart') }}
      </router-link>
    </div>

    <p class="disclaimer">Savings estimates based on Thai fuel &amp; electricity prices. Results may vary.</p>

  </div>

  <div v-else class="no-result">
    <p>{{ $t('common.error') }}</p>
    <router-link to="/" class="btn-red" style="margin-top:16px;">Start over</router-link>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const result   = ref(null)
const imgError = ref(false)

const model   = computed(() => result.value?.recommended)
const tagline = computed(() => result.value?.tagline || {})
const savings = computed(() => result.value?.savings  || {})

function formatNum(n) {
  if (n == null) return '–'
  return Number(n).toLocaleString()
}

onMounted(() => {
  const raw = sessionStorage.getItem('byd_result')
  if (raw) result.value = JSON.parse(raw)
})
</script>

<style scoped>
.result-wrap {
  max-width: 640px;
  margin: 0 auto;
  padding: 24px 16px 64px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ── Hero ───────────────────────────────────────────────── */
.result-hero {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
  position: relative;
}
.hero-img-wrap {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #0d0d0d;
}
.hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  opacity: 0.75;
}
/* Typographic fallback when image fails */
.hero-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
}
/* Ghost BYD text behind fallback */
.hero-fallback::before {
  content: 'BYD';
  position: absolute;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 140px;
  color: rgba(226, 35, 26, 0.06);
  letter-spacing: -0.02em;
  pointer-events: none;
  line-height: 1;
}
.hero-fallback-type {
  font-size: 11px;
  color: var(--c-red);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 700;
  position: relative;
  z-index: 1;
}
.hero-fallback-name {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 42px;
  color: var(--c-white);
  letter-spacing: 0.04em;
  position: relative;
  z-index: 1;
}
/* Diagonal red gradient overlay at bottom of hero image */
.hero-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60%;
  background: linear-gradient(to top, var(--c-card) 0%, transparent 100%);
  pointer-events: none;
}

.hero-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px 0;
}
.badge-match {
  font-size: 10px;
  color: var(--c-red);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-weight: 700;
  border: 1px solid rgba(226,35,26,0.3);
  padding: 3px 8px;
  border-radius: 2px;
}
.badge-type {
  font-size: 10px;
  color: var(--c-silver);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border: 1px solid var(--c-border);
  padding: 3px 8px;
  border-radius: 2px;
}

.hero-text {
  padding: 12px 20px 20px;
}
.hero-name {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(36px, 8vw, 54px);
  color: var(--c-white);
  letter-spacing: 0.02em;
  line-height: 1;
  margin-bottom: 6px;
}
.hero-tagline {
  font-size: 14px;
  font-style: italic;
  color: var(--c-red);
  font-weight: 500;
  margin-bottom: 12px;
  line-height: 1.4;
}
.hero-specs {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--c-dim);
}
.hero-specs strong { color: var(--c-white); }
.spec-sep { width: 1px; height: 12px; background: var(--c-border); }

/* ── Sections ───────────────────────────────────────────── */
.result-section {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 8px;
}
.section-eyebrow {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}
.section-eyebrow span {
  font-size: 11px;
  color: var(--c-silver);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 600;
}

/* Savings bars */
.savings-bars { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
.savings-row  { display: flex; flex-direction: column; gap: 5px; }
.savings-meta { display: flex; justify-content: space-between; align-items: baseline; }
.savings-label { font-size: 12px; color: var(--c-silver); }
.savings-val   { font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }
.savings-val.dim { color: rgba(240,240,240,0.5); }
.savings-val.red { color: var(--c-red); }
.bar-track { height: 5px; background: var(--c-border); border-radius: 2px; overflow: hidden; }
.bar-fill  { height: 100%; border-radius: 2px; }
.dim-fill  { background: var(--c-border-hi); }
.red-fill  { background: var(--c-red); box-shadow: 0 0 8px var(--c-red-glow); }

.savings-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 4px; }
.summary-card {
  border-radius: 6px;
  padding: 14px 16px;
  border: 1px solid;
}
.red-card   { background: rgba(226,35,26,0.07); border-color: rgba(226,35,26,0.2); }
.green-card { background: rgba(74,222,128,0.06); border-color: rgba(74,222,128,0.2); }
.summary-num {
  display: block;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 26px;
  color: var(--c-red);
  letter-spacing: 0.03em;
  line-height: 1.1;
}
.summary-num.green { color: #4ade80; }
.summary-label {
  display: block;
  font-size: 10px;
  color: var(--c-silver);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 4px;
}

/* Features */
.features-list { display: flex; flex-direction: column; gap: 10px; }
.feature-item  { display: flex; align-items: flex-start; gap: 10px; font-size: 13px; color: rgba(240,240,240,0.8); line-height: 1.5; }
.feature-dot   { width: 5px; height: 5px; border-radius: 50%; background: var(--c-red); margin-top: 6px; flex-shrink: 0; }

/* Alternatives */
.alts-list   { display: flex; flex-direction: column; gap: 6px; }
.alt-row     { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); border: 1px solid var(--c-border); border-radius: 5px; padding: 12px 14px; }
.alt-name    { font-size: 13px; font-weight: 600; color: var(--c-white); }
.alt-meta    { font-size: 11px; color: var(--c-silver); margin-top: 2px; }
.alt-price   { font-size: 13px; color: var(--c-dim); font-variant-numeric: tabular-nums; }

/* CTA */
.result-cta {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}

/* Disclaimer */
.disclaimer {
  text-align: center;
  font-size: 10px;
  color: rgba(136,136,136,0.4);
  margin-top: 24px;
  letter-spacing: 0.04em;
  line-height: 1.6;
}

/* No result */
.no-result {
  min-height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--c-silver);
  font-size: 14px;
}
</style>
