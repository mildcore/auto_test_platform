import request from './request'

export const authApi = {
  login(username, password) {
    return request.post('/auth/login', { username, password })
  },
  
  getCurrentUser() {
    return request.get('/auth/me')
  }
}
