import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))

  const login = async (username, password) => {
    const res = await axios.post('/api/auth/login', { username, password })
    token.value = res.data.token
    user.value = res.data.user
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res.data
  }

  const register = async (username, password, nickname) => {
    const res = await axios.post('/api/auth/register', { username, password, nickname })
    token.value = res.data.token
    user.value = res.data.user
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res.data
  }

  const logout = () => {
    token.value = ''
    user.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const role = user.value.role || ''

  return { token, user, role, login, register, logout }
})

export const useApi = () => {
  return axios.create({
    baseURL: '',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`
    }
  })
}