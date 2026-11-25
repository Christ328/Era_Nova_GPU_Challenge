import { api } from './client'

export const getIMFConfig = (id = 1) => api.get(`/imf/${id}`).then((r: any) => r.data)
export const updateIMFConfig = (id = 1, data: any) => api.put(`/imf/${id}`, data).then((r: any) => r.data)
