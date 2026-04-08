import request from './request'

export const suiteApi = {
  getList(params) {
    return request.get('/suites', { params })
  },
  
  getById(id) {
    return request.get(`/suites/${id}`)
  },
  
  getCases(suiteId) {
    return request.get(`/suites/${suiteId}/cases`)
  },
  
  create(data) {
    return request.post('/suites', data)
  },
  
  delete(id) {
    return request.delete(`/suites/${id}`)
  },
  
  createCase(suiteId, data) {
    return request.post(`/suites/${suiteId}/cases`, data)
  }
}
