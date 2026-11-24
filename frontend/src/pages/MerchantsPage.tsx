import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getMerchants } from '../api/merchants'
import type { Merchant } from '../types/merchant'

export default function MerchantsPage() {
  const [merchants, setMerchants] = useState<Merchant[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    getMerchants(1, 50, search)
      .then(r => setMerchants(r.merchants))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [search])

  if (loading) return <div className="text-text-secondary">Chargement...</div>

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Commerçants</h2>

      <div className="card">
        <input
          type="text"
          placeholder="Rechercher..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input-field mb-4"
        />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-2 font-medium text-text-secondary">ID</th>
                <th className="text-left py-3 px-2 font-medium text-text-secondary">Activité</th>
                <th className="text-left py-3 px-2 font-medium text-text-secondary">Zone</th>
                <th className="text-left py-3 px-2 font-medium text-text-secondary">Primo</th>
                <th className="text-left py-3 px-2 font-medium text-text-secondary">Complétude</th>
                <th className="text-left py-3 px-2 font-medium text-text-secondary">Action</th>
              </tr>
            </thead>
            <tbody>
              {merchants.map(m => (
                <tr key={m.merchant_id} className="border-b border-border hover:bg-gray-50">
                  <td className="py-3 px-2 font-medium">{m.merchant_id}</td>
                  <td className="py-3 px-2">{m.activity ?? '-'}</td>
                  <td className="py-3 px-2">{m.zone ?? '-'}</td>
                  <td className="py-3 px-2">{m.is_first_time_borrower ? 'Oui' : 'Non'}</td>
                  <td className="py-3 px-2">{m.data_completeness ? `${(m.data_completeness * 100).toFixed(0)}%` : '-'}</td>
                  <td className="py-3 px-2">
                    <Link to={`/merchants/${m.merchant_id}`} className="text-primary hover:underline">
                      Voir
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {merchants.length === 0 && (
          <p className="text-text-secondary text-center py-8">Aucun commerçant trouvé</p>
        )}
      </div>
    </div>
  )
}