import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getMerchants } from '../api/merchants'
import { getBenchmarks } from '../api/benchmarks'
import type { Merchant } from '../types/merchant'
import type { Benchmark } from '../types/benchmark'
import { Users, CreditCard, AlertTriangle, Cpu, ArrowRight } from 'lucide-react'

export default function DashboardPage() {
  const [merchants, setMerchants] = useState<Merchant[]>([])
  const [benchmark, setBenchmark] = useState<Benchmark | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getMerchants(1, 5), getBenchmarks()])
      .then(([m, b]) => { setMerchants(m.merchants); setBenchmark(b) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-text-secondary">Chargement...</div>

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Tableau de bord</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard icon={Users} label="Commerçants" value="3" color="primary" />
        <KpiCard icon={CreditCard} label="Évaluations" value="0" color="gpu" />
        <KpiCard icon={AlertTriangle} label="Revues requises" value="2" color="warning" />
        <KpiCard icon={Cpu} label="Speedup GPU" value={`${benchmark?.speedup ?? 'N/A'}x`} color="success" />
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Dossiers récents</h3>
          <Link to="/merchants" className="text-primary text-sm flex items-center gap-1">
            Tout voir <ArrowRight size={14} />
          </Link>
        </div>
        <div className="space-y-2">
          {merchants.map(m => (
            <Link
              key={m.merchant_id}
              to={`/merchants/${m.merchant_id}`}
              className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div>
                <span className="font-medium">{m.merchant_id}</span>
                <span className="text-sm text-text-secondary ml-3">{m.activity}</span>
              </div>
              <span className="text-sm text-text-secondary">{m.zone}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

function KpiCard({ icon: Icon, label, value, color }: any) {
  const colors: Record<string, string> = {
    primary: 'text-primary bg-primary/10',
    gpu: 'text-gpu bg-gpu/10',
    warning: 'text-warning bg-warning/10',
    success: 'text-success bg-success/10',
  }
  return (
    <div className="card">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color]}`}>
        <Icon size={20} />
      </div>
      <p className="text-2xl font-bold mt-3">{value}</p>
      <p className="text-sm text-text-secondary">{label}</p>
    </div>
  )
}