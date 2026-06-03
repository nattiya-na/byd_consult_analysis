<template>
  <div class="quiz-wrap">

    <!-- Progress rail (left edge) -->
    <div class="progress-rail">
      <div class="progress-fill" :style="{ height: `${((step + 1) / questions.length) * 100}%` }"></div>
    </div>

    <!-- Step counter -->
    <div class="step-meta">
      <span class="step-label">{{ String(step + 1).padStart(2, '0') }} / {{ String(questions.length).padStart(2, '0') }}</span>
      <button v-if="step > 0" @click="step--" class="back-btn">
        <svg width="12" height="8" viewBox="0 0 12 8" fill="none">
          <path d="M4 1L1 4l3 3M1 4h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('quiz.back') }}
      </button>
    </div>

    <!-- Question card -->
    <transition name="quiz-slide" mode="out-in">
      <div :key="step" class="quiz-card-wrap">

        <!-- Ghost number -->
        <div class="ghost-num" aria-hidden="true">{{ String(step + 1).padStart(2, '0') }}</div>

        <div class="quiz-card scan-card">
          <!-- Question label + text -->
          <div class="q-header">
            <div class="slash" style="margin-top:3px; flex-shrink:0;"></div>
            <div>
              <p class="q-tag">{{ currentQ.tag }}</p>
              <h2 class="q-text">{{ currentQ.question }}</h2>
              <p v-if="currentQ.sub" class="q-sub">{{ currentQ.sub }}</p>
            </div>
          </div>

          <!-- Options -->
          <div :class="currentQ.twoCol ? 'opts-2col' : 'opts-1col'">
            <button
              v-for="(opt, val) in currentQ.options"
              :key="val"
              @click="select(val)"
              :class="['opt-card', answers[currentQ.key] === val ? 'selected' : '']"
            >
              <div class="opt-inner">
                <span class="opt-label">{{ opt.label }}</span>
                <span v-if="opt.sub" class="opt-sub">{{ opt.sub }}</span>
              </div>
              <div class="opt-check" :class="{ active: answers[currentQ.key] === val }">
                <svg v-if="answers[currentQ.key] === val" width="10" height="8" viewBox="0 0 10 8" fill="none">
                  <path d="M1 4l3 3 5-6" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-ring"></div>
      <p class="loading-text">{{ $t('common.loading') }}</p>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import axios from 'axios'

const { t, tm } = useI18n()
const router = useRouter()

const step = ref(0)
const answers = ref({})
const loading = ref(false)

function buildOptions(optKeys, labelKeys, subKeys) {
  const labels = tm(labelKeys)
  const subs   = tm(subKeys)
  const result = {}
  for (const k of optKeys) {
    result[k] = { label: labels[k] || k, sub: subs?.[k] || '' }
  }
  return result
}

const questions = computed(() => [
  {
    key:      'daily_km',
    tag:      t('quiz.q1.tag'),
    question: t('quiz.q1.question'),
    options:  buildOptions(['<20','20-50','50-100','100+'], 'quiz.q1.options', 'quiz.q1.subs'),
    twoCol:   true,
  },
  {
    key:      'age_group',
    tag:      t('quiz.q2.tag'),
    question: t('quiz.q2.question'),
    options:  buildOptions(['18-24','25-34','35-54','55+'], 'quiz.q2.options', 'quiz.q2.subs'),
    twoCol:   true,
  },
  {
    key:      'drive_style',
    tag:      t('quiz.q3.tag'),
    question: t('quiz.q3.question'),
    options:  buildOptions(['city','mixed','highway'], 'quiz.q3.options', 'quiz.q3.subs'),
    twoCol:   false,
  },
  {
    key:      'long_trips',
    tag:      t('quiz.q4.tag'),
    question: t('quiz.q4.question'),
    options:  buildOptions(['true','false'], 'quiz.q4.options', 'quiz.q4.subs'),
    twoCol:   true,
  },
  {
    key:      'home_charging',
    tag:      t('quiz.q5.tag'),
    question: t('quiz.q5.question'),
    options:  buildOptions(['yes','unsure','no'], 'quiz.q5.options', 'quiz.q5.subs'),
    twoCol:   false,
  },
  {
    key:      'fuel_type',
    tag:      t('quiz.q6.tag'),
    question: t('quiz.q6.question'),
    sub:      t('quiz.q6.sub'),
    options:  buildOptions(['petrol','diesel','none'], 'quiz.q6.options', 'quiz.q6.subs'),
    twoCol:   false,
  },
])

const currentQ = computed(() => questions.value[step.value])

async function select(val) {
  answers.value[currentQ.value.key] = val
  if (step.value < questions.value.length - 1) { step.value++; return }

  loading.value = true
  try {
    const payload = {
      daily_km:      answers.value.daily_km,
      age_group:     answers.value.age_group,
      drive_style:   answers.value.drive_style,
      long_trips:    answers.value.long_trips === 'true',
      home_charging: answers.value.home_charging,
      fuel_type:     answers.value.fuel_type === 'none' ? 'petrol' : answers.value.fuel_type,
    }
    const { data } = await axios.post('/api/recommend', payload)
    sessionStorage.setItem('byd_result', JSON.stringify(data))
    router.push('/result')
  } catch { alert(t('common.error')) }
  finally { loading.value = false }
}
</script>

<style scoped>
.quiz-wrap {
  min-height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px 32px 40px;
  position: relative;
}

/* Left vertical progress rail */
.progress-rail {
  position: fixed;
  left: 16px;
  top: 56px;
  bottom: 0;
  width: 2px;
  background: var(--c-border);
  z-index: 10;
}
.progress-fill {
  width: 100%;
  background: var(--c-red);
  transition: height 0.5s ease;
  box-shadow: 0 0 8px var(--c-red-glow-hi);
}

/* Step meta row */
.step-meta {
  width: 100%;
  max-width: 560px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.step-label {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 20px;
  color: var(--c-silver);
  letter-spacing: 0.08em;
}
.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--c-silver);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0;
}
.back-btn:hover { color: var(--c-white); }

/* Card wrapper (positions ghost num relative to card) */
.quiz-card-wrap {
  position: relative;
  width: 100%;
  max-width: 560px;
}

/* Ghost number behind card */
.ghost-num {
  position: absolute;
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(100px, 20vw, 160px);
  color: rgba(226, 35, 26, 0.05);
  user-select: none;
  pointer-events: none;
  line-height: 1;
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 0;
}

.quiz-card {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  padding: 32px 28px;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.q-header {
  display: flex;
  gap: 14px;
  margin-bottom: 28px;
}
.q-tag {
  font-size: 10px;
  color: var(--c-red);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 6px;
  font-weight: 600;
}
.q-text {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(26px, 5vw, 36px);
  color: var(--c-white);
  line-height: 1.05;
  letter-spacing: 0.02em;
}
.q-sub {
  font-size: 12px;
  color: var(--c-dim);
  margin-top: 6px;
}

/* Option grids */
.opts-1col { display: flex; flex-direction: column; gap: 8px; }
.opts-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

/* Option inner content */
.opt-inner { flex: 1; min-width: 0; }
.opt-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--c-white);
  line-height: 1.3;
}
.opt-sub {
  display: block;
  font-size: 11px;
  color: var(--c-silver);
  margin-top: 3px;
  line-height: 1.4;
}

/* Checkmark circle */
.opt-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--c-border-hi);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}
.opt-check.active {
  background: var(--c-red);
  border-color: var(--c-red);
  box-shadow: 0 0 8px var(--c-red-glow-hi);
}

/* Slide transition */
.quiz-slide-enter-active { animation: slideIn 0.3s ease forwards; }
.quiz-slide-leave-active { animation: slideIn 0.2s ease reverse; }

/* Loading overlay */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(8,8,8,0.85);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 100;
}
.loading-ring {
  width: 48px;
  height: 48px;
  border: 2px solid var(--c-border);
  border-top-color: var(--c-red);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.loading-text {
  font-size: 12px;
  color: var(--c-silver);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
</style>
