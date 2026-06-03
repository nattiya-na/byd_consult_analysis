<template>
  <div class="home-wrap">
    <!-- Background: large ghost BYD text -->
    <div class="ghost-byd" aria-hidden="true">BYD</div>

    <!-- Speed sweep ambient -->
    <div class="home-sweep" aria-hidden="true"></div>

    <!-- Content -->
    <div class="home-content">

      <!-- Eyebrow -->
      <div class="anim-fade-up" style="display:flex; align-items:center; gap:10px; margin-bottom:24px;">
        <div class="slash"></div>
        <span style="font-size:11px; color:var(--c-silver); letter-spacing:0.14em; text-transform:uppercase;">Electric Vehicle Finder · Thailand</span>
      </div>

      <!-- Headline -->
      <h1 class="anim-fade-up-1 home-headline">{{ $t('home.headline') }}</h1>

      <!-- Subline -->
      <p class="anim-fade-up-2 home-sub">{{ $t('home.sub') }}</p>

      <!-- Mode cards -->
      <div class="anim-fade-up-3 mode-grid">

        <router-link to="/quiz" class="mode-card">
          <div class="mode-num">01</div>
          <div style="position:relative; z-index:1;">
            <p style="font-size:10px; color:var(--c-silver); letter-spacing:0.14em; text-transform:uppercase; margin-bottom:10px;">Mode A</p>
            <h2 class="mode-title">{{ $t('home.quiz_mode') }}</h2>
            <p class="mode-desc">{{ $t('home.quiz_desc') }}</p>
            <div class="mode-arrow">
              <span>Select</span>
              <svg width="14" height="10" viewBox="0 0 14 10" fill="none" style="transition:transform 0.2s;">
                <path d="M8 1l5 4-5 4M1 5h12" stroke="var(--c-red)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </router-link>

        <router-link to="/chat" class="mode-card">
          <div class="mode-num">02</div>
          <div style="position:relative; z-index:1;">
            <p style="font-size:10px; color:var(--c-silver); letter-spacing:0.14em; text-transform:uppercase; margin-bottom:10px;">Mode B</p>
            <h2 class="mode-title">{{ $t('home.chat_mode') }}</h2>
            <p class="mode-desc">{{ $t('home.chat_desc') }}</p>
            <div class="mode-arrow">
              <span>Select</span>
              <svg width="14" height="10" viewBox="0 0 14 10" fill="none" style="transition:transform 0.2s;">
                <path d="M8 1l5 4-5 4M1 5h12" stroke="var(--c-red)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </router-link>

      </div>

      <!-- Trust bar -->
      <div class="anim-fade-up-4 trust-bar">
        <span class="trust-item"><span class="trust-dot"></span>11 BYD models</span>
        <span class="trust-sep"></span>
        <span class="trust-item"><span class="trust-dot"></span>Thai EV survey data</span>
        <span class="trust-sep"></span>
        <span class="trust-item"><span class="trust-dot"></span>Real savings calculator</span>
      </div>

    </div>
  </div>
</template>

<style scoped>
.home-wrap {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  position: relative;
  overflow: hidden;
}

/* Giant ghost "BYD" behind everything */
.ghost-byd {
  position: absolute;
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(160px, 40vw, 380px);
  color: rgba(226, 35, 26, 0.03);
  user-select: none;
  pointer-events: none;
  right: -40px;
  bottom: -40px;
  line-height: 0.85;
  letter-spacing: -0.02em;
}

.home-sweep {
  position: absolute;
  top: 0;
  left: -80%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(226,35,26,0.025), transparent);
  animation: sweep 6s ease-in-out infinite;
  pointer-events: none;
}

.home-content {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 640px;
}

.home-headline {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(48px, 10vw, 76px);
  color: var(--c-white);
  line-height: 0.95;
  letter-spacing: 0.01em;
  margin-bottom: 20px;
  text-transform: uppercase;
}

.home-sub {
  font-size: 15px;
  color: var(--c-dim);
  line-height: 1.6;
  margin-bottom: 40px;
  max-width: 440px;
}

.mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 36px;
}
@media (max-width: 480px) { .mode-grid { grid-template-columns: 1fr; } }

/* Mode card big number watermark */
.mode-num {
  position: absolute;
  bottom: -10px;
  right: 12px;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 80px;
  color: rgba(255,255,255,0.03);
  line-height: 1;
  pointer-events: none;
  user-select: none;
}

.mode-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 26px;
  color: var(--c-white);
  letter-spacing: 0.02em;
  margin-bottom: 6px;
}

.mode-desc {
  font-size: 12px;
  color: var(--c-dim);
  line-height: 1.5;
  margin-bottom: 20px;
}

.mode-arrow {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--c-red);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 600;
}

/* Trust bar */
.trust-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.trust-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(136,136,136,0.6);
  letter-spacing: 0.06em;
}
.trust-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--c-red);
  opacity: 0.6;
}
.trust-sep {
  width: 1px;
  height: 12px;
  background: var(--c-border);
}
</style>
