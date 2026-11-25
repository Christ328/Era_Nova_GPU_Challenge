import { useEffect, useState } from 'react'
import { getBenchmarks } from '../api/benchmarks'
import type { Benchmark } from '../types/benchmark'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function GpuBenchmarkPage() {
  const [benchmark, setBenchmark] = useState<Benchmark | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getBenchmarks()
      .then(setBenchmark)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-text-secondary">Chargement...</div>
  if (!benchmark) return <div className="text-danger">Benchmark non disponible</div>

  const chartData = [
    { name: 'Entraînement', CPU: benchmark.cpu_time, GPU: benchmark.gpu_time },
    { name: 'AUC', CPU: benchmark.cpu_auc * 100, GPU: benchmark.gpu_auc * 100 },
  ]

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Benchmark GPU</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Entraînement GPU" value={`${benchmark.gpu_time}s`} color="gpu" />
        <MetricCard label="Entraînement CPU" value={`${benchmark.cpu_time}s`} color="danger" />
        <MetricCard label="Speedup" value={`${benchmark.speedup}x`} color="success" />
        <MetricCard label="GPU" value={benchmark.gpu_type} color="primary" />
      </div>

      <div className="card">
        <h3 className="font-semibold mb-4">Comparaison CPU vs GPU</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="CPU" fill="#C2414B" />
            <Bar dataKey="GPU" fill="#6C5CE7" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3 className="font-semibold mb-4">Configuration</h3>
        <dl className="space-y-2 text-sm">
          <div className="flex justify-between">
            <dt className="text-text-secondary">Dataset</dt>
            <dd className="font-medium">{benchmark.dataset_size.toLocaleString()} lignes</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-text-secondary">Features</dt>
            <dd className="font-medium">{benchmark.n_features}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-text-secondary">XGBoost</dt>
            <dd className="font-medium">{benchmark.xgboost_version}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-text-secondary">GPU</dt>
            <dd className="font-medium">{benchmark.gpu_type}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    gpu: 'border-l-gpu',
    danger: 'border-l-danger',
    success: 'border-l-success',
    primary: 'border-l-primary',
  }
  return (
    <div className={`card border-l-4 ${colors[color]}`}>
      <p className="text-sm text-text-secondary">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}