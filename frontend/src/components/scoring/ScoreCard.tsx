interface Props {
  score: number
  riskLevel: string
}

export default function ScoreCard({ score, riskLevel }: Props) {
  const getColor = () => {
    if (score < 30) return '#C2414B'
    if (score < 45) return '#C47B12'
    if (score < 60) return '#C47B12'
    if (score < 75) return '#168A62'
    return '#168A62'
  }

  return (
    <div className="card text-center">
      <p className="text-sm text-text-secondary mb-2">Score de crédit</p>
      <div className="text-5xl font-extrabold" style={{ color: getColor() }}>
        {score}
      </div>
      <p className="text-sm text-text-secondary mt-1">/ 100</p>
      <span
        className="badge mt-3 text-white"
        style={{ backgroundColor: getColor() }}
      >
        {riskLevel}
      </span>
    </div>
  )
}