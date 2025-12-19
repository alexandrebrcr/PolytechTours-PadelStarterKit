<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Planning</h1>
      <button 
        v-if="authStore.isAdmin"
        @click="openCreateModal(null)"
        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Ajouter un événement
      </button>
    </div>

    <!-- Calendar Controls -->
    <div class="flex justify-between items-center mb-4 bg-white p-4 rounded-lg shadow">
      <button @click="changeMonth(-1)" class="p-2 hover:bg-gray-100 rounded font-medium text-gray-600">&lt; Précédent</button>
      <h2 class="text-xl font-bold text-gray-800 capitalize">{{ currentMonthName }} {{ currentYear }}</h2>
      <button @click="changeMonth(1)" class="p-2 hover:bg-gray-100 rounded font-medium text-gray-600">Suivant &gt;</button>
    </div>

    <!-- Calendar Grid -->
    <div class="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <div class="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
        <div v-for="day in weekDays" :key="day" class="py-3 text-center font-semibold text-gray-600 text-sm uppercase tracking-wider">
          {{ day }}
        </div>
      </div>
      <div class="grid grid-cols-7 auto-rows-fr">
        <div 
          v-for="(day, index) in calendarDays" 
          :key="index"
          class="min-h-[120px] border-b border-r border-gray-100 p-2 relative hover:bg-gray-50 transition-colors cursor-pointer"
          :class="{'bg-gray-50/50 text-gray-400': !day.isCurrentMonth}"
          @click="selectDay(day)"
        >
          <div class="flex justify-between items-start">
            <span 
              class="font-medium text-sm w-7 h-7 flex items-center justify-center rounded-full"
              :class="isToday(day.date) ? 'bg-blue-600 text-white' : ''"
            >
              {{ day.dayNumber }}
            </span>
          </div>
          
          <!-- Events List -->
          <div class="mt-2 space-y-1">
            <div 
              v-for="event in day.events" 
              :key="event.id"
              class="text-xs p-1.5 rounded bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors truncate border-l-2 border-blue-500"
              @click.stop="openEventDetails(event)"
            >
              <span class="font-bold">{{ event.start_time.substring(0, 5) }}</span>
              <span class="ml-1">{{ event.matches.length }} match(s)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Details Modal -->
    <div v-if="selectedEvent" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-start mb-6">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Détails de l'événement</h2>
            <p class="text-gray-600 mt-1">
              {{ formatDate(selectedEvent.date) }} à {{ selectedEvent.start_time.substring(0, 5) }}
            </p>
          </div>
          <button @click="selectedEvent = null" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div class="space-y-6">
          <div v-for="(match, idx) in selectedEvent.matches" :key="match.id" class="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div class="flex justify-between items-center mb-3">
              <h3 class="font-bold text-gray-700">Match {{ idx + 1 }} - Piste {{ match.court_number }}</h3>
              <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="getStatusClass(match.status)">
                {{ formatStatus(match.status) }}
              </span>
            </div>
            
            <div class="flex justify-between items-center">
              <div class="text-center flex-1">
                <div class="font-bold text-lg">{{ match.team1.company }}</div>
                <div class="text-sm text-gray-500">
                  <div v-for="p in match.team1.players" :key="p.id">{{ p.firstname }} {{ p.lastname }}</div>
                </div>
              </div>
              <div class="text-gray-400 font-bold px-4">VS</div>
              <div class="text-center flex-1">
                <div class="font-bold text-lg">{{ match.team2.company }}</div>
                <div class="text-sm text-gray-500">
                  <div v-for="p in match.team2.players" :key="p.id">{{ p.firstname }} {{ p.lastname }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="authStore.isAdmin" class="mt-8 flex justify-end pt-4 border-t">
          <button 
            @click="deleteEvent(selectedEvent)"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            Supprimer l'événement
          </button>
        </div>
      </div>
    </div>

    <!-- Create Event Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-6">Ajouter un événement</h2>
        
        <form @submit.prevent="submitCreateForm" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <input type="date" v-model="createForm.date" required class="w-full border rounded p-2" :min="todayStr">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Heure</label>
              <input type="time" v-model="createForm.start_time" required class="w-full border rounded p-2">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de matchs</label>
              <select v-model.number="matchCount" class="w-full border rounded p-2">
                <option :value="1">1 Match</option>
                <option :value="2">2 Matchs</option>
                <option :value="3">3 Matchs</option>
              </select>
            </div>
          </div>

          <div class="space-y-4">
            <div v-for="(match, idx) in createForm.matches" :key="idx" class="bg-gray-50 p-4 rounded border">
              <h3 class="font-bold text-gray-700 mb-3">Match {{ idx + 1 }}</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Piste</label>
                  <select v-model.number="match.court_number" required class="w-full border rounded p-2 text-sm">
                    <option v-for="n in 10" :key="n" :value="n">Piste {{ n }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Équipe 1</label>
                  <select v-model.number="match.team1_id" required class="w-full border rounded p-2 text-sm">
                    <option value="">Sélectionner...</option>
                    <option v-for="team in teams" :key="team.id" :value="team.id" :disabled="isTeamSelected(team.id, idx)">
                      {{ team.name }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-500 mb-1">Équipe 2</label>
                  <select v-model.number="match.team2_id" required class="w-full border rounded p-2 text-sm">
                    <option value="">Sélectionner...</option>
                    <option v-for="team in teams" :key="team.id" :value="team.id" :disabled="isTeamSelected(team.id, idx)">
                      {{ team.name }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div v-if="createError" class="text-red-600 text-sm bg-red-50 p-3 rounded">
            {{ createError }}
          </div>

          <div class="flex justify-end space-x-3 pt-4 border-t">
            <button type="button" @click="showCreateModal = false" class="px-4 py-2 border rounded text-gray-700 hover:bg-gray-50">Annuler</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" :disabled="submitting">
              {{ submitting ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { planningAPI, authAPI } from '../services/api'

const authStore = useAuthStore()
const currentDate = ref(new Date())
const events = ref([])
const teams = ref([])
const loading = ref(false)

// Modal states
const selectedEvent = ref(null)
const showCreateModal = ref(false)
const createError = ref(null)
const submitting = ref(false)

// Helper for local YYYY-MM-DD
function toISODateLocal(d) {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Create Form
const todayStr = toISODateLocal(new Date())
const matchCount = ref(1)
const createForm = ref({
  date: todayStr,
  start_time: '19:00',
  matches: [{ court_number: 1, team1_id: '', team2_id: '' }]
})

// Calendar Logic
const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

const currentMonthName = computed(() => {
  return new Intl.DateTimeFormat('fr-FR', { month: 'long' }).format(currentDate.value)
})

const currentYear = computed(() => currentDate.value.getFullYear())

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  
  // 0 = Dimanche, 1 = Lundi... on veut Lundi = 0
  let startDay = firstDayOfMonth.getDay() - 1
  if (startDay === -1) startDay = 6
  
  const days = []
  
  // Previous month days
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    const d = new Date(year, month - 1, prevMonthLastDay - i)
    days.push({
      date: d,
      dayNumber: d.getDate(),
      isCurrentMonth: false,
      events: getEventsForDate(d)
    })
  }
  
  // Current month days
  for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
    const d = new Date(year, month, i)
    days.push({
      date: d,
      dayNumber: i,
      isCurrentMonth: true,
      events: getEventsForDate(d)
    })
  }
  
  // Next month days to fill grid (42 cells total usually covers all months)
  const remainingCells = 42 - days.length
  for (let i = 1; i <= remainingCells; i++) {
    const d = new Date(year, month + 1, i)
    days.push({
      date: d,
      dayNumber: i,
      isCurrentMonth: false,
      events: getEventsForDate(d)
    })
  }
  
  return days
})

// Methods
function changeMonth(delta) {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + delta, 1)
  fetchEvents()
}

function isToday(date) {
  const today = new Date()
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
}

function formatDate(dateStr) {
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'full' }).format(new Date(dateStr))
}

function formatStatus(status) {
  const map = { 'A_VENIR': 'À venir', 'TERMINE': 'Terminé', 'ANNULE': 'Annulé' }
  return map[status] || status
}

function getStatusClass(status) {
  const map = {
    'A_VENIR': 'bg-blue-100 text-blue-800',
    'TERMINE': 'bg-green-100 text-green-800',
    'ANNULE': 'bg-red-100 text-red-800'
  }
  return map[status] || 'bg-gray-100'
}

function getEventsForDate(date) {
  const dateStr = toISODateLocal(date)
  return events.value.filter(e => e.date === dateStr)
}

function selectDay(day) {
  if (day.events.length > 0) {
    // If multiple events, maybe show a list? For now just pick first or show modal logic
    // Requirement: "Clic sur un jour affiche les événements de cette date"
    // If we have events, we can show them.
    // But wait, the UI shows small badges.
    // Let's say clicking a day with events opens a modal with all events of that day?
    // Or clicking an event badge opens that event.
    // I implemented click.stop on event badge.
    // Clicking the day cell could create an event on that day if admin?
    if (authStore.isAdmin) {
      openCreateModal(day.date)
    }
  }
}

function openEventDetails(event) {
  selectedEvent.value = event
}

// API Calls
async function fetchEvents() {
  loading.value = true
  try {
    // Calculate start/end of view
    // Actually the API defaults are good enough (current month + next)
    // But if we navigate far, we should pass params.
    // For simplicity, let's rely on API default or pass current month range.
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    const start = toISODateLocal(new Date(year, month - 1, 1))
    const end = toISODateLocal(new Date(year, month + 2, 0))
    
    const res = await planningAPI.getEvents({ start_date: start, end_date: end })
    events.value = res.data
  } catch (err) {
    console.error('Erreur chargement planning', err)
  } finally {
    loading.value = false
  }
}

async function fetchTeams() {
  if (teams.value.length === 0 && authStore.isAdmin) {
    try {
      const res = await authAPI.getTeams()
      teams.value = res.data
    } catch (err) {
      console.error('Erreur chargement équipes', err)
    }
  }
}

// Create Event Logic
function openCreateModal(date = null) {
  createError.value = null
  // Ensure date is a Date object if passed (it might be a MouseEvent if not careful, but we fixed the template)
  // But to be safe against other calls:
  const targetDate = (date instanceof Date) ? date : new Date()
  
  createForm.value = {
    date: toISODateLocal(targetDate),
    start_time: '19:00',
    matches: Array(matchCount.value).fill().map((_, i) => ({ court_number: i + 1, team1_id: '', team2_id: '' }))
  }
  showCreateModal.value = true
  fetchTeams()
}

watch(matchCount, (newCount) => {
  const currentMatches = createForm.value.matches
  if (newCount > currentMatches.length) {
    for (let i = currentMatches.length; i < newCount; i++) {
      currentMatches.push({ court_number: i + 1, team1_id: '', team2_id: '' })
    }
  } else {
    createForm.value.matches = currentMatches.slice(0, newCount)
  }
})

function isTeamSelected(teamId, currentMatchIdx) {
  if (!teamId) return false
  // Check if team is used in other matches of the form
  for (let i = 0; i < createForm.value.matches.length; i++) {
    if (i === currentMatchIdx) {
      // In current match, check if it's the OTHER team
      const m = createForm.value.matches[i]
      if (m.team1_id === teamId && m.team2_id === teamId) return true // Should not happen due to select logic but...
      continue
    }
    const m = createForm.value.matches[i]
    if (m.team1_id === teamId || m.team2_id === teamId) return true
  }
  return false
}

async function submitCreateForm() {
  submitting.value = true
  createError.value = null
  try {
    // Basic validation
    const matches = createForm.value.matches
    for (const m of matches) {
      if (m.team1_id === m.team2_id) throw new Error("Une équipe ne peut pas jouer contre elle-même")
    }
    
    await planningAPI.createEvent(createForm.value)
    showCreateModal.value = false
    fetchEvents()
  } catch (err) {
    createError.value = err.response?.data?.detail || err.message || 'Erreur'
  } finally {
    submitting.value = false
  }
}

async function deleteEvent(event) {
  if (!confirm("Supprimer cet événement ?")) return
  try {
    await planningAPI.deleteEvent(event.id)
    selectedEvent.value = null
    fetchEvents()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur')
  }
}

onMounted(() => {
  fetchEvents()
})
</script>
