import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppLayout } from '@/layouts/AppLayout'
import { HomePage } from '@/pages/HomePage'
import { BookingsPage } from '@/pages/BookingsPage'
import { BookingDetailsPage } from '@/pages/BookingDetailsPage'
import { PaymentsPage } from '@/pages/PaymentsPage'
import { PaymentDetailsPage } from '@/pages/PaymentDetailsPage'
import { SafetyPage } from '@/pages/SafetyPage'
import { NotificationsPage } from '@/pages/NotificationsPage'
import { BusinessDashboardPage } from '@/pages/BusinessDashboardPage'
import { AdminDashboardPage } from '@/pages/AdminDashboardPage'
import { TripsPage } from '@/pages/TripsPage'
import { TripDetailsPage } from '@/pages/TripDetailsPage'
import { SharedTripPage } from '@/pages/SharedTripPage'
import { ExplorePage } from '@/pages/ExplorePage'
import { HealthPage } from '@/pages/HealthPage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { SearchPage } from '@/pages/SearchPage'
import { MapPage } from '@/pages/MapPage'
import { PlannerPage } from '@/pages/PlannerPage'
import { AskPage } from '@/pages/AskPage'
import { EvalPage } from '@/pages/EvalPage'
import { HotelsPage } from '@/pages/HotelsPage'
import { HotelDetailsPage } from '@/pages/HotelDetailsPage'
import { RestaurantsPage } from '@/pages/RestaurantsPage'
import { RestaurantDetailsPage } from '@/pages/RestaurantDetailsPage'
import { GuidesPage } from '@/pages/GuidesPage'
import { GuideDetailsPage } from '@/pages/GuideDetailsPage'
import { TransportPage } from '@/pages/TransportPage'
import { TransportDetailsPage } from '@/pages/TransportDetailsPage'
import { ActivitiesPage } from '@/pages/ActivitiesPage'
import { ActivityDetailsPage } from '@/pages/ActivityDetailsPage'
import { PlaceDetailsPage } from '@/pages/PlaceDetailsPage'
import { ROUTES } from '@/constants/app'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path={ROUTES.login} element={<LoginPage />} />
          <Route path={ROUTES.register} element={<RegisterPage />} />
          <Route path={ROUTES.forgotPassword} element={<ForgotPasswordPage />} />
          <Route element={<AppLayout />}>
            <Route index element={<HomePage />} />
            <Route path={ROUTES.explore.slice(1)} element={<ExplorePage />} />
            <Route path={ROUTES.trips.slice(1)} element={<TripsPage />} />
            <Route path="trips/shared/:shareCode" element={<SharedTripPage />} />
            <Route path="trips/:tripId" element={<TripDetailsPage />} />
            <Route path={ROUTES.bookings.slice(1)} element={<BookingsPage />} />
            <Route path="bookings/:bookingId" element={<BookingDetailsPage />} />
            <Route path={ROUTES.payments.slice(1)} element={<PaymentsPage />} />
            <Route path="payments/:paymentId" element={<PaymentDetailsPage />} />
            <Route path={ROUTES.safety.slice(1)} element={<SafetyPage />} />
            <Route path={ROUTES.notifications.slice(1)} element={<NotificationsPage />} />
            <Route path={ROUTES.business.slice(1)} element={<BusinessDashboardPage />} />
            <Route path={ROUTES.admin.slice(1)} element={<AdminDashboardPage />} />
            <Route path={ROUTES.profile.slice(1)} element={<ProfilePage />} />
            <Route path={ROUTES.search.slice(1)} element={<SearchPage />} />
            <Route path={ROUTES.map.slice(1)} element={<MapPage />} />
            <Route path={ROUTES.planner.slice(1)} element={<PlannerPage />} />
            <Route path={ROUTES.ask.slice(1)} element={<AskPage />} />
            <Route path={ROUTES.eval.slice(1)} element={<EvalPage />} />
            <Route path={ROUTES.hotels.slice(1)} element={<HotelsPage />} />
            <Route path="hotels/:hotelId" element={<HotelDetailsPage />} />
            <Route path="hotels/slug/:slug" element={<HotelDetailsPage />} />
            <Route path={ROUTES.restaurants.slice(1)} element={<RestaurantsPage />} />
            <Route path="restaurants/:restaurantId" element={<RestaurantDetailsPage />} />
            <Route path="restaurants/slug/:slug" element={<RestaurantDetailsPage />} />
            <Route path={ROUTES.guides.slice(1)} element={<GuidesPage />} />
            <Route path="guides/:guideId" element={<GuideDetailsPage />} />
            <Route path={ROUTES.transport.slice(1)} element={<TransportPage />} />
            <Route path="transport/code/:code" element={<TransportDetailsPage />} />
            <Route path="transport/:optionId" element={<TransportDetailsPage />} />
            <Route path={ROUTES.activities.slice(1)} element={<ActivitiesPage />} />
            <Route path="activities/slug/:slug" element={<ActivityDetailsPage />} />
            <Route path="activities/:activityId" element={<ActivityDetailsPage />} />
            <Route path="places/:placeId" element={<PlaceDetailsPage />} />
            <Route path="places/slug/:slug" element={<PlaceDetailsPage />} />
            <Route path="system/health" element={<HealthPage />} />
          </Route>
          <Route path="*" element={<Navigate to={ROUTES.home} replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
