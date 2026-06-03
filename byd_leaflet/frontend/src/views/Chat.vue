<template>
  <div class="chat-wrap">

    <!-- Aria header -->
    <div class="aria-header">
      <div class="aria-avatar">A</div>
      <div>
        <p class="aria-name">{{ $t('chat.aria_name') }}</p>
        <div class="aria-status">
          <span class="status-dot"></span>
          <span>Online</span>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div ref="chatEl" class="chat-messages">
      <transition-group name="bubble">
        <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.from">

          <!-- Aria message -->
          <template v-if="msg.from === 'aria'">
            <div class="aria-bubble">{{ msg.text }}</div>
          </template>

          <!-- User message -->
          <template v-else>
            <div class="user-bubble">{{ msg.text }}</div>
          </template>

        </div>
      </transition-group>

      <!-- Typing indicator -->
      <div v-if="typing" class="msg-row aria">
        <div class="aria-bubble typing-bubble">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <!-- Quick-reply chips -->
    <div v-if="currentQ && !loading" class="chips-wrap">
      <button
        v-for="(opt, val) in currentQ.options"
        :key="val"
        @click="reply(val, opt.label)"
        class="chip-btn"
      >
        <span class="chip-label">{{ opt.label }}</span>
        <span v-if="opt.sub" class="chip-sub">{{ opt.sub }}</span>
      </button>
    </div>

    <!-- Submitting -->
    <div v-if="loading" class="submit-status">
      <div class="loading-ring-sm"></div>
      <span>{{ $t('chat.submit') }}</span>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import axios from 'axios'

const { t, tm } = useI18n()
const router = useRouter()

const messages = ref([])
const answers  = ref({})
const typing   = ref(false)
const loading  = ref(false)
const chatEl   = ref(null)
const qIndex   = ref(-1)

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
  { key: 'daily_km',      prompt: t('chat.q1'),        options: buildOptions(['<20','20-50','50-100','100+'], 'quiz.q1.options', 'quiz.q1.subs'), followUp: tm('chat.q1_follow') },
  { key: 'age_group',     prompt: t('chat.q2_prefix'), options: buildOptions(['18-24','25-34','35-54','55+'], 'quiz.q2.options', 'quiz.q2.subs') },
  { key: 'drive_style',   prompt: t('chat.q3_prefix'), options: buildOptions(['city','mixed','highway'], 'quiz.q3.options', 'quiz.q3.subs') },
  { key: 'long_trips',    prompt: t('chat.q4_prefix'), options: buildOptions(['true','false'], 'quiz.q4.options', 'quiz.q4.subs') },
  { key: 'home_charging', prompt: t('chat.q5_prefix'), options: buildOptions(['yes','unsure','no'], 'quiz.q5.options', 'quiz.q5.subs') },
  { key: 'fuel_type',     prompt: t('chat.q6_prefix'), options: buildOptions(['petrol','diesel','none'], 'quiz.q6.options', 'quiz.q6.subs') },
])

const currentQ = computed(() => {
  if (qIndex.value < 0 || qIndex.value >= questions.value.length) return null
  return questions.value[qIndex.value]
})

async function ariaType(text, delay = 700) {
  typing.value = true
  await new Promise(r => setTimeout(r, delay))
  typing.value = false
  messages.value.push({ from: 'aria', text })
  await scrollBottom()
}

async function scrollBottom() {
  await nextTick()
  if (chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight
}

async function reply(val, label) {
  const q = questions.value[qIndex.value]
  answers.value[q.key] = val
  messages.value.push({ from: 'user', text: label })
  await scrollBottom()

  if (q.followUp?.[val]) {
    await ariaType(q.followUp[val], 450)
  }

  qIndex.value++

  if (qIndex.value < questions.value.length) {
    await ariaType(questions.value[qIndex.value].prompt, q.followUp?.[val] ? 350 : 650)
  } else {
    await submit()
  }
}

async function submit() {
  loading.value = true
  await ariaType(t('chat.submit'), 400)
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
  } catch {
    await ariaType(t('common.error'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await ariaType(t('chat.aria_intro'), 500)
  qIndex.value = 0
  await ariaType(questions.value[0].prompt, 700)
})
</script>

<style scoped>
.chat-wrap {
  min-height: calc(100vh - 56px);
  max-width: 560px;
  margin: 0 auto;
  padding: 20px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Aria header */
.aria-header {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.aria-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--c-red);
  color: white;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  letter-spacing: 0.05em;
  box-shadow: 0 0 12px var(--c-red-glow);
}
.aria-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-white);
  letter-spacing: 0.02em;
}
.aria-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  color: var(--c-silver);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 2px;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 6px rgba(74, 222, 128, 0.5);
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 8px;
}

.msg-row { display: flex; }
.msg-row.user { justify-content: flex-end; }
.msg-row.aria { justify-content: flex-start; }

.aria-bubble {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-left: 2px solid var(--c-red);
  border-radius: 0 10px 10px 10px;
  padding: 11px 14px;
  max-width: 85%;
  font-size: 13.5px;
  color: var(--c-white);
  line-height: 1.55;
  animation: bubbleIn 0.25s ease forwards;
}

.user-bubble {
  background: var(--c-red);
  border-radius: 10px 10px 0 10px;
  padding: 11px 14px;
  max-width: 75%;
  font-size: 13.5px;
  color: white;
  font-weight: 500;
  line-height: 1.55;
  animation: bubbleIn 0.2s ease forwards;
}

/* Typing dots */
.typing-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 14px 16px;
}
.typing-bubble span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--c-silver);
  animation: bounce 1.2s ease infinite;
}
.typing-bubble span:nth-child(2) { animation-delay: 0.15s; }
.typing-bubble span:nth-child(3) { animation-delay: 0.30s; }

/* Quick-reply chips */
.chips-wrap {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chip-btn {
  width: 100%;
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 6px;
  padding: 12px 16px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
  overflow: hidden;
}
.chip-btn::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 2px; height: 100%;
  background: var(--c-red);
  transform: scaleY(0);
  transform-origin: top;
  transition: transform 0.2s;
}
.chip-btn:hover {
  border-color: rgba(226,35,26,0.45);
  background: #120808;
}
.chip-btn:hover::before { transform: scaleY(1); }
.chip-btn:active { transform: scale(0.99); }

.chip-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--c-white);
}
.chip-sub {
  display: block;
  font-size: 11px;
  color: var(--c-silver);
  margin-top: 2px;
}

/* Submit status */
.submit-status {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  font-size: 11px;
  color: var(--c-silver);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.loading-ring-sm {
  width: 16px;
  height: 16px;
  border: 1.5px solid var(--c-border);
  border-top-color: var(--c-red);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* Bubble transition */
.bubble-enter-active { animation: bubbleIn 0.25s ease forwards; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; }
  40%            { transform: scale(1);   opacity: 1;   }
}
</style>
