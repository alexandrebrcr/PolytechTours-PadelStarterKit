<template>
  <div class="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Administration</h1>

      <!-- Tabs -->
      <div class="bg-white shadow rounded-lg mb-8">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex">
            <button
              v-for="tab in tabs"
              :key="tab.name"
              @click="currentTab = tab.name"
              :class="[
                currentTab === tab.name
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm'
              ]"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>
      </div>

      <!-- Content -->
      <div v-if="error" class="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong class="font-bold">Erreur !</strong>
        <span class="block sm:inline">{{ error }}</span>
        <span class="absolute top-0 bottom-0 right-0 px-4 py-3" @click="error = null">
          <svg class="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/></svg>
        </span>
      </div>

      <div class="bg-white shadow rounded-lg p-6">
        
        <!-- Gestion des Joueurs -->
        <div v-if="currentTab === 'players'">
          <div class="flex justify-between mb-4">
            <h2 class="text-xl font-semibold">Joueurs</h2>
            <button @click="openPlayerModal()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Ajouter un joueur
            </button>
          </div>

          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entreprise</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Licence</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compte</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="player in players" :key="player.id">
                <td class="px-6 py-4 whitespace-nowrap">{{ player.firstname }} {{ player.lastname }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ player.company }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ player.license_number }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span v-if="player.user_role" :class="player.user_role === 'ADMINISTRATEUR' ? 'text-red-600 font-bold' : 'text-green-600'">
                    {{ player.user_role }}
                  </span>
                  <span v-else class="text-gray-400">Aucun</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button @click="openPlayerModal(player)" class="text-indigo-600 hover:text-indigo-900">Modifier</button>
                  <button @click="deletePlayer(player.id)" class="text-red-600 hover:text-red-900">Supprimer</button>
                  <button v-if="!player.user_role" @click="createAccount(player.id)" class="text-green-600 hover:text-green-900">Créer compte</button>
                  <button v-if="player.user_role === 'JOUEUR'" @click="changeRole(player.id, 'ADMINISTRATEUR')" class="text-purple-600 hover:text-purple-900">Promouvoir Admin</button>
                  <button v-if="player.user_role === 'ADMINISTRATEUR'" @click="changeRole(player.id, 'JOUEUR')" class="text-orange-600 hover:text-orange-900">Rétrograder</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Gestion des Équipes -->
        <div v-if="currentTab === 'teams'">
          <div class="flex justify-between mb-4">
            <h2 class="text-xl font-semibold">Équipes</h2>
            <button @click="openTeamModal()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Créer une équipe
            </button>
          </div>
          
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom d'équipe</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joueurs</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Poule</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="team in teams" :key="team.id">
                <td class="px-6 py-4 whitespace-nowrap">{{ team.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div v-for="p in team.players" :key="p.id">{{ p.firstname }} {{ p.lastname }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">{{ team.pool_id ? 'Oui' : 'Non' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button @click="deleteTeam(team.id)" class="text-red-600 hover:text-red-900">Supprimer</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Gestion des Poules -->
        <div v-if="currentTab === 'pools'">
          <div class="flex justify-between mb-4">
            <h2 class="text-xl font-semibold">Poules</h2>
            <button @click="openPoolModal()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Créer une poule
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="pool in pools" :key="pool.id" class="border rounded-lg p-4">
              <h3 class="font-bold text-lg mb-2">{{ pool.name }}</h3>
              <ul class="list-disc list-inside text-sm text-gray-600">
                <li v-for="team in pool.teams" :key="team.id">
                  {{ team.name }}
                </li>
              </ul>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Modals -->
    <!-- Player Modal -->
    <div v-if="showPlayerModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
      <div class="bg-white rounded-lg p-8 max-w-md w-full">
        <h3 class="text-lg font-medium mb-4">{{ editingPlayer ? 'Modifier' : 'Ajouter' }} un joueur</h3>
        <form @submit.prevent="savePlayer" class="space-y-4">
          <input v-model="playerForm.firstname" placeholder="Prénom" class="w-full border rounded p-2" required pattern="[a-zA-Z\s\-_']+" title="Lettres, espaces, tirets, underscores et apostrophes">
          <input v-model="playerForm.lastname" placeholder="Nom" class="w-full border rounded p-2" required pattern="[a-zA-Z\s\-_\.']+" title="Lettres, espaces, tirets, underscores, points et apostrophes">
          <input v-model="playerForm.company" placeholder="Entreprise" class="w-full border rounded p-2" required>
          <input v-model="playerForm.email" type="email" placeholder="Email" class="w-full border rounded p-2" required :disabled="!!editingPlayer">
          <input v-model="playerForm.license_number" placeholder="N° Licence (LXXXXXX)" class="w-full border rounded p-2" required pattern="L\d{6}" :disabled="!!editingPlayer">
          
          <div class="flex justify-end space-x-2">
            <button type="button" @click="showPlayerModal = false" class="px-4 py-2 border rounded">Annuler</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Team Modal -->
    <div v-if="showTeamModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
      <div class="bg-white rounded-lg p-8 max-w-md w-full">
        <h3 class="text-lg font-medium mb-4">Créer une équipe</h3>
        <form @submit.prevent="saveTeam" class="space-y-4">
          <input v-model="teamForm.name" placeholder="Nom d'équipe" class="w-full border rounded p-2" required>
          
          <select v-model="teamForm.player1_id" class="w-full border rounded p-2" required @change="teamForm.player2_id = ''">
            <option value="">Sélectionner Joueur 1</option>
            <option v-for="p in availablePlayers" :key="p.id" :value="p.id">
              {{ p.firstname }} {{ p.lastname }} ({{ p.company }})
            </option>
          </select>

          <select v-model="teamForm.player2_id" class="w-full border rounded p-2" required :disabled="!teamForm.player1_id">
            <option value="">Sélectionner Joueur 2 (Même entreprise)</option>
            <option v-for="p in availablePlayersForTeam2" :key="p.id" :value="p.id">
              {{ p.firstname }} {{ p.lastname }} ({{ p.company }})
            </option>
          </select>

          <div class="flex justify-end space-x-2">
            <button type="button" @click="showTeamModal = false" class="px-4 py-2 border rounded">Annuler</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded">Créer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Pool Modal -->
    <div v-if="showPoolModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
      <div class="bg-white rounded-lg p-8 max-w-lg w-full">
        <h3 class="text-lg font-medium mb-4">Créer une poule</h3>
        <form @submit.prevent="savePool" class="space-y-4">
          <input v-model="poolForm.name" placeholder="Nom de la poule" class="w-full border rounded p-2" required>
          
          <div class="space-y-2 max-h-60 overflow-y-auto">
            <p class="text-sm text-gray-500">Sélectionnez exactement 6 équipes : {{ selectedTeams.length }}/6</p>
            <div v-for="team in availableTeams" :key="team.id" class="flex items-center">
              <input type="checkbox" :value="team.id" v-model="selectedTeams" :disabled="selectedTeams.length >= 6 && !selectedTeams.includes(team.id)">
              <span class="ml-2">{{ team.name }}</span>
            </div>
          </div>

          <div class="flex justify-end space-x-2">
            <button type="button" @click="showPoolModal = false" class="px-4 py-2 border rounded">Annuler</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded" :disabled="selectedTeams.length !== 6">Créer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Account Created Modal -->
    <div v-if="newAccount" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
      <div class="bg-white rounded-lg p-8 max-w-md w-full text-center">
        <h3 class="text-lg font-bold text-green-600 mb-4">Compte créé avec succès !</h3>
        <p class="mb-2">Email : <strong>{{ newAccount.email }}</strong></p>
        <p class="mb-4">Mot de passe temporaire : <strong class="bg-yellow-100 p-1">{{ newAccount.temp_password }}</strong></p>
        <p class="text-sm text-red-500 mb-6">Notez ce mot de passe, il ne sera plus affiché.</p>
        <button @click="newAccount = null" class="px-4 py-2 bg-blue-600 text-white rounded">Fermer</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const router = useRouter()
const authStore = useAuthStore()

const error = ref(null)
const currentTab = ref('players')
const tabs = [
  { name: 'players', label: 'Joueurs' },
  { name: 'teams', label: 'Équipes' },
  { name: 'pools', label: 'Poules' }
]

const players = ref([])
const teams = ref([])
const pools = ref([])

// Modals state
const showPlayerModal = ref(false)
const showTeamModal = ref(false)
const showPoolModal = ref(false)
const newAccount = ref(null)

// Forms
const editingPlayer = ref(null)
const playerForm = ref({ firstname: '', lastname: '', company: '', email: '', license_number: '' })
const teamForm = ref({ name: '', player1_id: '', player2_id: '' })
const poolForm = ref({ name: '' })
const selectedTeams = ref([])

// Computed
const availablePlayers = computed(() => players.value.filter(p => !p.team_id))
const availablePlayersForTeam2 = computed(() => {
  if (!teamForm.value.player1_id) return []
  const p1 = players.value.find(p => p.id === teamForm.value.player1_id)
  if (!p1) return []
  return availablePlayers.value.filter(p => p.company === p1.company && p.id !== p1.id)
})
const availableTeams = computed(() => teams.value.filter(t => !t.pool_id))

onMounted(() => {
  loadData()
})

async function loadData() {
  try {
    const [pRes, tRes, poolRes] = await Promise.all([
      api.get('/admin/players'),
      api.get('/admin/teams'),
      api.get('/admin/pools')
    ])
    players.value = pRes.data
    teams.value = tRes.data
    pools.value = poolRes.data
  } catch (err) {
    console.error('Erreur chargement données', err)
  }
}

// Players
function openPlayerModal(player = null) {
  editingPlayer.value = player
  if (player) {
    playerForm.value = { ...player }
  } else {
    playerForm.value = { firstname: '', lastname: '', company: '', email: '', license_number: '' }
  }
  showPlayerModal.value = true
}

async function savePlayer() {
  try {
    if (editingPlayer.value) {
      await api.put(`/admin/players/${editingPlayer.value.id}`, playerForm.value)
    } else {
      await api.post('/admin/players', playerForm.value)
    }
    showPlayerModal.value = false
    loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur')
  }
}

async function deletePlayer(id) {
  const player = players.value.find(p => p.id === id)
  if (player && authStore.user && player.email === authStore.user.email) {
    alert("Impossible de supprimer votre propre compte")
    return
  }

  if (!confirm("Attention, cette action est irréversible")) return
  try {
    await api.delete(`/admin/players/${id}`)
    loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur')
  }
}

async function createAccount(playerId) {
  try {
    const res = await api.post('/admin/accounts', { player_id: playerId })
    newAccount.value = res.data
    loadData() // Recharger pour voir le nouveau statut
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur')
  }
}

async function changeRole(playerId, newRole) {
  if (!confirm(`Voulez-vous vraiment changer le rôle en ${newRole} ?`)) return
  try {
    await api.put(`/admin/players/${playerId}/role`, { role: newRole })
    
    // Gestion de l'auto-rétrogradation
    if (authStore.user?.player_id === playerId && newRole !== 'ADMINISTRATEUR') {
      alert("Vous avez modifié votre propre rôle. Vous n'avez plus accès à cette page.")
      
      // Mettre à jour le store et le localStorage
      const updatedUser = { ...authStore.user, role: newRole }
      authStore.user = updatedUser
      localStorage.setItem('user', JSON.stringify(updatedUser))
      
      router.push('/')
      return
    }

    loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur')
  }
}

// Teams
function openTeamModal() {
  teamForm.value = { name: '', player1_id: '', player2_id: '' }
  showTeamModal.value = true
}

async function saveTeam() {
  error.value = null
  try {
    await api.post('/admin/teams', teamForm.value)
    showTeamModal.value = false
    loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur')
  }
}

async function deleteTeam(id) {
  if (!confirm("Supprimer cette équipe ?")) return
  error.value = null
  try {
    await api.delete(`/admin/teams/${id}`)
    loadData()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur'
  }
}

// Pools
function openPoolModal() {
  poolForm.value = { name: '' }
  selectedTeams.value = []
  showPoolModal.value = true
}

async function savePool() {
  try {
    await api.post('/admin/pools', {
      name: poolForm.value.name,
      team_ids: selectedTeams.value
    })
    showPoolModal.value = false
    loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Erreur')
  }
}
</script>