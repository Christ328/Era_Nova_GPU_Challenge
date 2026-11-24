interface Props {
  riskLevel: string
  confidence: string
}

export default function RiskBadge({ riskLevel, confidence }: Props) {
  const riskColors: Record<string, string> = {
    VERY_HIGH: 'bg-danger text-white',
    HIGH: 'bg-warning text-white',
    MODERATE: 'bg-warning text-white',
    LOW: 'bg-success text-white',
    VERY_LOW: 'bg-success text-white',
  }

  const confColors: Record<string, string> = {
    LOW: 'text-danger',
    MEDIUM: 'text-warning',
    HIGH: 'text-success',
  }

  return (
    <div className="card">
      <p className="text-sm text-text-secondary mb-2">Niveau de risque</p>
      <span className={`badge ${riskColors[riskLevel] || 'bg-gray-200'}`}>
        {riskLevel}
      </span>
      <div className="mt-4">
        <p className="text-sm text-text-secondary mb-1">Confiance</p>
        <span className={`font-semibold ${confColors[confidence] || ''}`}>
          {confidence}
        </span>
      </div>
    </div>
  )
}