import { NavLink } from 'react-router-dom'
import {
  BookmarkCheck,
  Compass,
  Home,
  Map,
  UserRound,
} from 'lucide-react'
import { ROUTES } from '@/constants/app'
import { cn } from '@/utils/cn'

const items = [
  { to: ROUTES.home, label: 'Home', icon: Home },
  { to: ROUTES.explore, label: 'Explore', icon: Compass },
  { to: ROUTES.trips, label: 'Trips', icon: Map },
  { to: ROUTES.bookings, label: 'Bookings', icon: BookmarkCheck },
  { to: ROUTES.profile, label: 'Profile', icon: UserRound },
] as const

export function BottomNavigation() {
  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-by-border bg-white/95 shadow-[var(--shadow-by-nav)] backdrop-blur safe-pb md:hidden"
    >
      <ul className="mx-auto flex max-w-lg items-stretch justify-between px-2 pt-2">
        {items.map(({ to, label, icon: Icon }) => (
          <li key={to} className="flex-1">
            <NavLink
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center gap-1 rounded-xl px-2 py-1.5 text-[11px] font-medium transition-colors',
                  isActive ? 'text-by-green' : 'text-by-muted hover:text-by-ink',
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={cn('size-5', isActive && 'stroke-[2.5]')}
                    aria-hidden
                  />
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
