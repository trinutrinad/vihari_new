export const APP_NAME = 'Bharat Yatra'
export const APP_TAGLINE = 'Discover. Plan. Travel. Experience India.'

export const ROUTES = {
  home: '/',
  explore: '/explore',
  map: '/map',
  planner: '/planner',
  ask: '/ask',
  eval: '/eval',
  hotels: '/hotels',
  restaurants: '/restaurants',
  guides: '/guides',
  transport: '/transport',
  activities: '/activities',
  trips: '/trips',
  bookings: '/bookings',
  payments: '/payments',
  safety: '/safety',
  notifications: '/notifications',
  business: '/business',
  admin: '/admin',
  profile: '/profile',
  search: '/search',
  login: '/login',
  register: '/register',
  forgotPassword: '/forgot-password',
  health: '/system/health',
} as const

export type AppRoute = (typeof ROUTES)[keyof typeof ROUTES]
