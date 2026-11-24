import type { Assessment } from '../../types/assessment'

export default function RecommendationCard({ assessment }: { assessment: Assessment }) {
  return (
    <div className="card">
      <p className="text-sm text-text-secondary mb-2">Recommandation</p>
      <p className="font-semibold text-lg">
        {assessment.recommended_amount_min.toLocaleString()} - {assessment.recommended_amount_max.toLocaleString()} FCFA
      </p>
      <p className="text-sm text-text-secondary mt-1">
        Durée: {assessment.recommended_duration_months} mois
      </p>
      <p className="text-sm text-text-secondary">
        Produit: {assessment.product_type}
      </p>
      {assessment.human_review_required && (
        <span className="badge bg-warning/10 text-warning mt-2">
          Revue humaine requise
        </span>
      )}
    </div>
  )
}