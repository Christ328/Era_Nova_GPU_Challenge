import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { createAssessment } from '../api/assessments'
import type { Assessment } from '../types/assessment'
import ScoreCard from '../components/scoring/ScoreCard'
import RiskBadge from '../components/scoring/RiskBadge'
import RecommendationCard from '../components/scoring/RecommendationCard'
import ShapBarChart from '../components/explainability/ShapBarChart'
import FactorList from '../components/explainability/FactorList'

export default function AssessmentPage() {
  const { id } = useParams<{ id: string }>()
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id && id !== 'undefined') {
      createAssessment(id)
        .then(setAssessment)
        .catch(e => setError(e.message || 'Erreur lors de l\'évaluation'))
        .finally(() => setLoading(false))
    } else {
      setError('ID commerçant manquant')
      setLoading(false)
    }
  }, [id])

  if (loading) return <div className="text-text-secondary">Évaluation en cours...</div>
  if (error) return <div className="text-danger">{error}</div>
  if (!assessment) return null

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h2 className="text-2xl font-bold">Évaluation - {assessment.merchant_id}</h2>
        <Link to={`/review/${assessment.merchant_id}`} className="btn-primary">
          Décision humaine
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ScoreCard score={assessment.score} riskLevel={assessment.risk_level} />
        <RiskBadge riskLevel={assessment.risk_level} confidence={assessment.confidence} />
        <RecommendationCard assessment={assessment} />
      </div>

      <div className="card">
        <h3 className="font-semibold mb-2">Explication</h3>
        <p className="text-text-secondary">{assessment.explanation}</p>
        {assessment.human_review_required && (
          <div className="mt-3 p-3 bg-warning/10 border border-warning rounded-lg text-warning text-sm">
            Revue humaine obligatoire
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold mb-4">Facteurs SHAP</h3>
          <ShapBarChart factors={assessment.top_factors} />
        </div>
        <div className="card">
          <h3 className="font-semibold mb-4">Détail des facteurs</h3>
          <FactorList factors={assessment.top_factors} />
        </div>
      </div>

      {assessment.alerts.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-4">Alertes et règles métier</h3>
          <div className="space-y-2">
            {assessment.alerts.map((a, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg text-sm ${
                  a.severity === 'error'
                    ? 'bg-danger/10 border border-danger text-danger'
                    : a.severity === 'warning'
                    ? 'bg-warning/10 border border-warning text-warning'
                    : 'bg-primary/10 border border-primary text-primary'
                }`}
              >
                {a.message}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}