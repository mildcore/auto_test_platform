import request from './request'

export const caseApi = {
  delete(id) {
    return request.delete(`/cases/${id}`)
  }
}
