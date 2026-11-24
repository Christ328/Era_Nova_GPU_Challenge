import { api } from './client'
import type { MerchantListResponse, Merchant } from '../types/merchant'

export async function getMerchants(page = 1, pageSize = 20, search = ''): Promise<MerchantListResponse> {
  const { data } = await api.get('/merchants', { params: { page, page_size: pageSize, search } })
  return data
}

export async function getMerchant(id: string): Promise<Merchant> {
  const { data } = await api.get(`/merchants/${id}`)
  return data
}