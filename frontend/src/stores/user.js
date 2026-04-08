import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import request from '@/api/request'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  
  // Getters
  const isLoggedIn = computed(() => !!token.value)
  
  // Actions
  async function login(user, pass) {
    const res = await authApi.login(user, pass)
    token.value = res.data.token
    username.value = res.data.username
    
    localStorage.setItem('token', token.value)
    localStorage.setItem('username', username.value)
    
    // 设置axios默认header
    request.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    
    return res
  }
  
  function logout() {
    token.value = ''
    username.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    delete request.defaults.headers.common['Authorization']
  }
  
  // 初始化时恢复token
  function init() {
    if (token.value) {
      request.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }
  
  return {
    token,
    username,
    isLoggedIn,
    login,
    logout,
    init
  }
})
