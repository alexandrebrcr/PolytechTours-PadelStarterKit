<template>
  <div class="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto space-y-8">
      <!-- Header -->
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center space-x-6">
          <div class="relative">
            <img 
              :src="userAvatar" 
              alt="Profile" 
              class="h-24 w-24 rounded-full object-cover border-4 border-white shadow-lg"
            >
            <button 
              @click="triggerFileInput"
              class="absolute bottom-0 right-0 bg-blue-600 text-white p-1.5 rounded-full hover:bg-blue-700 transition-colors"
              title="Modifier la photo"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
            </button>
            <input 
              type="file" 
              ref="fileInput" 
              class="hidden" 
              accept="image/jpeg,image/png"
              @change="handleFileChange"
            >
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ fullName }}</h1>
            <p class="text-gray-500">{{ authStore.user?.email }}</p>
            <p class="text-sm text-blue-600 mt-1">{{ authStore.user?.role }}</p>
          </div>
        </div>
        <div v-if="authStore.user?.profile_picture" class="mt-4 ml-2">
             <button @click="handleDeleteAvatar" class="text-sm text-red-600 hover:text-red-800">Supprimer la photo</button>
        </div>
      </div>

      <!-- Forms -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
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
                'w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm'
              ]"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Profile Form -->
          <form v-if="currentTab === 'profile'" @submit.prevent="handleUpdateProfile" class="space-y-6" novalidate>
            <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-700">Prénom</label>
                <input 
                  v-model="profileForm.firstname" 
                  type="text" 
                  name="firstname"
                  required
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Nom</label>
                <input 
                  v-model="profileForm.lastname" 
                  type="text" 
                  name="lastname"
                  required
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Email</label>
                <input 
                  v-model="profileForm.email" 
                  type="email" 
                  name="email"
                  required
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Date de naissance</label>
                <input 
                  v-model="profileForm.birthdate" 
                  type="date" 
                  name="birthdate"
                  required
                  :max="maxDate"
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
              </div>
              <div class="sm:col-span-2">
                <label class="block text-sm font-medium text-gray-700">N° de licence</label>
                <input 
                  :value="authStore.user?.license_number || 'Non renseigné'" 
                  disabled
                  class="mt-1 block w-full bg-gray-50 border border-gray-300 rounded-md shadow-sm py-2 px-3 text-gray-500 sm:text-sm"
                >
              </div>
            </div>

            <div class="flex justify-end">
              <button 
                type="submit" 
                :disabled="authStore.loading"
                class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {{ authStore.loading ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
            </div>
          </form>

          <!-- Password Form -->
          <form v-else @submit.prevent="handleChangePassword" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700">Mot de passe actuel</label>
              <input 
                v-model="passwordForm.current" 
                type="password" 
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Nouveau mot de passe</label>
              <input 
                v-model="passwordForm.new" 
                type="password" 
                required
                minlength="12"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
              <p class="mt-1 text-xs text-gray-500">12 caractères min, majuscule, minuscule, chiffre, caractère spécial.</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Confirmer le mot de passe</label>
              <input 
                v-model="passwordForm.confirm" 
                type="password" 
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
            </div>

            <div class="flex justify-end">
              <button 
                type="submit" 
                :disabled="authStore.loading"
                class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {{ authStore.loading ? 'Modification...' : 'Modifier le mot de passe' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- Notifications -->
      <div v-if="message.text" :class="['rounded-md p-4', message.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700']">
        <div class="flex">
          <div class="ml-3">
            <p class="text-sm font-medium whitespace-pre-wrap">{{ message.text }}</p>
          </div>
        </div>
      </div>

    </div>

    <!-- Error Modal -->
    <div v-if="showErrorModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-md w-full text-center">
        <h3 class="text-lg font-bold text-red-600 mb-4">Erreur</h3>
        <p class="mb-6 text-gray-700">{{ errorMessage }}</p>
        <button @click="showErrorModal = false" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Fermer</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const fileInput = ref(null)
const currentTab = ref('profile')
const message = ref({ type: '', text: '' })
const showErrorModal = ref(false)
const errorMessage = ref('')

function showError(msg) {
  errorMessage.value = msg
  showErrorModal.value = true
}

const tabs = [
  { name: 'profile', label: 'Informations personnelles' },
  { name: 'security', label: 'Sécurité' }
]

const profileForm = ref({
  firstname: '',
  lastname: '',
  email: '',
  birthdate: ''
})

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

// Calculer la date max pour avoir 16 ans
const maxDate = computed(() => {
  const date = new Date()
  date.setFullYear(date.getFullYear() - 16)
  return date.toISOString().split('T')[0]
})

const fullName = computed(() => {
  if (authStore.user?.firstname && authStore.user?.lastname) {
    return `${authStore.user.firstname} ${authStore.user.lastname}`
  }
  return authStore.user?.email
})

const userAvatar = computed(() => {
  if (authStore.user?.profile_picture) {
    // Si c'est une URL relative, ajouter le base URL de l'API
    if (authStore.user.profile_picture.startsWith('/')) {
        return `${import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'}${authStore.user.profile_picture}`
    }
    return authStore.user.profile_picture
  }
  return `https://ui-avatars.com/api/?name=${fullName.value}&background=random`
})

onMounted(() => {
  initForm()
})

// Watch for user changes (e.g. after page reload when auth is checked)
watch(() => authStore.user, () => {
  initForm()
}, { deep: true })

function initForm() {
  if (authStore.user) {
    profileForm.value = {
      firstname: authStore.user.firstname || '',
      lastname: authStore.user.lastname || '',
      email: authStore.user.email || '',
      birthdate: authStore.user.birthdate || ''
    }
  }
}

function triggerFileInput() {
  fileInput.value.click()
}

async function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 2 * 1024 * 1024) {
    message.value = { type: 'error', text: 'La taille du fichier ne doit pas dépasser 2MB' }
    return
  }

  const result = await authStore.uploadAvatar(file)
  if (result.success) {
    message.value = { type: 'success', text: 'Photo de profil mise à jour' }
  } else {
    message.value = { type: 'error', text: result.error }
  }
}

async function handleDeleteAvatar() {
    if(!confirm("Voulez-vous vraiment supprimer votre photo de profil ?")) return;
    const result = await authStore.deleteAvatar()
    if (result.success) {
        message.value = { type: 'success', text: 'Photo de profil supprimée' }
    } else {
        message.value = { type: 'error', text: result.error }
    }
}

async function handleUpdateProfile() {
  // Validation manuelle
  const nameRegex = /^[a-zA-Z\s\-_']+$/
  const lastnameRegex = /^[a-zA-Z\s\-_\.']+$/
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  
  if (!nameRegex.test(profileForm.value.firstname)) {
    showError("Le prénom contient des caractères invalides (Lettres, espaces, tirets, underscores, points et apostrophes autorisés)")
    return
  }
  if (profileForm.value.firstname.length < 2 || profileForm.value.firstname.length > 50) {
    showError("Le prénom doit faire entre 2 et 50 caractères")
    return
  }

  if (!lastnameRegex.test(profileForm.value.lastname)) {
    showError("Le nom contient des caractères invalides (Lettres, espaces, tirets, underscores, points et apostrophes autorisés)")
    return
  }
  if (profileForm.value.lastname.length < 2 || profileForm.value.lastname.length > 50) {
    showError("Le nom doit faire entre 2 et 50 caractères")
    return
  }

  if (!emailRegex.test(profileForm.value.email)) {
    showError("Format d'email invalide")
    return
  }

  if (profileForm.value.birthdate) {
    const birthdate = new Date(profileForm.value.birthdate)
    const today = new Date()
    const minAgeDate = new Date()
    minAgeDate.setFullYear(today.getFullYear() - 16)

    // Reset hours for accurate date comparison
    today.setHours(0, 0, 0, 0)
    birthdate.setHours(0, 0, 0, 0)
    minAgeDate.setHours(0, 0, 0, 0)

    if (birthdate > today) {
      showError("Impossible de sélectionner une date future")
      return
    }

    if (birthdate > minAgeDate) {
      showError("L'utilisateur doit avoir au moins 16 ans")
      return
    }
  }

  const result = await authStore.updateProfile(profileForm.value)
  if (result.success) {
    message.value = { type: 'success', text: 'Profil mis à jour avec succès' }
  } else {
    // Backend error (e.g. email already used)
    showError(result.error)
  }
}

async function handleChangePassword() {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    message.value = { type: 'error', text: 'Les mots de passe ne correspondent pas' }
    return
  }

  const result = await authStore.changePassword(
    passwordForm.value.current,
    passwordForm.value.new,
    passwordForm.value.confirm
  )

  if (result.success) {
    message.value = { type: 'success', text: 'Mot de passe modifié avec succès' }
    passwordForm.value = { current: '', new: '', confirm: '' }
  } else {
    message.value = { type: 'error', text: result.error }
  }
}
</script>