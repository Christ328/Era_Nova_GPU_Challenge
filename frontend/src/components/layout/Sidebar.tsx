import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Users, CreditCard, Cpu } from 'lucide-react'

const links = [
  { to: '/', label: 'Tableau de bord', icon: LayoutDashboard, end: true },
  { to: '/merchants', label: 'Commerçants', icon: Users, end: false },
  { to: '/benchmark', label: 'Benchmark GPU', icon: Cpu, end: false },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-lg font-bold text-primary">GPU Credit Scoring</h1>
        <p className="text-xs text-text-secondary mt-1">Évaluation risque commerçants</p>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
            }
          >
            <Icon size={18} />
            <span className="text-sm">{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-border">
        <span className="badge bg-gpu/10 text-gpu">GPU Accelerated</span>
        <p className="text-xs text-text-secondary mt-2">v1.0.0</p>
      </div>
    </aside>
  )
}