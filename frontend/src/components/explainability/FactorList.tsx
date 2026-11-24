import type { ShapFactor } from '../../types/assessment'

export default function FactorList({ factors }: { factors: ShapFactor[] }) {
  return (
    <div className="space-y-2 max-h-80 overflow-y-auto">
      {factors.map((f, i) => (
        <div
          key={i}
          className={`flex items-center justify-between p-2 rounded-lg text-sm ${
            f.direction === 'positive' ? 'bg-success/5' : 'bg-danger/5'
          }`}
        >
          <div className="flex items-center gap-2">
            <span className={f.direction === 'positive' ? 'text-success' : 'text-danger'}>
              {f.direction === 'positive' ? '+' : ''}{f.impact.toFixed(4)}
            </span>
            <span>{f.label}</span>
          </div>
          <span className="text-text-secondary">
            {typeof f.value === 'number' ? f.value.toFixed(2) : f.value}
          </span>
        </div>
      ))}
    </div>
  )
}