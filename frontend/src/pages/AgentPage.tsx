import { useState } from 'react'
import ScoringLoader from '../components/scoring/ScoringLoader'
import { scoreCustom } from '../api/assessments'
import type { Assessment, CounterProposal } from '../types/assessment'

interface FormState {
  nom: string
  prenom: string
  telephone: string
  numero_mobile_money: string
  genre: 'Homme' | 'Femme'
  age: number
  secteur_activite: 'Commerce' | 'Agriculture' | 'Artisanat' | 'Services' | 'Autre'
  anciennete_mois: number
  montant_demande: number
  duree_mois: number
  garantie: boolean
  type_garantie: string
}

const DEFAULT_FORM: FormState = {
  nom: '',
  prenom: '',
  telephone: '',
  numero_mobile_money: '',
  genre: 'Homme',
  age: 30,
  secteur_activite: 'Commerce',
  anciennete_mois: 12,
  montant_demande: 50000,
  duree_mois: 6,
  garantie: false,
  type_garantie: '',
}

function buildFeatures(form: FormState): Record<string, number> {
  return {
    age: form.age,
    anciennete_activite_mois: form.anciennete_mois,
    revenu_mensuel_declare: 100000,
    depenses_mensuelles: 60000,
    proprietaire_local: 0,
    nombre_employes: 1,
    nb_transactions_mois: 20,
    volume_depots_moyen: 40000,
    volume_retraits_moyen: 25000,
    solde_moyen_compte: 80000,
    tendance_solde_3m: 0.05,
    regularite_depots_ecart_type: 0.3,
    nb_contreparties_distinctes: 10,
    part_transferts_marchands: 0.15,
    nb_transactions_echouees: 1,
    frequence_recharges_mois: 4,
    montant_moyen_recharge: 500,
    anciennete_ligne_mois: form.anciennete_mois,
    nb_contacts_distincts: 20,
    stabilite_lieu_vie: 0.7,
    membre_tontine: 0,
    anciennete_tontine_mois: 0,
    regularite_cotisations_tontine: 0,
    montant_moyen_cotisation: 0,
    deja_beneficiaire_tour: 0,
    score_aptitude_entrepreneuriale: 60,
    score_integrite: 0.7,
    locus_controle_interne: 5,
    proximite_marche_km: 3,
    indicateur_jour_marche: 1,
    membre_groupement_pro: 0,
    premiere_fois: 1,
    montant_demande: form.montant_demande,
    duree_credit_mois: form.duree_mois,
    garantie: form.garantie ? 1 : 0,
  }
}

const STEPPER_LABELS = ['Informations client', 'Traitement', 'Résultat']

export default function AgentPage() {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState<FormState>(DEFAULT_FORM)
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastFeatures, setLastFeatures] = useState<Record<string, number>>({})

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    setStep(2)
    const features = buildFeatures(form)
    setLastFeatures(features)
    try {
      const result = await scoreCustom(features)
      setAssessment(result)
      setStep(3)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'API inaccessible')
      setStep(1)
    } finally {
      setLoading(false)
    }
  }

  const handleCounterProposal = async (proposal: CounterProposal) => {
    setLoading(true)
    setStep(2)
    const proposalFeatures = { ...lastFeatures, montant_demande: proposal.amount, duree_credit_mois: proposal.duration }
    try {
      const result = await scoreCustom(proposalFeatures)
      setAssessment(result)
      setStep(3)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'API inaccessible')
      setStep(3)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold">Nouvelle demande de crédit</h2>

      {/* Stepper */}
      <div className="flex items-center gap-2">
        {STEPPER_LABELS.map((label, i) => {
          const num = i + 1
          const active = step === num
          const done = step > num
          return (
            <div key={num} className="flex items-center gap-2 flex-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
                done ? 'bg-primary text-white' :
                active ? 'bg-primary text-white ring-4 ring-primary/20' :
                'bg-gray-100 text-text-secondary'
              }`}>
                {done ? '✓' : num}
              </div>
              <span className={`text-sm ${active ? 'font-semibold text-primary' : 'text-text-secondary'}`}>{label}</span>
              {i < STEPPER_LABELS.length - 1 && (
                <div className={`flex-1 h-0.5 ${done ? 'bg-primary' : 'bg-gray-200'}`} />
              )}
            </div>
          )
        })}
      </div>

      {/* Step 1 — Form */}
      {step === 1 && (
        <form onSubmit={handleSubmit} className="card space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-danger/10 border border-danger text-danger text-sm">{error}</div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nom *</label>
              <input
                type="text"
                required
                value={form.nom}
                onChange={e => setForm(f => ({ ...f, nom: e.target.value }))}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Prénom *</label>
              <input
                type="text"
                required
                value={form.prenom}
                onChange={e => setForm(f => ({ ...f, prenom: e.target.value }))}
                className="input-field"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Téléphone</label>
              <input
                type="text"
                value={form.telephone}
                onChange={e => setForm(f => ({ ...f, telephone: e.target.value }))}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">N° Mobile Money</label>
              <input
                type="text"
                value={form.numero_mobile_money}
                onChange={e => setForm(f => ({ ...f, numero_mobile_money: e.target.value }))}
                className="input-field"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Genre</label>
              <select
                value={form.genre}
                onChange={e => setForm(f => ({ ...f, genre: e.target.value as FormState['genre'] }))}
                className="input-field"
              >
                <option value="Homme">Homme</option>
                <option value="Femme">Femme</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Âge</label>
              <input
                type="number"
                min={18}
                max={99}
                value={form.age}
                onChange={e => setForm(f => ({ ...f, age: parseInt(e.target.value) || 18 }))}
                className="input-field"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Secteur d'activité</label>
              <select
                value={form.secteur_activite}
                onChange={e => setForm(f => ({ ...f, secteur_activite: e.target.value as FormState['secteur_activite'] }))}
                className="input-field"
              >
                <option value="Commerce">Commerce</option>
                <option value="Agriculture">Agriculture</option>
                <option value="Artisanat">Artisanat</option>
                <option value="Services">Services</option>
                <option value="Autre">Autre</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Ancienneté (mois)</label>
              <input
                type="number"
                min={0}
                value={form.anciennete_mois}
                onChange={e => setForm(f => ({ ...f, anciennete_mois: parseInt(e.target.value) || 0 }))}
                className="input-field"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Montant demandé (FCFA)</label>
              <input
                type="number"
                min={5000}
                max={300000}
                value={form.montant_demande}
                onChange={e => setForm(f => ({ ...f, montant_demande: parseInt(e.target.value) || 5000 }))}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Durée (mois)</label>
              <input
                type="number"
                min={1}
                max={60}
                value={form.duree_mois}
                onChange={e => setForm(f => ({ ...f, duree_mois: parseInt(e.target.value) || 1 }))}
                className="input-field"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="garantie"
                checked={form.garantie}
                onChange={e => setForm(f => ({ ...f, garantie: e.target.checked }))}
                className="w-4 h-4"
              />
              <label htmlFor="garantie" className="text-sm font-medium">Garantie disponible</label>
            </div>
            {form.garantie && (
              <div>
                <label className="block text-sm font-medium mb-1">Type de garantie</label>
                <input
                  type="text"
                  value={form.type_garantie}
                  onChange={e => setForm(f => ({ ...f, type_garantie: e.target.value }))}
                  className="input-field"
                  placeholder="Ex : bien immobilier, véhicule..."
                />
              </div>
            )}
          </div>

          <button type="submit" className="btn-primary w-full">
            Soumettre la demande
          </button>
        </form>
      )}

      {/* Step 2 — Loading */}
      {step === 2 && loading && <ScoringLoader />}

      {/* Step 3 — Result */}
      {step === 3 && assessment && (
        <div className="space-y-6">
          {/* ACCEPTED */}
          {assessment.decision === 'ACCEPTED' && (
            <div className="space-y-6">
              <div className="text-center"><span className="badge-accepted">ACCEPTÉ</span></div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Score</span>
                  <span className="font-bold">{assessment.score} / 1000</span>
                </div>
                <div className="score-gauge">
                  <div
                    className="score-gauge-fill"
                    style={{
                      width: `${(assessment.score / 1000) * 100}%`,
                      background: assessment.score >= 750 ? '#168A62' : assessment.score >= 450 ? '#C47B12' : '#C2414B'
                    }}
                  />
                </div>
              </div>
              {assessment.ml_score !== undefined && assessment.business_score !== undefined && (
                <p className="text-sm text-text-secondary text-center">
                  Score ML : {assessment.ml_score}/1000 · Score Règles : {assessment.business_score}/1000
                </p>
              )}
              <div className="card">
                <h4 className="font-semibold mb-3">Conditions du prêt</h4>
                <dl className="grid grid-cols-2 gap-2 text-sm">
                  <dt className="text-text-secondary">Montant demandé</dt>
                  <dd className="font-medium">{form.montant_demande?.toLocaleString()} FCFA</dd>
                  <dt className="text-text-secondary">Durée</dt>
                  <dd className="font-medium">{form.duree_mois} mois</dd>
                  {assessment.teg !== undefined && (
                    <>
                      <dt className="text-text-secondary">TEG</dt>
                      <dd className="font-medium">{(assessment.teg * 100).toFixed(2)}%</dd>
                    </>
                  )}
                </dl>
              </div>
              <button
                className="btn-secondary w-full"
                onClick={() => alert('Fonctionnalité à venir')}
              >
                Générer le contrat
              </button>
            </div>
          )}

          {/* REFUSED_REGULATORY */}
          {assessment.decision === 'REFUSED_REGULATORY' && (
            <div className="space-y-4">
              <div className="text-center"><span className="badge-refused">REFUSÉ — MOTIF RÉGLEMENTAIRE</span></div>
              <div className="p-4 rounded-xl bg-danger/10 border-2 border-danger text-danger">
                Le TEG de {assessment.teg}% dépasse le plafond légal de 24% (BCEAO).
              </div>
              <button className="btn-secondary" onClick={() => setStep(1)}>Retour</button>
            </div>
          )}

          {/* REFUSED_RISK or MANUAL_REVIEW or default */}
          {(assessment.decision === 'REFUSED_RISK' || assessment.decision === 'MANUAL_REVIEW' || (!assessment.decision)) && (
            <div className="space-y-6">
              <div className="text-center">
                {assessment.decision === 'MANUAL_REVIEW'
                  ? <span className="badge-review">REVUE REQUISE</span>
                  : <span className="badge-refused">REFUSÉ</span>
                }
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Score</span>
                  <span className="font-bold">{assessment.score} / 1000</span>
                </div>
                <div className="score-gauge">
                  <div
                    className="score-gauge-fill"
                    style={{
                      width: `${(assessment.score / 1000) * 100}%`,
                      background: assessment.score >= 750 ? '#168A62' : assessment.score >= 450 ? '#C47B12' : '#C2414B'
                    }}
                  />
                </div>
              </div>
              {assessment.top_factors && assessment.top_factors.length > 0 && (
                <div className="card">
                  <h4 className="font-semibold mb-3">Facteurs de risque</h4>
                  <div className="space-y-2">
                    {assessment.top_factors.filter(f => f.direction === 'negative').slice(0, 5).map((f, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded-lg text-sm bg-danger/5">
                        <span>{f.label}</span>
                        <span className="font-medium text-danger">{f.impact.toFixed(3)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {assessment.counter_proposals && assessment.counter_proposals.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3">Alternatives possibles</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {assessment.counter_proposals.map((proposal, i) => (
                      <button
                        key={i}
                        className="card text-left hover:border-primary hover:shadow-md transition-all cursor-pointer"
                        onClick={() => handleCounterProposal(proposal)}
                      >
                        <div className="font-semibold text-primary mb-1">{proposal.label}</div>
                        <div className="text-sm text-text-secondary">
                          {proposal.amount.toLocaleString()} FCFA · {proposal.duration} mois
                        </div>
                        <div className="text-sm font-medium mt-1">Score : {proposal.score}/1000</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <button className="btn-secondary" onClick={() => setStep(1)}>Retour</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
