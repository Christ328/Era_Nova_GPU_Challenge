import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { submitDecision } from '../api/assessments'

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>()
  const [decision, setDecision] = useState('approve')
  const [amount, setAmount] = useState('')
  const [duration, setDuration] = useState('')
  const [comments, setComments] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async () => {
    if (id) {
      await submitDecision(
        id,
        decision,
        amount ? parseInt(amount) : undefined,
        duration ? parseInt(duration) : undefined,
        comments || undefined
      )
      setSubmitted(true)
    }
  }

  if (submitted) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Décision enregistrée</h2>
        <div className="card">
          <p className="text-success">La décision a été enregistrée avec succès.</p>
          <Link to="/" className="btn-primary mt-4 inline-block">Retour au tableau de bord</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Revue humaine - {id}</h2>

      <div className="card max-w-2xl">
        <h3 className="font-semibold mb-4">Décision de l'agent</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Décision</label>
            <div className="flex gap-2">
              {['approve', 'modify', 'reject'].map(d => (
                <button
                  key={d}
                  onClick={() => setDecision(d)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    decision === d
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-text-primary hover:bg-gray-200'
                  }`}
                >
                  {d === 'approve' ? 'Approuver' : d === 'modify' ? 'Modifier' : 'Rejeter'}
                </button>
              ))}
            </div>
          </div>

          {decision === 'modify' && (
            <>
              <div>
                <label className="block text-sm font-medium mb-2">Montant ajusté (FCFA)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={e => setAmount(e.target.value)}
                  className="input-field"
                  placeholder="Montant"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Durée ajustée (mois)</label>
                <input
                  type="number"
                  value={duration}
                  onChange={e => setDuration(e.target.value)}
                  className="input-field"
                  placeholder="Durée"
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Commentaires</label>
            <textarea
              value={comments}
              onChange={e => setComments(e.target.value)}
              className="input-field"
              rows={3}
              placeholder="Justification..."
            />
          </div>

          <button onClick={handleSubmit} className="btn-primary">
            Enregistrer la décision
          </button>
        </div>
      </div>
    </div>
  )
}