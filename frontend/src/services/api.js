// ============================================
// FICHIER : frontend/src/services/api.js
// ============================================

import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Ne pas rediriger si c'est une erreur de login (401 normal)
    if (error.response?.status === 401 && !error.config.url.includes('/auth/login')) {
      // Token expiré ou invalide sur une autre route
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API d'authentification
export const authAPI = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  logout: () => 
    api.post('/auth/logout'),
  
  changePassword: (currentPassword, newPassword, confirmPassword) =>
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    }),

  getProfile: () => api.get('/auth/me'),
  
  updateProfile: (data) => api.put('/auth/me', data),
  
  uploadAvatar: (formData) => api.post('/auth/me/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  deleteAvatar: () => api.delete('/auth/me/avatar'),

  // API administrateur
  createAccount: (playerId) => api.post('/admin/accounts', { player_id: playerId }),
  
  updatePlayerRole: (playerId, role) => api.put(`/admin/players/${playerId}/role?role=${role}`),

  // Teams
  getTeams: () => api.get('/admin/teams'),
  
  // Pools
  getPools: () => api.get('/admin/pools'),
}

export const matchesAPI = {
  getMatches: (params) => api.get('/matches', { params }),
  createMatch: (data) => api.post('/matches', data),
  updateMatch: (id, data) => api.put(`/matches/${id}`, data),
  deleteMatch: (id) => api.delete(`/matches/${id}`)
}

export const resultsAPI = {
  getRanking: () => api.get('/results/ranking')
}

export const planningAPI = {
  getEvents: (params) => api.get('/planning', { params }),
  createEvent: (data) => api.post('/planning', data),
  deleteEvent: (id) => api.delete(`/planning/${id}`)
}

export default api