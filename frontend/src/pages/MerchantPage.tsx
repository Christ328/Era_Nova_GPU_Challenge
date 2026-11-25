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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h2 className="text-2xl font-bold">{merchant.merchant_id}</h2>
        <Link to={`/assessment/${merchant.merchant_id}`} className="btn-primary">
          Évaluer ce commerçant
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold mb-4">Informations générales</h3>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Genre" value={(merchant as any).genre} />
            <InfoRow label="Âge" value={(merchant as any).age} />
            <InfoRow label="Éducation" value={(merchant as any).niveau_education} />
            <InfoRow label="Situation familiale" value={(merchant as any).situation_familiale} />
            <InfoRow label="Département" value={(merchant as any).departement} />
            <InfoRow label="Secteur" value={(merchant as any).secteur_activite} />
            <InfoRow label="Ancienneté" value={`${(merchant as any).anciennete_activite_mois} mois`} />
            <InfoRow label="Première fois" value={(merchant as any).premiere_fois ? 'Oui' : 'Non'} />
          </dl>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-4">Indicateurs financiers</h3>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Revenu mensuel" value={`${((merchant as any).revenu_mensuel_declare ?? 0).toLocaleString()} FCFA`} />
            <InfoRow label="Dépenses mensuelles" value={`${((merchant as any).depenses_mensuelles ?? 0).toLocaleString()} FCFA`} />
            <InfoRow label="Solde moyen" value={`${((merchant as any).solde_moyen_compte ?? 0).toLocaleString()} FCFA`} />
            <InfoRow label="Transactions/mois" value={(merchant as any).nb_transactions_mois} />
            <InfoRow label="Score intégrité" value={`${(((merchant as any).score_integrite ?? 0) * 100).toFixed(0)}%`} />
            <InfoRow label="Aptitude entrepreneuriale" value={(merchant as any).score_aptitude_entrepreneuriale} />
            <InfoRow label="Montant demandé" value={`${((merchant as any).montant_demande ?? 0).toLocaleString()} FCFA`} />
            <InfoRow label="Défaut paiement" value={(merchant as any).defaut_paiement ? 'Oui' : 'Non'} />
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