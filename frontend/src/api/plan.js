import request from './request'

export const planApi = {
  getList(params) {
    return request.get('/plans', { params })
  },
  
  getById(id) {
    return request.get(`/plans/${id}`)
  },
  
  create(data) {
    return request.post('/plans', data)
  },
  
  update(id, data) {
    return request.put(`/plans/${id}`, data)
  },
  
  delete(id) {
    return request.delete(`/plans/${id}`)
  },
  
  execute(id) {
    return request.post(`/plans/${id}/execute`)
  },
  
  toggle(id) {
    return request.post(`/plans/${id}/toggle`)
  },
  
  copy(id) {
    return request.post(`/plans/${id}/copy`)
  }
}
