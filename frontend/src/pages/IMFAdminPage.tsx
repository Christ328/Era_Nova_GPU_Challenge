import { useState, useEffect } from 'react'
import { getIMFConfig, updateIMFConfig } from '../api/imf'

export default function IMFAdminPage() {
  const [config, setConfig] = useState({
    nom_imf: '',
    taux_interet_annuel: 18,
    frais_dossier: 5000,
    taux_assurance: 1,
    plafond_primo: 50000,
    plafond_regulier: 300000,
    duree_min: 1,
    duree_max: 60,
    score_auto_accept: 700,
    score_manual_review: 500,
    taux_effort_max: 40,
    garantie_obligatoire_seuil: 100000,
    bonus_tontine: 50,
    bonus_garantie: 30,
    malus_primo: -20,
    malus_fraude: -200,
    poids_tendance: 30,
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    getIMFConfig().then(data => {
      if (data) setConfig(prev => ({ ...prev, ...data }))
    }).catch(() => {
      // endpoint may not exist yet — ignore silently
    })
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)
    try {
      await updateIMFConfig(1, config)
      setMessage({ type: 'success', text: 'Configuration sauvegardée avec succès.' })
    } catch {
      setMessage({ type: 'error', text: 'Erreur lors de la sauvegarde.' })
    } finally {
      setSaving(false)
    }
  }

  const set = (key: keyof typeof config, value: number | string) =>
    setConfig(prev => ({ ...prev, [key]: value }))

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-2xl font-bold">Configuration IMF</h2>
        <p className="text-text-secondary mt-1">Paramètres de politique de crédit</p>
      </div>

      {/* Section A — Paramètres financiers */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-lg">Paramètres financiers</h3>

        <div>
          <label className="block text-sm font-medium mb-1">Nom IMF</label>
          <input
            type="text"
            value={config.nom_imf}
            onChange={e => set('nom_imf', e.target.value)}
            className="input-field"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Taux d'intérêt annuel %</label>
            <input
              type="number"
              min={0}
              max={100}
              step={0.1}
              value={config.taux_interet_annuel}
              onChange={e => set('taux_interet_annuel', parseFloat(e.target.value))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Frais de dossier (FCFA)</label>
            <input
              type="number"
              min={0}
              value={config.frais_dossier}
              onChange={e => set('frais_dossier', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Taux d'assurance %</label>
            <input
              type="number"
              min={0}
              max={10}
              step={0.1}
              value={config.taux_assurance}
              onChange={e => set('taux_assurance', parseFloat(e.target.value))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Plafond primo-emprunteur (FCFA)</label>
            <input
              type="number"
              min={0}
              value={config.plafond_primo}
              onChange={e => set('plafond_primo', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Plafond client régulier (FCFA)</label>
            <input
              type="number"
              min={0}
              value={config.plafond_regulier}
              onChange={e => set('plafond_regulier', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-sm font-medium mb-1">Durée min (mois)</label>
              <input
                type="number"
                min={1}
                value={config.duree_min}
                onChange={e => set('duree_min', parseInt(e.target.value))}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Durée max (mois)</label>
              <input
                type="number"
                min={1}
                value={config.duree_max}
                onChange={e => set('duree_max', parseInt(e.target.value))}
                className="input-field"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Section B — Politique de risque */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-lg">Politique de risque</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Score d'acceptation automatique /1000</label>
            <input
              type="number"
              min={0}
              max={1000}
              value={config.score_auto_accept}
              onChange={e => set('score_auto_accept', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Score de revue manuelle /1000</label>
            <input
              type="number"
              min={0}
              max={1000}
              value={config.score_manual_review}
              onChange={e => set('score_manual_review', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Taux d'effort maximum %</label>
            <input
              type="number"
              min={0}
              max={100}
              value={config.taux_effort_max}
              onChange={e => set('taux_effort_max', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Garantie obligatoire au-delà de X (FCFA)</label>
            <input
              type="number"
              min={0}
              value={config.garantie_obligatoire_seuil}
              onChange={e => set('garantie_obligatoire_seuil', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
        </div>
      </div>

      {/* Section C — Bonus/Malus */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-lg">Bonus / Malus</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Bonus Tontine (+pts)</label>
            <input
              type="number"
              value={config.bonus_tontine}
              onChange={e => set('bonus_tontine', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Bonus Garantie (+pts)</label>
            <input
              type="number"
              value={config.bonus_garantie}
              onChange={e => set('bonus_garantie', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Malus Primo-emprunteur (pts négatif)</label>
            <input
              type="number"
              value={config.malus_primo}
              onChange={e => set('malus_primo', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Malus Fraude (pts négatif)</label>
            <input
              type="number"
              value={config.malus_fraude}
              onChange={e => set('malus_fraude', parseInt(e.target.value))}
              className="input-field"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Poids tendance % : <span className="font-bold text-primary">{config.poids_tendance}%</span>
          </label>
          <input
            type="range"
            min={0}
            max={100}
            value={config.poids_tendance}
            onChange={e => set('poids_tendance', parseInt(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      <div className="space-y-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary w-full"
        >
          {saving ? 'Sauvegarde...' : 'Sauvegarder la configuration'}
        </button>

        {message && (
          <div className={`p-3 rounded-lg text-sm font-medium ${
            message.type === 'success'
              ? 'bg-success/10 border border-success text-success'
              : 'bg-danger/10 border border-danger text-danger'
          }`}>
            {message.text}
          </div>
        )}
      </div>
    </div>
  )
}
