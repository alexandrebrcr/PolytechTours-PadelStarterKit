// ============================================
// FICHIER : frontend/src/stores/auth.js
// ============================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'ADMINISTRATEUR')

  function setAuth(authToken, userData) {
    token.value = authToken
    user.value = userData
    localStorage.setItem('token', authToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function checkAuth() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    
    try {
      const response = await authAPI.login(email, password)
      const { access_token, user: userData } = response.data
      
      setAuth(access_token, userData)
      return { success: true }
    } catch (err) {
      console.log('Login error:', err)
      console.log('Response data:', err.response?.data)
      const errorData = err.response?.data?.detail
      
      if (typeof errorData === 'object') {
        error.value = errorData.message || 'Erreur de connexion'
        return { 
          success: false, 
          error: errorData.message,
          attemptsRemaining: errorData.attempts_remaining,
          minutesRemaining: errorData.minutes_remaining
        }
      } else {
        error.value = errorData || 'Erreur de connexion'
        return { success: false, error: error.value }
      }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authAPI.logout()
    } catch (err) {
      console.error('Erreur lors de la déconnexion:', err)
    } finally {
      clearAuth()
    }
  }

  async function updateProfile(data) {
    loading.value = true
    error.value = null
    try {
      // Clean data before sending
      const payload = { ...data }
      if (payload.birthdate === '') {
        payload.birthdate = null
      }

      const response = await authAPI.updateProfile(payload)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erreur lors de la mise à jour'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function changePassword(current, newP, confirmP) {
    loading.value = true
    error.value = null
    try {
      await authAPI.changePassword(current, newP, confirmP)
      return { success: true }
    } catch (err) {
      let errorMessage = 'Erreur lors du changement de mot de passe'
      const detail = err.response?.data?.detail

      if (Array.isArray(detail)) {
        // Pydantic validation errors
        errorMessage = detail.map(e => {
            if (e.msg.startsWith('Value error, ')) {
                return e.msg.replace('Value error, ', '')
            }
            return e.msg
        }).join('\n')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      }
      
      error.value = errorMessage
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function uploadAvatar(file) {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await authAPI.uploadAvatar(formData)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Erreur upload' }
    } finally {
      loading.value = false
    }
  }

  async function deleteAvatar() {
    loading.value = true
    try {
      const response = await authAPI.deleteAvatar()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail }
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    checkAuth,
    updateProfile,
    changePassword,
    uploadAvatar,
    deleteAvatar
  }
})
