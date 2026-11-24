import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import type { ShapFactor } from '../../types/assessment'

export default function ShapBarChart({ factors }: { factors: ShapFactor[] }) {
  const data = factors.map(f => ({
    name: f.label.length > 15 ? f.label.slice(0, 15) + '...' : f.label,
    impact: f.impact,
    direction: f.direction,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(v: number) => v.toFixed(4)} />
        <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.direction === 'positive' ? '#168A62' : '#C2414B'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}