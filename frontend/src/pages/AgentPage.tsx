import { useState } from 'react'
import ScoringLoader from '../components/scoring/ScoringLoader'
import { scoreCustom } from '../api/assessments'
import type { Assessment, CounterProposal } from '../types/assessment'

// ── All 35 model features grouped by section ──────────────────────────────────
interface FormState {
  // Identity (not sent to model)
  nom: string
  prenom: string
  telephone: string
  numero_mobile_money: string

  // Section A — Profil personnel
  genre: 'Homme' | 'Femme'
  age: number
  niveau_education: 'Aucun' | 'Primaire' | 'Secondaire' | 'Supérieur'
  situation_familiale: 'Célibataire' | 'Marié(e)' | 'Divorcé(e)' | 'Veuf(ve)'
  departement: string
  stabilite_lieu_vie: number  // 0–1

  // Section B — Activité économique
  secteur_activite: 'Vendeuse' | 'Revendeuse en détail' | 'Revendeuse en gros' | 'Autre petit commerce'
  anciennete_activite_mois: number
  proprietaire_local: 0 | 1
  nombre_employes: number
  score_aptitude_entrepreneuriale: number  // 0–100
  score_integrite: number                 // 0–1
  locus_controle_interne: number          // 0–10
  indicateur_jour_marche: 0 | 1
  proximite_marche_km: number
  membre_groupement_pro: 0 | 1

  // Section C — Revenus & Dépenses
  revenu_mensuel_declare: number
  depenses_mensuelles: number
  solde_moyen_compte: number
  tendance_solde_3m: number  // -1 à +1

  // Section D — Activité mobile money
  anciennete_ligne_mois: number
  nb_transactions_mois: number
  volume_depots_moyen: number
  volume_retraits_moyen: number
  regularite_depots_ecart_type: number  // 0–1
  nb_contreparties_distinctes: number
  part_transferts_marchands: number     // 0–1
  nb_transactions_echouees: number
  frequence_recharges_mois: number
  montant_moyen_recharge: number
  nb_contacts_distincts: number

  // Section E — Capital social (Tontine)
  membre_tontine: 0 | 1
  anciennete_tontine_mois: number
  regularite_cotisations_tontine: number  // 0–1
  montant_moyen_cotisation: number
  deja_beneficiaire_tour: 0 | 1

  // Section F — Demande
  premiere_fois: 0 | 1
  montant_demande: number
  duree_credit_mois: number
  garantie: number  // 0–1
}

const DEFAULT_FORM: FormState = {
  nom: '', prenom: '', telephone: '', numero_mobile_money: '',
  genre: 'Femme',
  age: 32,
  niveau_education: 'Primaire',
  situation_familiale: 'Marié(e)',
  departement: 'Littoral',
  stabilite_lieu_vie: 0.8,
  secteur_activite: 'Revendeuse en détail',
  anciennete_activite_mois: 24,
  proprietaire_local: 0,
  nombre_employes: 1,
  score_aptitude_entrepreneuriale: 60,
  score_integrite: 0.75,
  locus_controle_interne: 6,
  indicateur_jour_marche: 1,
  proximite_marche_km: 2,
  membre_groupement_pro: 0,
  revenu_mensuel_declare: 100000,
  depenses_mensuelles: 65000,
  solde_moyen_compte: 80000,
  tendance_solde_3m: 0.05,
  anciennete_ligne_mois: 24,
  nb_transactions_mois: 25,
  volume_depots_moyen: 60000,
  volume_retraits_moyen: 40000,
  regularite_depots_ecart_type: 0.3,
  nb_contreparties_distinctes: 12,
  part_transferts_marchands: 0.2,
  nb_transactions_echouees: 1,
  frequence_recharges_mois: 4,
  montant_moyen_recharge: 500,
  nb_contacts_distincts: 20,
  membre_tontine: 1,
  anciennete_tontine_mois: 12,
  regularite_cotisations_tontine: 0.85,
  montant_moyen_cotisation: 2000,
  deja_beneficiaire_tour: 0,
  premiere_fois: 0,
  montant_demande: 100000,
  duree_credit_mois: 6,
  garantie: 0,
}

const DEPARTEMENTS = [
  'Alibori','Atacora','Atlantique','Borgou','Collines',
  'Couffo','Donga','Littoral','Mono','Ouémé','Plateau','Zou'
]

function buildFeatures(form: FormState): Record<string, number> {
  const f: Record<string, number> = {
    age: form.age,
    anciennete_activite_mois: form.anciennete_activite_mois,
    revenu_mensuel_declare: form.revenu_mensuel_declare,
    depenses_mensuelles: form.depenses_mensuelles,
    proprietaire_local: form.proprietaire_local,
    nombre_employes: form.nombre_employes,
    nb_transactions_mois: form.nb_transactions_mois,
    volume_depots_moyen: form.volume_depots_moyen,
    volume_retraits_moyen: form.volume_retraits_moyen,
    solde_moyen_compte: form.solde_moyen_compte,
    tendance_solde_3m: form.tendance_solde_3m,
    regularite_depots_ecart_type: form.regularite_depots_ecart_type,
    nb_contreparties_distinctes: form.nb_contreparties_distinctes,
    part_transferts_marchands: form.part_transferts_marchands,
    nb_transactions_echouees: form.nb_transactions_echouees,
    frequence_recharges_mois: form.frequence_recharges_mois,
    montant_moyen_recharge: form.montant_moyen_recharge,
    anciennete_ligne_mois: form.anciennete_ligne_mois,
    nb_contacts_distincts: form.nb_contacts_distincts,
    stabilite_lieu_vie: form.stabilite_lieu_vie,
    membre_tontine: form.membre_tontine,
    anciennete_tontine_mois: form.anciennete_tontine_mois,
    regularite_cotisations_tontine: form.regularite_cotisations_tontine,
    montant_moyen_cotisation: form.montant_moyen_cotisation,
    deja_beneficiaire_tour: form.deja_beneficiaire_tour,
    score_aptitude_entrepreneuriale: form.score_aptitude_entrepreneuriale,
    score_integrite: form.score_integrite,
    locus_controle_interne: form.locus_controle_interne,
    proximite_marche_km: form.proximite_marche_km,
    indicateur_jour_marche: form.indicateur_jour_marche,
    membre_groupement_pro: form.membre_groupement_pro,
    premiere_fois: form.premiere_fois,
    montant_demande: form.montant_demande,
    duree_credit_mois: form.duree_credit_mois,
    garantie: form.garantie,
    // One-hot: genre
    genre_Homme: form.genre === 'Homme' ? 1 : 0,
    // One-hot: niveau_education
    niveau_education_Primaire:  form.niveau_education === 'Primaire'  ? 1 : 0,
    niveau_education_Secondaire: form.niveau_education === 'Secondaire' ? 1 : 0,
    'niveau_education_Supérieur': form.niveau_education === 'Supérieur' ? 1 : 0,
    // One-hot: situation_familiale
    'situation_familiale_Divorcé(e)': form.situation_familiale === 'Divorcé(e)' ? 1 : 0,
    'situation_familiale_Marié(e)':   form.situation_familiale === 'Marié(e)'   ? 1 : 0,
    'situation_familiale_Veuf(ve)':   form.situation_familiale === 'Veuf(ve)'   ? 1 : 0,
    // One-hot: departement
    departement_Atacora:    form.departement === 'Atacora'    ? 1 : 0,
    departement_Atlantique: form.departement === 'Atlantique' ? 1 : 0,
    departement_Borgou:     form.departement === 'Borgou'     ? 1 : 0,
    departement_Collines:   form.departement === 'Collines'   ? 1 : 0,
    departement_Couffo:     form.departement === 'Couffo'     ? 1 : 0,
    departement_Donga:      form.departement === 'Donga'      ? 1 : 0,
    departement_Littoral:   form.departement === 'Littoral'   ? 1 : 0,
    departement_Mono:       form.departement === 'Mono'       ? 1 : 0,
    'departement_Ouémé':    form.departement === 'Ouémé'      ? 1 : 0,
    departement_Plateau:    form.departement === 'Plateau'    ? 1 : 0,
    departement_Zou:        form.departement === 'Zou'        ? 1 : 0,
    // One-hot: secteur_activite
    'secteur_activite_Autre petit commerce':  form.secteur_activite === 'Autre petit commerce'  ? 1 : 0,
    'secteur_activite_Revendeuse en détail':  form.secteur_activite === 'Revendeuse en détail'  ? 1 : 0,
    'secteur_activite_Revendeuse en gros':    form.secteur_activite === 'Revendeuse en gros'    ? 1 : 0,
    secteur_activite_Vendeuse:                form.secteur_activite === 'Vendeuse'              ? 1 : 0,
  }
  return f
}

const STEPPER_LABELS = ['Informations client', 'Traitement', 'Résultat']

// ── Reusable field components ─────────────────────────────────────────────────
const F = ({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) => (
  <div>
    <label className="block text-sm font-medium mb-1">{label}</label>
    {children}
    {hint && <p className="text-xs text-text-secondary mt-1">{hint}</p>}
  </div>
)

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h3 className="font-semibold text-primary text-sm uppercase tracking-wide border-b border-border pb-2 mt-6 mb-4">{children}</h3>
)

export default function AgentPage() {
  const [step, setStep]           = useState(1)
  const [form, setForm]           = useState<FormState>(DEFAULT_FORM)
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<string | null>(null)
  const [lastFeatures, setLastFeatures] = useState<Record<string, number>>({})

  const set = <K extends keyof FormState>(key: K, val: FormState[K]) =>
    setForm(f => ({ ...f, [key]: val }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (form.montant_demande > 300000) { alert('Montant max : 300 000 FCFA'); return }
    setError(null); setLoading(true); setStep(2)
    const features = buildFeatures(form)
    setLastFeatures(features)
    try {
      const result = await scoreCustom(features)
      setAssessment(result); setStep(3)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'API inaccessible'); setStep(1)
    } finally { setLoading(false) }
  }

  const handleCounterProposal = async (proposal: CounterProposal) => {
    setLoading(true); setStep(2)
    const pf = { ...lastFeatures, montant_demande: proposal.amount, duree_credit_mois: proposal.duration }
    try {
      const result = await scoreCustom(pf)
      setAssessment(result); setStep(3)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Erreur'); setStep(3)
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold">Nouvelle demande de crédit</h2>

      {/* Stepper */}
      <div className="flex items-center gap-2">
        {STEPPER_LABELS.map((label, i) => {
          const num = i + 1; const active = step === num; const done = step > num
          return (
            <div key={num} className="flex items-center gap-2 flex-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
                done ? 'bg-primary text-white' : active ? 'bg-primary text-white ring-4 ring-primary/20' : 'bg-gray-100 text-text-secondary'
              }`}>{done ? '✓' : num}</div>
              <span className={`text-sm ${active ? 'font-semibold text-primary' : 'text-text-secondary'}`}>{label}</span>
              {i < STEPPER_LABELS.length - 1 && <div className={`flex-1 h-0.5 ${done ? 'bg-primary' : 'bg-gray-200'}`} />}
            </div>
          )
        })}
      </div>

      {/* ── STEP 1 — Full form ── */}
      {step === 1 && (
        <form onSubmit={handleSubmit} className="card space-y-2">
          {error && <div className="p-3 rounded-lg bg-danger/10 border border-danger text-danger text-sm">{error}</div>}

          {/* Identité */}
          <SectionTitle>Identité du client</SectionTitle>
          <div className="grid grid-cols-2 gap-4">
            <F label="Nom *"><input required type="text" value={form.nom} onChange={e => set('nom', e.target.value)} className="input-field" /></F>
            <F label="Prénom *"><input required type="text" value={form.prenom} onChange={e => set('prenom', e.target.value)} className="input-field" /></F>
            <F label="Téléphone"><input type="text" value={form.telephone} onChange={e => set('telephone', e.target.value)} className="input-field" /></F>
            <F label="N° Mobile Money"><input type="text" value={form.numero_mobile_money} onChange={e => set('numero_mobile_money', e.target.value)} className="input-field" /></F>
          </div>

          {/* Profil personnel */}
          <SectionTitle>Profil personnel</SectionTitle>
          <div className="grid grid-cols-2 gap-4">
            <F label="Genre">
              <select value={form.genre} onChange={e => set('genre', e.target.value as any)} className="input-field">
                <option value="Femme">Femme</option>
                <option value="Homme">Homme</option>
              </select>
            </F>
            <F label="Âge"><input type="number" min={18} max={80} value={form.age} onChange={e => set('age', +e.target.value)} className="input-field" /></F>
            <F label="Niveau d'éducation">
              <select value={form.niveau_education} onChange={e => set('niveau_education', e.target.value as any)} className="input-field">
                <option value="Aucun">Aucun</option>
                <option value="Primaire">Primaire</option>
                <option value="Secondaire">Secondaire</option>
                <option value="Supérieur">Supérieur</option>
              </select>
            </F>
            <F label="Situation familiale">
              <select value={form.situation_familiale} onChange={e => set('situation_familiale', e.target.value as any)} className="input-field">
                <option value="Célibataire">Célibataire</option>
                <option value="Marié(e)">Marié(e)</option>
                <option value="Divorcé(e)">Divorcé(e)</option>
                <option value="Veuf(ve)">Veuf(ve)</option>
              </select>
            </F>
            <F label="Département">
              <select value={form.departement} onChange={e => set('departement', e.target.value)} className="input-field">
                {DEPARTEMENTS.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </F>
            <F label="Stabilité lieu de vie (0–1)" hint="0 = nomade · 1 = très stable">
              <input type="number" min={0} max={1} step={0.1} value={form.stabilite_lieu_vie} onChange={e => set('stabilite_lieu_vie', +e.target.value)} className="input-field" />
            </F>
          </div>

          {/* Activité économique */}
          <SectionTitle>Activité économique</SectionTitle>
          <div className="grid grid-cols-2 gap-4">
            <F label="Secteur d'activité">
              <select value={form.secteur_activite} onChange={e => set('secteur_activite', e.target.value as any)} className="input-field">
                <option value="Vendeuse">Vendeuse</option>
                <option value="Revendeuse en détail">Revendeuse en détail</option>
                <option value="Revendeuse en gros">Revendeuse en gros</option>
                <option value="Autre petit commerce">Autre petit commerce</option>
              </select>
            </F>
            <F label="Ancienneté activité (mois)"><input type="number" min={0} value={form.anciennete_activite_mois} onChange={e => set('anciennete_activite_mois', +e.target.value)} className="input-field" /></F>
            <F label="Propriétaire du local">
              <select value={form.proprietaire_local} onChange={e => set('proprietaire_local', +e.target.value as 0|1)} className="input-field">
                <option value={0}>Non</option>
                <option value={1}>Oui</option>
              </select>
            </F>
            <F label="Nombre d'employés"><input type="number" min={0} value={form.nombre_employes} onChange={e => set('nombre_employes', +e.target.value)} className="input-field" /></F>
            <F label="Aptitude entrepreneuriale (0–100)" hint="Auto-évaluation ou estimation agent">
              <input type="number" min={0} max={100} value={form.score_aptitude_entrepreneuriale} onChange={e => set('score_aptitude_entrepreneuriale', +e.target.value)} className="input-field" />
            </F>
            <F label="Score d'intégrité (0–1)" hint="Réputation dans la communauté">
              <input type="number" min={0} max={1} step={0.05} value={form.score_integrite} onChange={e => set('score_integrite', +e.target.value)} className="input-field" />
            </F>
            <F label="Locus de contrôle (0–10)" hint="0 = fataliste · 10 = très autonome">
              <input type="number" min={0} max={10} value={form.locus_controle_interne} onChange={e => set('locus_controle_interne', +e.target.value)} className="input-field" />
            </F>
            <F label="Proximité du marché (km)"><input type="number" min={0} step={0.5} value={form.proximite_marche_km} onChange={e => set('proximite_marche_km', +e.target.value)} className="input-field" /></F>
            <F label="Vend le jour du marché">
              <select value={form.indicateur_jour_marche} onChange={e => set('indicateur_jour_marche', +e.target.value as 0|1)} className="input-field">
                <option value={0}>Non</option>
                <option value={1}>Oui</option>
              </select>
            </F>
            <F label="Membre groupement pro">
              <select value={form.membre_groupement_pro} onChange={e => set('membre_groupement_pro', +e.target.value as 0|1)} className="input-field">
                <option value={0}>Non</option>
                <option value={1}>Oui</option>
              </select>
            </F>
          </div>

          {/* Revenus & Dépenses */}
          <SectionTitle>Revenus & Dépenses</SectionTitle>
          <div className="grid grid-cols-2 gap-4">
            <F label="Revenu mensuel déclaré (FCFA)"><input type="number" min={0} step={5000} value={form.revenu_mensuel_declare} onChange={e => set('revenu_mensuel_declare', +e.target.value)} className="input-field" /></F>
            <F label="Dépenses mensuelles (FCFA)"><input type="number" min={0} step={5000} value={form.depenses_mensuelles} onChange={e => set('depenses_mensuelles', +e.target.value)} className="input-field" /></F>
            <F label="Solde moyen du compte (FCFA)"><input type="number" min={0} step={5000} value={form.solde_moyen_compte} onChange={e => set('solde_moyen_compte', +e.target.value)} className="input-field" /></F>
            <F label="Tendance solde 3 mois (-1 à +1)" hint="-1 = fort déclin · +1 = forte croissance">
              <input type="number" min={-1} max={1} step={0.05} value={form.tendance_solde_3m} onChange={e => set('tendance_solde_3m', +e.target.value)} className="input-field" />
            </F>
          </div>

          {/* Mobile Money */}
          <SectionTitle>Activité Mobile Money</SectionTitle>
          <div className="grid grid-cols-2 gap-4">
            <F label="Ancienneté ligne (mois)"><input type="number" min={0} value={form.anciennete_ligne_mois} onChange={e => set('anciennete_ligne_mois', +e.target.value)} className="input-field" /></F>
            <F label="Nb transactions/mois"><input type="number" min={0} value={form.nb_transactions_mois} onChange={e => set('nb_transactions_mois', +e.target.value)} className="input-field" /></F>
            <F label="Volume moyen dépôts (FCFA)"><input type="number" min={0} step={5000} value={form.volume_depots_moyen} onChange={e => set('volume_depots_moyen', +e.target.value)} className="input-field" /></F>
            <F label="Volume moyen retraits (FCFA)"><input type="number" min={0} step={5000} value={form.volume_retraits_moyen} onChange={e => set('volume_retraits_moyen', +e.target.value)} className="input-field" /></F>
            <F label="Régularité dépôts (0–1)" hint="0 = très irrégulier · 1 = très régulier">
              <input type="number" min={0} max={1} step={0.05} value={form.regularite_depots_ecart_type} onChange={e => set('regularite_depots_ecart_type', +e.target.value)} className="input-field" />
            </F>
            <F label="Contreparties distinctes"><input type="number" min={0} value={form.nb_contreparties_distinctes} onChange={e => set('nb_contreparties_distinctes', +e.target.value)} className="input-field" /></F>
            <F label="Part transferts marchands (0–1)" hint="Part des tx vers commerçants">
              <input type="number" min={0} max={1} step={0.05} value={form.part_transferts_marchands} onChange={e => set('part_transferts_marchands', +e.target.value)} className="input-field" />
            </F>
            <F label="Transactions échouées"><input type="number" min={0} value={form.nb_transactions_echouees} onChange={e => set('nb_transactions_echouees', +e.target.value)} className="input-field" /></F>
            <F label="Fréquence recharges/mois"><input type="number" min={0} value={form.frequence_recharges_mois} onChange={e => set('frequence_recharges_mois', +e.target.value)} className="input-field" /></F>
            <F label="Montant moyen recharge (FCFA)"><input type="number" min={0} step={100} value={form.montant_moyen_recharge} onChange={e => set('montant_moyen_recharge', +e.target.value)} className="input-field" /></F>
            <F label="Contacts distincts"><input type="number" min={0} value={form.nb_contacts_distincts} onChange={e => set('nb_contacts_distincts', +e.target.value)} className="input-field" /></F>
          </div>

          {/* Tontine */}
          <SectionTitle>Capital social — Tontine</SectionTitle>
          <div className="grid grid-cols-2 gap-4">
            <F label="Membre d'une tontine">
              <select value={form.membre_tontine} onChange={e => set('membre_tontine', +e.target.value as 0|1)} className="input-field">
                <option value={0}>Non</option>
                <option value={1}>Oui</option>
              </select>
            </F>
            {form.membre_tontine === 1 && <>
              <F label="Ancienneté tontine (mois)"><input type="number" min={0} value={form.anciennete_tontine_mois} onChange={e => set('anciennete_tontine_mois', +e.target.value)} className="input-field" /></F>
              <F label="Régularité cotisations (0–1)"><input type="number" min={0} max={1} step={0.05} value={form.regularite_cotisations_tontine} onChange={e => set('regularite_cotisations_tontine', +e.target.value)} className="input-field" /></F>
              <F label="Montant moyen cotisation (FCFA)"><input type="number" min={0} step={500} value={form.montant_moyen_cotisation} onChange={e => set('montant_moyen_cotisation', +e.target.value)} className="input-field" /></F>
              <F label="Déjà bénéficiaire du tour">
                <select value={form.deja_beneficiaire_tour} onChange={e => set('deja_beneficiaire_tour', +e.target.value as 0|1)} className="input-field">
                  <option value={0}>Non</option>
                  <option value={1}>Oui</option>
                </select>
              </F>
            </>}
          </div>

          {/* Demande */}
          <SectionTitle>Demande de crédit</SectionTitle>
          <div className="grid grid-cols-2 gap-4">
            <F label="Première demande">
              <select value={form.premiere_fois} onChange={e => set('premiere_fois', +e.target.value as 0|1)} className="input-field">
                <option value={0}>Non</option>
                <option value={1}>Oui — première fois</option>
              </select>
            </F>
            <F label="Montant demandé (FCFA)"><input type="number" min={5000} max={300000} step={5000} value={form.montant_demande} onChange={e => set('montant_demande', +e.target.value)} className="input-field" /></F>
            <F label="Durée souhaitée (mois)"><input type="number" min={1} max={24} value={form.duree_credit_mois} onChange={e => set('duree_credit_mois', +e.target.value)} className="input-field" /></F>
            <F label="Garantie (0–1)" hint="0 = aucune · 0.5 = partielle · 1 = totale">
              <input type="number" min={0} max={1} step={0.1} value={form.garantie} onChange={e => set('garantie', +e.target.value)} className="input-field" />
            </F>
          </div>

          <div className="pt-4">
            <button type="submit" className="btn-primary w-full text-base py-3">
              Soumettre la demande
            </button>
          </div>
        </form>
      )}

      {/* ── STEP 2 — Loading ── */}
      {step === 2 && loading && <ScoringLoader />}

      {/* ── STEP 3 — Result ── */}
      {step === 3 && assessment && (
        <div className="space-y-6">

          {/* ACCEPTED */}
          {assessment.decision === 'ACCEPTED' && (
            <div className="space-y-5">
              <div className="text-center"><span className="badge-accepted">ACCEPTÉ</span></div>
              <div>
                <div className="flex justify-between text-sm mb-1"><span>Score</span><span className="font-bold">{assessment.score} / 1000</span></div>
                <div className="score-gauge">
                  <div className="score-gauge-fill" style={{ width: `${(assessment.score/1000)*100}%`, background: assessment.score >= 750 ? '#168A62' : '#C47B12' }} />
                </div>
              </div>
              {assessment.ml_score !== undefined && (
                <p className="text-sm text-text-secondary text-center">
                  Score ML : {assessment.ml_score}/1000 ({Math.round((assessment.score_weights?.ml ?? 0.55)*100)}%) · Score Règles : {assessment.business_score}/1000 ({Math.round((assessment.score_weights?.rules ?? 0.45)*100)}%)
                </p>
              )}
              <div className="card">
                <h4 className="font-semibold mb-3">Conditions</h4>
                <dl className="grid grid-cols-2 gap-2 text-sm">
                  <dt className="text-text-secondary">Montant</dt><dd className="font-medium">{form.montant_demande.toLocaleString()} FCFA</dd>
                  <dt className="text-text-secondary">Durée</dt><dd className="font-medium">{form.duree_credit_mois} mois</dd>
                  {assessment.teg !== undefined && <><dt className="text-text-secondary">TEG</dt><dd className="font-medium">{(assessment.teg*100).toFixed(2)}%</dd></>}
                </dl>
              </div>
              <button className="btn-secondary w-full" onClick={() => alert('Fonctionnalité à venir')}>Générer le contrat</button>
              <button className="btn-secondary w-full" onClick={() => { setStep(1); setAssessment(null) }}>Nouvelle demande</button>
            </div>
          )}

          {/* REFUSED_REGULATORY */}
          {assessment.decision === 'REFUSED_REGULATORY' && (
            <div className="space-y-4">
              <div className="text-center"><span className="badge-refused">REFUSÉ — MOTIF RÉGLEMENTAIRE</span></div>
              <div className="p-4 rounded-xl bg-danger/10 border-2 border-danger text-danger text-sm">
                Le TEG de {assessment.teg ? (assessment.teg*100).toFixed(2) : '?'}% dépasse le plafond légal de 24% fixé par la BCEAO.
              </div>
              <button className="btn-secondary" onClick={() => setStep(1)}>Retour</button>
            </div>
          )}

          {/* REFUSED_RISK / MANUAL_REVIEW */}
          {(assessment.decision === 'REFUSED_RISK' || assessment.decision === 'MANUAL_REVIEW' || !assessment.decision) && (
            <div className="space-y-5">
              <div className="text-center">
                {assessment.decision === 'MANUAL_REVIEW'
                  ? <span className="badge-review">REVUE REQUISE</span>
                  : <span className="badge-refused">REFUSÉ</span>}
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1"><span>Score</span><span className="font-bold">{assessment.score} / 1000</span></div>
                <div className="score-gauge">
                  <div className="score-gauge-fill" style={{ width: `${(assessment.score/1000)*100}%`, background: assessment.score >= 500 ? '#C47B12' : '#C2414B' }} />
                </div>
              </div>
              {assessment.top_factors?.filter(f => f.direction === 'negative').length > 0 && (
                <div className="card">
                  <h4 className="font-semibold mb-3">Principaux facteurs de risque</h4>
                  <div className="space-y-2">
                    {assessment.top_factors.filter(f => f.direction === 'negative').slice(0, 5).map((f, i) => (
                      <div key={i} className="flex justify-between p-2 rounded-lg text-sm bg-danger/5">
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
                    {assessment.counter_proposals.map((p, i) => (
                      <button key={i} className="card text-left hover:border-primary hover:shadow-md transition-all cursor-pointer" onClick={() => handleCounterProposal(p)}>
                        <div className="font-semibold text-primary mb-1">{p.label}</div>
                        <div className="text-sm text-text-secondary">{p.amount.toLocaleString()} FCFA · {p.duration} mois</div>
                        <div className="text-sm font-medium mt-1">Score : {p.score}/1000</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex gap-3">
                <button className="btn-secondary flex-1" onClick={() => setStep(1)}>Modifier</button>
                <button className="btn-secondary flex-1" onClick={() => { setStep(1); setAssessment(null); setForm(DEFAULT_FORM) }}>Nouvelle demande</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
