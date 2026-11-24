import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getMerchant } from '../api/merchants'
import type { Merchant } from '../types/merchant'

export default function MerchantPage() {
  const { id } = useParams<{ id: string }>()
  const [merchant, setMerchant] = useState<Merchant | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      getMerchant(id)
        .then(setMerchant)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading) return <div className="text-text-secondary">Chargement...</div>
  if (!merchant) return <div className="text-danger">Commerçant non trouvé</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{merchant.merchant_id}</h2>
        <Link to={`/assessment/${merchant.merchant_id}`} className="btn-primary">
          Évaluer ce commerçant
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold mb-4">Informations générales</h3>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Activité" value={merchant.activity} />
            <InfoRow label="Zone" value={merchant.zone} />
            <InfoRow label="Taille" value={(merchant as any).activity_size} />
            <InfoRow label="Ancienneté" value={`${merchant.activity_age_months} mois`} />
            <InfoRow label="Primo-emprunteur" value={merchant.is_first_time_borrower ? 'Oui' : 'Non'} />
            <InfoRow label="Complétude données" value={`${((merchant.data_completeness ?? 0) * 100).toFixed(0)}%`} />
            <InfoRow label="Incohérences" value={(merchant as any).has_inconsistencies ? 'Détectées' : 'Aucune'} />
          </dl>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-4">Indicateurs financiers</h3>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Revenu mensuel" value={`${((merchant as any).monthly_income_mean ?? 0).toLocaleString()} FCFA`} />
            <InfoRow label="Ratio dépenses/revenus" value={`${(((merchant as any).expense_income_ratio ?? 0) * 100).toFixed(0)}%`} />
            <InfoRow label="Marge nette" value={`${(((merchant as any).margin_ratio ?? 0) * 100).toFixed(0)}%`} />
            <InfoRow label="Régularité" value={`${(((merchant as any).regularity_score ?? 0) * 100).toFixed(0)}%`} />
            <InfoRow label="Documentation" value={`${(((merchant as any).documentation_quality ?? 0) * 100).toFixed(0)}%`} />
          </dl>
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: any }) {
  return (
    <div className="flex justify-between">
      <dt className="text-text-secondary">{label}</dt>
      <dd className="font-medium">{value ?? '-'}</dd>
    </div>
  )
}