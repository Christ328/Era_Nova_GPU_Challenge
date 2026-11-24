import { api } from './client'
import type { Benchmark } from '../types/benchmark'

export async function getBenchmarks(): Promise<Benchmark> {
  const { data } = await api.get('/benchmarks')
  return data
}