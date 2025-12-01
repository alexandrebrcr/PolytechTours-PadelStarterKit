<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Matchs</h1>
      <button 
        v-if="authStore.isAdmin"
        @click="openCreateModal"
        class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Ajouter un match
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-6 rounded-lg shadow-md mb-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Date Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Du</label>
          <input 
            type="date" 
            v-model="filters.start_date"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Au</label>
          <input 
            type="date" 
            v-model="filters.end_date"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
        </div>

        <!-- Admin Filters -->
        <template v-if="authStore.isAdmin">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Entreprise</label>
            <input 
              type="text" 
              v-model="filters.company"
              placeholder="Rechercher..."
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Statut</label>
            <select 
              v-model="filters.status"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Tous</option>
              <option value="A_VENIR">À venir</option>
              <option value="TERMINE">Terminé</option>
              <option value="ANNULE">Annulé</option>
            </select>
          </div>
        </template>

        <!-- Player Filters -->
        <div v-else class="flex items-end pb-2">
          <label class="inline-flex items-center">
            <input 
              type="checkbox" 
              v-model="filters.all_matches"
              class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
            <span class="ml-2 text-gray-700">Voir tous les matchs</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Matches List -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
    </div>

    <div v-else-if="matches.length === 0" class="text-center py-8 text-gray-500">
      Aucun match trouvé pour cette période.
    </div>

    <div v-else class="space-y-4">
      <div 
        v-for="match in matches" 
        :key="match.id" 
        class="bg-white p-6 rounded-lg shadow-md border-l-4"
        :class="{
          'border-blue-500': match.status === 'A_VENIR',
          'border-green-500': match.status === 'TERMINE',
          'border-red-500': match.status === 'ANNULE'
        }"
      >
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <!-- Date & Court -->
          <div class="min-w-[200px]">
            <div class="text-lg font-semibold text-gray-900">
              {{ formatDate(match.date, match.time) }}
            </div>
            <div class="text-gray-600">
              Piste {{ match.court_number }}
            </div>
            <div class="mt-2">
              <span 
                class="px-2 py-1 text-xs font-semibold rounded-full"
                :class="{
                  'bg-blue-100 text-blue-800': match.status === 'A_VENIR',
                  'bg-green-100 text-green-800': match.status === 'TERMINE',
                  'bg-red-100 text-red-800': match.status === 'ANNULE'
                }"
              >
                {{ formatStatus(match.status) }}
              </span>
            </div>
          </div>

          <!-- Teams -->
          <div class="flex-1 w-full md:w-auto">
            <div class="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8">
              <!-- Team 1 -->
              <div class="text-center flex-1">
                <div class="font-bold text-lg">{{ match.team1.company }}</div>
                <div class="text-sm text-gray-600">
                  <div v-for="player in match.team1.players" :key="player.id">
                    {{ player.firstname }} {{ player.lastname }}
                  </div>
                </div>
                <div v-if="match.status === 'TERMINE'" class="text-2xl font-bold mt-2 text-blue-600">
                  {{ match.score_team1 }}
                </div>
              </div>

              <div class="text-gray-400 font-bold text-xl">VS</div>

              <!-- Team 2 -->
              <div class="text-center flex-1">
                <div class="font-bold text-lg">{{ match.team2.company }}</div>
                <div class="text-sm text-gray-600">
                  <div v-for="player in match.team2.players" :key="player.id">
                    {{ player.firstname }} {{ player.lastname }}
                  </div>
                </div>
                <div v-if="match.status === 'TERMINE'" class="text-2xl font-bold mt-2 text-blue-600">
                  {{ match.score_team2 }}
                </div>
              </div>
            </div>
          </div>

          <!-- Admin Actions -->
          <div v-if="authStore.isAdmin" class="flex gap-2 w-full md:w-auto justify-end">
            <button 
              @click="openEditModal(match)"
              class="text-gray-600 hover:text-blue-600 p-2"
              title="Modifier"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
            </button>
            <button 
              v-if="match.status === 'A_VENIR'"
              @click="confirmDelete(match)"
              class="text-gray-600 hover:text-red-600 p-2"
              title="Supprimer"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-6">
          {{ isEditing ? 'Modifier le match' : 'Ajouter un match' }}
        </h2>

        <form @submit.prevent="submitForm" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Date</label>
              <input 
                type="date" 
                v-model="form.date"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                :disabled="isEditing && form.status !== 'A_VENIR'"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Heure</label>
              <input 
                type="time" 
                v-model="form.time"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                :disabled="isEditing && form.status !== 'A_VENIR'"
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">Piste (1-10)</label>
            <input 
              type="number" 
              v-model="form.court_number"
              min="1"
              max="10"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              :disabled="isEditing && form.status !== 'A_VENIR'"
            >
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Équipe 1</label>
              <select 
                v-model="form.team1_id"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                :disabled="isEditing"
              >
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.company }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Équipe 2</label>
              <select 
                v-model="form.team2_id"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                :disabled="isEditing"
              >
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.company }}
                </option>
              </select>
            </div>
          </div>

          <div v-if="isEditing">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700">Statut</label>
              <select 
                v-model="form.status"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="A_VENIR">À venir</option>
                <option value="TERMINE">Terminé</option>
                <option value="ANNULE">Annulé</option>
              </select>
            </div>

            <div v-if="form.status === 'TERMINE'" class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Score Équipe 1</label>
                <input 
                  type="text" 
                  v-model="form.score_team1"
                  placeholder="ex: 6-4 6-2"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Score Équipe 2</label>
                <input 
                  type="text" 
                  v-model="form.score_team2"
                  placeholder="ex: 4-6 2-6"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
              </div>
            </div>
          </div>

          <div v-if="error" class="text-red-600 text-sm mt-2">
            {{ error }}
          </div>

          <div class="flex justify-end gap-4 mt-6">
            <button 
              type="button" 
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
            <button 
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              :disabled="submitting"
            >
              {{ submitting ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { matchesAPI, authAPI } from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const matches = ref([])
const teams = ref([])
const loading = ref(false)
const error = ref(null)
const submitting = ref(false)

// Filters
const filters = ref({
  start_date: new Date().toISOString().split('T')[0],
  end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  all_matches: false,
  company: '',
  status: ''
})

// Modal state
const showModal = ref(false)
const isEditing = ref(false)
const currentMatchId = ref(null)
const form = ref({
  date: '',
  time: '',
  court_number: 1,
  team1_id: '',
  team2_id: '',
  status: 'A_VENIR',
  score_team1: '',
  score_team2: ''
})

// Fetch matches
const fetchMatches = async () => {
  loading.value = true
  try {
    const params = { ...filters.value }
    // Clean empty params
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) delete params[key]
    })
    
    const response = await matchesAPI.getMatches(params)
    matches.value = response.data
  } catch (err) {
    console.error('Erreur chargement matchs:', err)
  } finally {
    loading.value = false
  }
}

// Fetch teams (for admin)
const fetchTeams = async () => {
  if (authStore.isAdmin && teams.value.length === 0) {
    try {
      const response = await authAPI.getTeams()
      teams.value = response.data
    } catch (err) {
      console.error('Erreur chargement équipes:', err)
    }
  }
}

// Watch filters
watch(filters, () => {
  fetchMatches()
}, { deep: true })

onMounted(() => {
  fetchMatches()
  fetchTeams()
})

// Formatters
const formatDate = (dateStr, timeStr) => {
  const date = new Date(`${dateStr}T${timeStr}`)
  return new Intl.DateTimeFormat('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const formatStatus = (status) => {
  const map = {
    'A_VENIR': 'À venir',
    'TERMINE': 'Terminé',
    'ANNULE': 'Annulé'
  }
  return map[status] || status
}

// Actions
const openCreateModal = () => {
  isEditing.value = false
  currentMatchId.value = null
  form.value = {
    date: filters.value.start_date,
    time: '19:00',
    court_number: 1,
    team1_id: '',
    team2_id: '',
    status: 'A_VENIR',
    score_team1: '',
    score_team2: ''
  }
  error.value = null
  showModal.value = true
  fetchTeams()
}

const openEditModal = (match) => {
  isEditing.value = true
  currentMatchId.value = match.id
  form.value = {
    date: match.date,
    time: match.time.substring(0, 5), // HH:MM:SS -> HH:MM
    court_number: match.court_number,
    team1_id: match.team1.id,
    team2_id: match.team2.id,
    status: match.status,
    score_team1: match.score_team1 || '',
    score_team2: match.score_team2 || ''
  }
  error.value = null
  showModal.value = true
  fetchTeams()
}

const closeModal = () => {
  showModal.value = false
}

const submitForm = async () => {
  submitting.value = true
  error.value = null
  
  try {
    if (form.value.team1_id === form.value.team2_id) {
      throw new Error("Les deux équipes doivent être différentes")
    }

    // On crée une copie des données du formulaire
    const payload = { ...form.value }

    if (isEditing.value) {
      // Si on est en mode édition, l'API (Pydantic) semble rejeter la date/heure 
      // si elles sont renvoyées alors qu'elles ne changent pas (erreur "none_required").
      // On supprime ces champs du payload pour ne pas bloquer la requête.
      delete payload.date
      delete payload.time
      delete payload.court_number
      delete payload.team1_id
      delete payload.team2_id
      
      await matchesAPI.updateMatch(currentMatchId.value, payload)
    } else {
      await matchesAPI.createMatch(payload)
    }
    
    closeModal()
    fetchMatches()
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || err.message || 'Une erreur est survenue'
  } finally {
    submitting.value = false
  }
}

const confirmDelete = async (match) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce match ?')) {
    try {
      await matchesAPI.deleteMatch(match.id)
      fetchMatches()
    } catch (err) {
      alert(err.response?.data?.detail || 'Erreur lors de la suppression')
    }
  }
}
</script>
