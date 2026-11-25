import { Search, Wifi, Menu } from 'lucide-react'

interface TopbarProps {
  onMenuToggle: () => void
}

export default function Topbar({ onMenuToggle }: TopbarProps) {
  return (
    <header className="h-14 bg-surface border-b border-border flex items-center px-4 md:px-6 gap-3">
      {/* Hamburger — mobile only */}
      <button
        className="md:hidden p-1 rounded hover:bg-border flex-shrink-0"
        onClick={onMenuToggle}
        aria-label="Ouvrir le menu"
      >
        <Menu size={22} />
      </button>

      {/* Search — hidden on mobile, visible from sm+ */}
      <div className="flex-1 relative hidden sm:block">
        <Search size={18} className="absolute left-3 top-2.5 text-text-secondary" />
        <input
          type="text"
          placeholder="Rechercher un commerçant..."
          className="input-field pl-10"
        />
      </div>

      {/* Spacer on mobile so API badge goes to the right */}
      <div className="flex-1 sm:hidden" />

      <div className="flex items-center gap-2 text-sm text-text-secondary flex-shrink-0">
        <Wifi size={16} className="text-success" />
        <span className="hidden md:inline">API connectée</span>
      </div>
    </header>
  )
}
