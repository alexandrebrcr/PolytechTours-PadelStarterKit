<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Résultats & Classement</h1>

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-8">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="currentTab = 'history'"
          :class="[
            currentTab === 'history'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Mes Résultats
        </button>
        <button
          @click="currentTab = 'ranking'"
          :class="[
            currentTab === 'ranking'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Classement Général
        </button>
      </nav>
    </div>

    <!-- Content -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
    </div>

    <div v-else>
      <!-- History Tab -->
      <div v-if="currentTab === 'history'" class="space-y-4">
        <div v-if="history.length === 0" class="text-center py-8 text-gray-500">
          Aucun match terminé.
        </div>
        
        <div 
          v-for="match in history" 
          :key="match.id"
          class="bg-white p-6 rounded-lg shadow-md border-l-4"
          :class="isVictory(match) ? 'border-green-500' : 'border-red-500'"
        >
          <div class="flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="text-gray-600 font-medium">
              {{ formatDate(match.date) }}
            </div>
            
            <div class="flex-1 text-center">
              <div class="text-lg font-bold">
                <span :class="isMyTeam(match.team1) ? 'text-blue-600' : 'text-gray-900'">
                  {{ match.team1.company }}
                </span>
                <span class="mx-2 text-gray-400">vs</span>
                <span :class="isMyTeam(match.team2) ? 'text-blue-600' : 'text-gray-900'">
                  {{ match.team2.company }}
                </span>
              </div>
              <div class="text-sm text-gray-500 mt-1">
                Adversaires : {{ getOpponents(match) }}
              </div>
            </div>

            <div class="text-xl font-bold" :class="isVictory(match) ? 'text-green-600' : 'text-red-600'">
              {{ formatScore(match) }}
            </div>
            
            <div class="text-gray-500 text-sm">
              Piste {{ match.court_number }}
            </div>
          </div>
        </div>
      </div>

      <!-- Ranking Tab -->
      <div v-if="currentTab === 'ranking'" class="overflow-x-auto">
        <table class="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pos</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entreprise</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Joués</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">V</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">D</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Sets +/-</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="row in ranking" :key="row.company" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap font-bold text-gray-900">
                {{ row.position }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-900">
                {{ row.company }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-gray-500">
                {{ row.matches_played }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-green-600 font-medium">
                {{ row.wins }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-red-600 font-medium">
                {{ row.losses }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-gray-500">
                {{ row.sets_won - row.sets_lost }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center font-bold text-blue-600 text-lg">
                {{ row.points }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { matchesAPI, resultsAPI } from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const currentTab = ref('history')
const loading = ref(false)
const history = ref([])
const ranking = ref([])

const fetchHistory = async () => {
  loading.value = true
  try {
    // On récupère tous les matchs terminés
    // Le backend filtre déjà pour le joueur connecté si non-admin
    // Mais pour l'historique perso, on veut voir ses matchs.
    // Si admin, il verra tout, mais l'onglet s'appelle "Mes Résultats"...
    // Pour l'instant on utilise le endpoint matches avec status=TERMINE
    const response = await matchesAPI.getMatches({
      status: 'TERMINE',
      start_date: '2024-01-01', // Depuis le début de l'année/saison
      end_date: '2025-12-31'
    })
    // Tri par date décroissante
    history.value = response.data.sort((a, b) => new Date(b.date) - new Date(a.date))
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const fetchRanking = async () => {
  loading.value = true
  try {
    const response = await resultsAPI.getRanking()
    ranking.value = response.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (currentTab.value === 'history') fetchHistory()
  else fetchRanking()
})

watch(currentTab, (newTab) => {
  if (newTab === 'history') fetchHistory()
  else fetchRanking()
})

// Helpers
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

const isMyTeam = (team) => {
  // On suppose que l'utilisateur a un player_id et que le player a un team_id
  // Mais ici on a juste l'objet team.
  // On peut comparer le nom de l'entreprise si on l'a dans le store
  // Ou mieux, on regarde si l'utilisateur est dans la liste des joueurs de l'équipe
  if (!authStore.user?.player_id) return false
  return team.players.some(p => p.id === authStore.user.player_id)
}

const isVictory = (match) => {
  // Déterminer le vainqueur à partir du score
  // score_team1 format "6-4, 6-3"
  if (!match.score_team1) return false
  
  const sets = match.score_team1.split(", ")
  let t1_sets = 0
  let t2_sets = 0
  
  sets.forEach(s => {
    const [g1, g2] = s.split("-").map(Number)
    if (g1 > g2) t1_sets++
    else t2_sets++
  })
  
  const myTeamIsTeam1 = isMyTeam(match.team1)
  const myTeamIsTeam2 = isMyTeam(match.team2)
  
  if (myTeamIsTeam1) return t1_sets > t2_sets
  if (myTeamIsTeam2) return t2_sets > t1_sets
  
  return false // Si spectateur (admin)
}

const getOpponents = (match) => {
  const myTeamIsTeam1 = isMyTeam(match.team1)
  const opponents = myTeamIsTeam1 ? match.team2 : match.team1
  
  return opponents.players
    .map(p => `${p.firstname} ${p.lastname}`)
    .join(' & ') + ` (${opponents.company})`
}

const formatScore = (match) => {
  return match.score_team1
}
</script>
