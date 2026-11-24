import { useEffect, useState } from 'react'
import { api } from '../api/client'

interface Rule {
  name: string
  description: string
  condition: string
  action: string
  severity: string
  multiplier?: number
}

export default function RulesPage() {
  const [rules, setRules] = useState<Rule[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/rules')
      .then(r => setRules(r.data.rules))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-text-secondary">Chargement...</div>

  const severityColors: Record<string, string> = {
    error: 'bg-danger/10 border-danger text-danger',
    warning: 'bg-warning/10 border-warning text-warning',
    info: 'bg-primary/10 border-primary text-primary',
  }

  const actionLabels: Record<string, string> = {
    limit_amount: 'Limiter le montant',
    reduce_amount: 'Réduire le montant',
    require_human_review: 'Revue humaine',
    no_auto_recommendation: 'Pas de recommandation auto',
    progressive_amount: 'Crédit progressif',
    request_additional_info: 'Infos complémentaires',
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Règles métier</h2>
      <p className="text-text-secondary">
        Les règles complètent le modèle statistique. Elles s'appliquent après le calcul du score.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {rules.map((rule, i) => (
          <div key={i} className={`card border-l-4 ${severityColors[rule.severity] || ''}`}>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">{rule.description}</h3>
              <span className={`badge ${severityColors[rule.severity] || ''}`}>
                {rule.severity}
              </span>
            </div>
            <p className="text-sm text-text-secondary mb-2">
              <code className="bg-gray-100 px-2 py-1 rounded text-xs">{rule.condition}</code>
            </p>
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-secondary">Action:</span>
              <span className="font-medium">{actionLabels[rule.action] || rule.action}</span>
            </div>
            {rule.multiplier && (
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-text-secondary">Multiplicateur:</span>
                <span className="font-medium text-warning">×{rule.multiplier}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="font-semibold mb-3">Logique de décision</h3>
        <div className="text-sm text-text-secondary space-y-2">
          <p>1. Le modèle XGBoost calcule un score de 0 à 100</p>
          <p>2. Les règles métier vérifient les conditions et ajustent le score</p>
          <p>3. Si le montant demandé dépasse 300 000 FCFA, il est plafonné</p>
          <p>4. Si le score est inférieur à 70, le montant est réduit par paliers de 10 000 FCFA</p>
          <p>5. La décision finale reste humaine</p>
        </div>
      </div>
    </div>
  )
}