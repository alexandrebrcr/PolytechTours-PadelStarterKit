// ============================================
// FICHIER : frontend/src/views/LoginPage.vue
// ============================================

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-lg shadow-2xl p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="text-6xl mb-4">🎾</div>
          <h1 class="text-3xl font-bold text-gray-800">Corpo Padel</h1>
          <p class="text-gray-600 mt-2">Connectez-vous à votre compte</p>
        </div>

        <!-- Formulaire -->
        <form @submit.prevent="handleLogin">
          <!-- Email -->
          <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="votre@email.com"
            />
          </div>

          <!-- Mot de passe -->
          <div class="mb-2">
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          <!-- Mot de passe oublié -->
          <div class="flex justify-end mb-6">
            <button 
              type="button" 
              @click="showForgotPasswordModal = true"
              class="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Mot de passe oublié ?
            </button>
          </div>

          <!-- Message d'erreur -->
          <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-700 text-sm">{{ errorMessage }}</p>
            <p v-if="attemptsRemaining !== null" class="text-red-600 text-sm font-semibold mt-1">
              Tentatives restantes : {{ attemptsRemaining }}
            </p>
            <p v-if="minutesRemaining !== null" class="text-red-600 text-sm font-semibold mt-1">
              Compte bloqué pendant {{ minutesRemaining }} minutes
            </p>
          </div>

          <!-- Bouton de connexion -->
          <button
            type="submit"
            :disabled="loading || minutesRemaining !== null"
            class="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Connexion...</span>
            <span v-else-if="minutesRemaining !== null">Compte bloqué</span>
            <span v-else>Se connecter</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showChangePasswordModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
      <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4 text-gray-800">Changement de mot de passe requis</h2>
        <p class="text-gray-600 mb-6">C'est votre première connexion. Veuillez changer votre mot de passe pour continuer.</p>
        
        <form @submit.prevent="handleChangePassword">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Nouveau mot de passe</label>
            <input v-model="newPassword" type="password" required minlength="12" class="w-full px-4 py-2 border rounded-lg">
            <p class="text-xs text-gray-500 mt-1">12 caractères min, majuscule, minuscule, chiffre, caractère spécial.</p>
          </div>
          
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Confirmer le mot de passe</label>
            <input v-model="confirmPassword" type="password" required class="w-full px-4 py-2 border rounded-lg">
          </div>

          <div v-if="modalError" class="mb-4 p-3 bg-red-50 text-red-700 rounded text-sm whitespace-pre-wrap">
            {{ modalError }}
          </div>

          <button type="submit" class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Changer le mot de passe
          </button>
        </form>
      </div>
    </div>

    <!-- Forgot Password Modal -->
    <div v-if="showForgotPasswordModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
      <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md text-center">
        <h2 class="text-2xl font-bold mb-4 text-gray-800">Mot de passe oublié</h2>
        <p class="text-gray-600 mb-4">Veuillez contacter votre administrateur local.</p>
        <p class="text-blue-600 font-bold text-lg mb-6">contact.support@padel.com</p>
        <button @click="showForgotPasswordModal = false" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Fermer
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const attemptsRemaining = ref(null)
const minutesRemaining = ref(null)

// Modal state
const showChangePasswordModal = ref(false)
const showForgotPasswordModal = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const modalError = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''
  attemptsRemaining.value = null
  minutesRemaining.value = null

  const result = await authStore.login(email.value, password.value)

  if (result.success) {
    if (authStore.user?.must_change_password) {
      showChangePasswordModal.value = true
    } else {
      router.push('/')
    }
  } else {
    errorMessage.value = result.error || 'Erreur de connexion'
    attemptsRemaining.value = result.attemptsRemaining ?? null
    minutesRemaining.value = result.minutesRemaining ?? null
  }

  loading.value = false
}

const handleChangePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    modalError.value = "Les mots de passe ne correspondent pas"
    return
  }

  const result = await authStore.changePassword(password.value, newPassword.value, confirmPassword.value)
  
  if (result.success) {
    showChangePasswordModal.value = false
    router.push('/')
  } else {
    modalError.value = result.error
  }
}
</script>