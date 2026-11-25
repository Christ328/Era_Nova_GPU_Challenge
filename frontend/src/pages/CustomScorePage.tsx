import { useState } from 'react'
import { scoreCustom } from '../api/assessments'
import type { Assessment } from '../types/assessment'
import ScoreCard from '../components/scoring/ScoreCard'
import RiskBadge from '../components/scoring/RiskBadge'
import ScoringLoader from '../components/scoring/ScoringLoader'
import ShapBarChart from '../components/explainability/ShapBarChart'

const DEFAULT_FEATURES: Record<string, number> = {
  age: 35,
  anciennete_activite_mois: 24,
  revenu_mensuel_declare: 150000,
  depenses_mensuelles: 90000,
  proprietaire_local: 0,
  nombre_employes: 1,
  nb_transactions_mois: 30,
  volume_depots_moyen: 50000,
  volume_retraits_moyen: 30000,
  solde_moyen_compte: 100000,
  tendance_solde_3m: 0.1,
  regularite_depots_ecart_type: 0.3,
  nb_contreparties_distinctes: 15,
  part_transferts_marchands: 0.2,
  nb_transactions_echouees: 1,
  frequence_recharges_mois: 5,
  montant_moyen_recharge: 500,
  anciennete_ligne_mois: 24,
  nb_contacts_distincts: 30,
  stabilite_lieu_vie: 0.8,
  membre_tontine: 1,
  anciennete_tontine_mois: 12,
  regularite_cotisations_tontine: 0.9,
  montant_moyen_cotisation: 2000,
  deja_beneficiaire_tour: 0,
  score_aptitude_entrepreneuriale: 65,
  score_integrite: 0.75,
  locus_controle_interne: 6,
  proximite_marche_km: 3,
  indicateur_jour_marche: 1,
  membre_groupement_pro: 1,
  premiere_fois: 0,
  montant_demande: 200000,
  duree_credit_mois: 6,
  garantie: 0.5,
}

const FEATURE_LABELS: Record<string, string> = {
  age: 'Âge',
  anciennete_activite_mois: 'Ancienneté (mois)',
  revenu_mensuel_declare: 'Revenu mensuel (FCFA)',
  depenses_mensuelles: 'Dépenses mensuelles (FCFA)',
  proprietaire_local: 'Propriétaire local (0/1)',
  nombre_employes: 'Nombre employés',
  nb_transactions_mois: 'Transactions/mois',
  volume_depots_moyen: 'Volume dépôts moyen',
  volume_retraits_moyen: 'Volume retraits moyen',
  solde_moyen_compte: 'Solde moyen compte',
  tendance_solde_3m: 'Tendance solde 3m',
  regularite_depots_ecart_type: 'Régularité dépôts',
  nb_contreparties_distinctes: 'Contreparties',
  part_transferts_marchands: 'Part transferts',
  nb_transactions_echouees: 'Transactions échouées',
  frequence_recharges_mois: 'Fréquence recharges',
  montant_moyen_recharge: 'Montant recharge',
  anciennete_ligne_mois: 'Ancienneté ligne (mois)',
  nb_contacts_distincts: 'Contacts distincts',
  stabilite_lieu_vie: 'Stabilité lieu vie',
  membre_tontine: 'Membre tontine (0/1)',
  anciennete_tontine_mois: 'Ancienneté tontine',
  regularite_cotisations_tontine: 'Régularité cotisations',
  montant_moyen_cotisation: 'Montant cotisation',
  deja_beneficiaire_tour: 'Déjà bénéficiaire (0/1)',
  score_aptitude_entrepreneuriale: 'Aptitude entrepreneuriale',
  score_integrite: 'Score intégrité',
  locus_controle_interne: 'Locus contrôle',
  proximite_marche_km: 'Proximité marché (km)',
  indicateur_jour_marche: 'Jour marché (0/1)',
  membre_groupement_pro: 'Groupement pro (0/1)',
  premiere_fois: 'Première fois (0/1)',
  montant_demande: 'Montant demandé (FCFA)',
  duree_credit_mois: 'Durée crédit (mois)',
  garantie: 'Garantie',
}

export default function CustomScorePage() {
  const [features, setFeatures] = useState<Record<string, number>>(DEFAULT_FEATURES)
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (key: string, value: string) => {
    setFeatures(prev => ({ ...prev, [key]: parseFloat(value) || 0 }))
  }

  const handleScore = async () => {
    if (features.montant_demande > 300000) {
      alert('Le montant demandé ne peut pas dépasser 300 000 FCFA.')
      return
    }
    setLoading(true)
    try {
      const result = await scoreCustom(features)
      setAssessment(result)
    } catch (e: any) {
      console.error('Score error:', e)
      alert('Erreur: ' + (e.response?.data?.detail || e.message || 'API inaccessible'))
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFeatures(DEFAULT_FEATURES)
    setAssessment(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h2 className="text-2xl font-bold">Évaluation personnalisée</h2>
        <div className="flex gap-2">
          <button onClick={handleReset} className="btn-secondary">Réinitialiser</button>
          <button onClick={handleScore} disabled={loading} className="btn-primary">
            {loading ? 'Calcul...' : 'Calculer le score'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {Object.entries(features).map(([key, val]) => (
          <div key={key}>
            <label className="block text-sm font-medium mb-1">
              {FEATURE_LABELS[key] || key}
            </label>
            <input
              type="number"
              value={val}
              onChange={e => handleChange(key, e.target.value)}
              className="input-field"
              step={key.includes('revenu') || key.includes('depenses') || key.includes('montant') || key.includes('solde') || key.includes('volume') ? 1000 : 0.1}
              max={key === 'montant_demande' ? 300000 : undefined}
              min={key === 'montant_demande' ? 5000 : undefined}            />
          </div>
        ))}
      </div>

      {loading && <ScoringLoader />}

      {!loading && assessment && (
        <div className="space-y-6 mt-8">
          <h3 className="text-xl font-bold">Résultat</h3>

          {/* Alerts first — prominent, full-width */}
          {assessment.alerts.length > 0 && (
            <div className="space-y-3">
              {assessment.alerts.map((a, i) => (
                <div key={i} className={`p-4 rounded-xl text-base font-medium flex items-start gap-3 ${
                  a.severity === 'error'   ? 'bg-danger/10 border-2 border-danger text-danger' :
                  a.severity === 'warning' ? 'bg-warning/10 border-2 border-warning text-warning' :
                                             'bg-primary/10 border-2 border-primary text-primary'
                }`}>
                  <span className="text-xl mt-0.5">
                    {a.severity === 'error' ? '🚫' : a.severity === 'warning' ? '⚠️' : 'ℹ️'}
                  </span>
                  <span>{a.message}</span>
                </div>
              ))}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ScoreCard score={assessment.score} riskLevel={assessment.risk_level} />
            <RiskBadge riskLevel={assessment.risk_level} confidence={assessment.confidence} />
          </div>

          {/* Hybrid score breakdown */}
          {(assessment.ml_score !== undefined || assessment.business_score !== undefined) && (
            <div className="card bg-surface-alt border border-border">
              <h4 className="text-sm font-semibold text-text-secondary mb-3">Décomposition du score</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col items-center p-3 rounded-lg bg-primary/5 border border-primary/20">
                  <span className="text-xs text-text-secondary mb-1">Score ML</span>
                  <span className="text-2xl font-bold text-primary">{assessment.ml_score ?? '—'}</span>
                  <span className="text-xs text-text-secondary mt-1">poids {assessment.score_weights ? Math.round(assessment.score_weights.ml * 100) : '—'}%</span>
                </div>
                <div className="flex flex-col items-center p-3 rounded-lg bg-success/5 border border-success/20">
                  <span className="text-xs text-text-secondary mb-1">Score Règles</span>
                  <span className="text-2xl font-bold" style={{color: '#168A62'}}>{assessment.business_score ?? '—'}</span>
                  <span className="text-xs text-text-secondary mt-1">poids {assessment.score_weights ? Math.round(assessment.score_weights.rules * 100) : '—'}%</span>
                </div>
              </div>
            </div>
          )}

          <div className="card">
            <h3 className="font-semibold mb-4">Explication</h3>
            <p className="text-text-secondary mb-6">{assessment.explanation}</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Positive factors */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-3 h-3 rounded-full" style={{ background: '#168A62' }} />
                  <h4 className="font-semibold text-sm" style={{ color: '#168A62' }}>Facteurs favorables</h4>
                </div>
                <div className="space-y-2">
                  {assessment.top_factors.filter(f => f.direction === 'positive').map((f, i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded-lg text-sm bg-success/5">
                      <span className="text-text-primary">{f.label}</span>
                      <div className="flex items-center gap-2 text-right">
                        <span className="text-text-secondary text-xs">{typeof f.value === 'number' ? f.value.toLocaleString() : f.value}</span>
                        <span className="font-medium" style={{ color: '#168A62' }}>+{f.impact.toFixed(3)}</span>
                      </div>
                    </div>
                  ))}
                  {assessment.top_factors.filter(f => f.direction === 'positive').length === 0 && (
                    <p className="text-xs text-text-secondary italic">Aucun facteur favorable détecté.</p>
                  )}
                </div>
              </div>

              {/* Negative factors */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-3 h-3 rounded-full" style={{ background: '#C2414B' }} />
                  <h4 className="font-semibold text-sm" style={{ color: '#C2414B' }}>Facteurs pénalisants</h4>
                </div>
                <div className="space-y-2">
                  {assessment.top_factors.filter(f => f.direction === 'negative').map((f, i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded-lg text-sm bg-danger/5">
                      <span className="text-text-primary">{f.label}</span>
                      <div className="flex items-center gap-2 text-right">
                        <span className="text-text-secondary text-xs">{typeof f.value === 'number' ? f.value.toLocaleString() : f.value}</span>
                        <span className="font-medium" style={{ color: '#C2414B' }}>{f.impact.toFixed(3)}</span>
                      </div>
                    </div>
                  ))}
                  {assessment.top_factors.filter(f => f.direction === 'negative').length === 0 && (
                    <p className="text-xs text-text-secondary italic">Aucun facteur pénalisant détecté.</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold mb-4">Graphique SHAP</h3>
            <ShapBarChart factors={assessment.top_factors} />
          </div>
        </div>
      )}
    </div>
  )
}