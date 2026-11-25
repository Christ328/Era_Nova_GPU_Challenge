import { useEffect, useState } from 'react'

const STEPS = [
  'Chargement du profil…',
  'Normalisation des données…',
  'Prédiction XGBoost…',
  'Calcul des valeurs SHAP…',
  "Génération de l'analyse…",
]

export default function ScoringLoader() {
  const [stepIndex, setStepIndex] = useState(0)
  const [dots, setDots] = useState('')

  useEffect(() => {
    const stepTimer = setInterval(() => {
      setStepIndex(i => (i + 1) % STEPS.length)
    }, 900)
    const dotTimer = setInterval(() => {
      setDots(d => (d.length >= 3 ? '' : d + '.'))
    }, 350)
    return () => {
      clearInterval(stepTimer)
      clearInterval(dotTimer)
    }
  }, [])

  return (
    /* Full-screen overlay, centered */
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl px-12 py-10 flex flex-col items-center gap-8 min-w-[320px]">

        {/* Spinning arc */}
        <div className="relative w-28 h-28">
          <svg
            className="absolute inset-0 w-full h-full animate-spin"
            style={{ animationDuration: '1.4s' }}
            viewBox="0 0 112 112"
          >
            <circle cx="56" cy="56" r="48" fill="none" stroke="#E4E7EC" strokeWidth="9" />
            <circle
              cx="56" cy="56" r="48"
              fill="none"
              stroke="url(#loaderGrad)"
              strokeWidth="9"
              strokeLinecap="round"
              strokeDasharray="226"
              strokeDashoffset="170"
            />
            <defs>
              <linearGradient id="loaderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%"   stopColor="#145DA0" />
                <stop offset="100%" stopColor="#6C5CE7" />
              </linearGradient>
            </defs>
          </svg>
          {/* Inner pulsing dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="w-9 h-9 rounded-full animate-pulse"
              style={{ background: 'linear-gradient(135deg, #145DA0, #6C5CE7)' }}
            />
          </div>
        </div>

        {/* Labels */}
        <div className="text-center">
          <p className="text-lg font-semibold" style={{ color: '#172033' }}>
            Analyse en cours{dots}
          </p>
          <p
            className="text-sm mt-1"
            style={{ color: '#145DA0', minHeight: '1.25rem' }}
            key={stepIndex}
          >
            {STEPS[stepIndex]}
          </p>
        </div>

        {/* Sweeping progress bar */}
        <div className="w-56 h-1.5 rounded-full overflow-hidden" style={{ background: '#E4E7EC' }}>
          <div
            className="h-full rounded-full"
            style={{
              width: '55%',
              background: 'linear-gradient(90deg, #145DA0, #6C5CE7)',
              animation: 'sweep 1.6s ease-in-out infinite',
            }}
          />
        </div>

        <style>{`
          @keyframes sweep {
            0%   { transform: translateX(-110%); }
            100% { transform: translateX(210%); }
          }
        `}</style>
      </div>
    </div>
  )
}
