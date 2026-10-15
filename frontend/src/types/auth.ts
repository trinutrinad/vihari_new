export type UserProfile = {
  avatar_url: string | null
  bio: string | null
  preferred_language: string
  home_city: string | null
  travel_preferences: string[]
}

export type AuthUser = {
  id: string
  full_name: string
  email: string | null
  phone: string | null
  primary_role: string
  roles: string[]
  is_active: boolean
  is_email_verified: boolean
  is_phone_verified: boolean
  last_login_at: string | null
  profile: UserProfile | null
}

export type TokenPair = {
  access_token: string
  refresh_token: string
  token_type: string
}

export type AuthSession = {
  user: AuthUser
  tokens: TokenPair
}
