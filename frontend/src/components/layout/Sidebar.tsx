import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Users, CreditCard, Cpu, Shield, X } from 'lucide-react'

const links = [
  { to: '/', label: 'Tableau de bord', icon: LayoutDashboard, end: true },
  { to: '/merchants', label: 'Commerçants', icon: Users, end: false },
  { to: '/custom', label: 'Évaluation manuelle', icon: CreditCard, end: false },
  { to: '/rules', label: 'Règles métier', icon: Shield, end: false },
  { to: '/benchmark', label: 'Benchmark GPU', icon: Cpu, end: false },
]

interface SidebarProps {
  open: boolean
  onClose: () => void
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <aside
      className={[
        'bg-surface border-r border-border flex flex-col',
        // Desktop: always visible, static width
        'md:static md:translate-x-0 md:w-64 md:z-auto',
        // Mobile: fixed drawer sliding in from left
        'fixed inset-y-0 left-0 z-50 w-64 transition-transform duration-300',
        open ? 'translate-x-0' : '-translate-x-full',
      ].join(' ')}
    >
      <div className="p-6 border-b border-border flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-primary">GPU Credit Scoring</h1>
          <p className="text-xs text-text-secondary mt-1">Évaluation risque commerçants</p>
        </div>
        {/* Close button — only shown on mobile */}
        <button
          className="md:hidden p-1 rounded hover:bg-border"
          onClick={onClose}
          aria-label="Fermer le menu"
        >
          <X size={20} />
        </button>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={onClose}
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
