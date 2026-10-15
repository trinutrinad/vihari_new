import { NavLink, Outlet } from 'react-router-dom'
import { BottomNavigation } from '@/components/layout/BottomNavigation'
import { TopNavigation } from '@/components/layout/TopNavigation'
import { ROUTES } from '@/constants/app'
import { cn } from '@/utils/cn'

const desktopLinks = [
  { to: ROUTES.home, label: 'Home' },
  { to: ROUTES.explore, label: 'Explore' },
  { to: ROUTES.hotels, label: 'Hotels' },
  { to: ROUTES.restaurants, label: 'Food' },
  { to: ROUTES.guides, label: 'Guides' },
  { to: ROUTES.transport, label: 'Rides' },
  { to: ROUTES.activities, label: 'Activities' },
  { to: ROUTES.map, label: 'Map' },
  { to: ROUTES.planner, label: 'AI Plan' },
  { to: ROUTES.ask, label: 'Ask' },
  { to: ROUTES.eval, label: 'Eval' },
  { to: ROUTES.search, label: 'Search' },
  { to: ROUTES.trips, label: 'Trips' },
  { to: ROUTES.bookings, label: 'Bookings' },
  { to: ROUTES.payments, label: 'Pay' },
  { to: ROUTES.safety, label: 'Safety' },
  { to: ROUTES.notifications, label: 'Alerts' },
  { to: ROUTES.business, label: 'Business' },
  { to: ROUTES.admin, label: 'Admin' },
  { to: ROUTES.profile, label: 'Profile' },
] as const

export function AppLayout() {
  return (
    <div className="mx-auto flex min-h-svh w-full max-w-6xl flex-col">
      <TopNavigation subtitle="Discover India with confidence" />
      <nav
        aria-label="Desktop"
        className="sticky top-[57px] z-20 hidden border-b border-by-border/70 bg-white/90 px-4 py-2 backdrop-blur md:block"
      >
        <ul className="flex flex-wrap gap-2">
          {desktopLinks.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                className={({ isActive }) =>
                  cn(
                    'rounded-full px-3 py-1.5 text-sm font-medium transition',
                    isActive
                      ? 'bg-by-green-soft text-by-green'
                      : 'text-by-muted hover:bg-by-green-soft/60 hover:text-by-ink',
                  )
                }
              >
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <main className="flex-1 px-4 pb-24 pt-4 md:pb-8">
        <Outlet />
      </main>
      <BottomNavigation />
    </div>
  )
}
