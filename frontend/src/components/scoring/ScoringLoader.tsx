import { useEffect, useState } from 'react'

const STEPS = [
  'Chargement du profil…',
  'Normalisation des données…',
  'Prédiction XGBoost…',
  'Calcul des valeurs SHAP…',
  'Génération de l\'analyse…',
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
    <div className="flex flex-col items-center justify-center py-16 space-y-10">

      {/* Spinning ring with GPU purple + primary blue */}
      <div className="relative w-32 h-32">
        {/* outer spinning ring */}
        <svg
          className="absolute inset-0 w-full h-full animate-spin"
          style={{ animationDuration: '1.4s' }}
          viewBox="0 0 128 128"
        >
          <circle
            cx="64" cy="64" r="56"
            fill="none"
            stroke="#E4E7EC"
            strokeWidth="10"
          />
          <circle
            cx="64" cy="64" r="56"
            fill="none"
            stroke="url(#loaderGrad)"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray="260"
            strokeDashoffset="195"
          />
          <defs>
            <linearGradient id="loaderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stopColor="#145DA0" />
              <stop offset="100%" stopColor="#6C5CE7" />
            </linearGradient>
          </defs>
        </svg>

        {/* inner pulsing dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className="w-10 h-10 rounded-full animate-pulse"
            style={{ background: 'linear-gradient(135deg, #145DA0, #6C5CE7)' }}
          />
        </div>
      </div>

      {/* Step label */}
      <div className="text-center space-y-1">
        <p className="text-lg font-semibold" style={{ color: '#172033' }}>
          Analyse en cours{dots}
        </p>
        <p
          className="text-sm transition-all duration-500"
          style={{ color: '#145DA0' }}
          key={stepIndex}
        >
          {STEPS[stepIndex]}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-64 h-1.5 rounded-full overflow-hidden" style={{ background: '#E4E7EC' }}>
        <div
          className="h-full rounded-full animate-pulse"
          style={{
            width: '60%',
            background: 'linear-gradient(90deg, #145DA0, #6C5CE7)',
            animation: 'progress-sweep 1.6s ease-in-out infinite',
          }}
        />
      </div>

      <style>{`
        @keyframes progress-sweep {
          0%   { transform: translateX(-100%); width: 60%; }
          50%  { transform: translateX(60%);  width: 60%; }
          100% { transform: translateX(170%); width: 60%; }
        }
      `}</style>
    </div>
  )
}
