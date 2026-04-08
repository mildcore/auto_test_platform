import request from './request'

export const taskApi = {
  getList(params) {
    return request.get('/tasks', { params })
  },
  
  getById(id) {
    return request.get(`/tasks/${id}`)
  },
  
  delete(id) {
    return request.delete(`/tasks/${id}`)
  },
  
  cancel(id) {
    return request.post(`/tasks/${id}/cancel`)
  }
}
