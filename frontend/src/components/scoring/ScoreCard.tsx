interface Props {
  score: number
  riskLevel: string
}

export default function ScoreCard({ score, riskLevel }: Props) {
  const getColor = () => {
    if (score < 300) return '#C2414B'
    if (score < 450) return '#C47B12'
    if (score < 600) return '#C47B12'
    if (score < 750) return '#168A62'
    return '#168A62'
  }

  return (
    <div className="card text-center">
      <p className="text-sm text-text-secondary mb-2">Score de crédit</p>
      <div className="text-5xl font-extrabold" style={{ color: getColor() }}>
        {score}
      </div>
      <p className="text-sm text-text-secondary mt-1">/ 1000</p>
      <span
        className="badge mt-3 text-white"
        style={{ backgroundColor: getColor() }}
      >
        {riskLevel}
      </span>
    </div>
  )
}
