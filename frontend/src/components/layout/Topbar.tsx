import { Search, Wifi } from 'lucide-react'

export default function Topbar() {
  return (
    <header className="h-14 bg-surface border-b border-border flex items-center px-6 gap-4">
      <div className="flex-1 relative">
        <Search size={18} className="absolute left-3 top-2.5 text-text-secondary" />
        <input
          type="text"
          placeholder="Rechercher un commerçant..."
          className="input-field pl-10"
        />
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <Wifi size={16} className="text-success" />
        <span>API connectée</span>
      </div>
    </header>
  )
}