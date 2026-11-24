import { Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import DashboardPage from './pages/DashboardPage'
import MerchantsPage from './pages/MerchantsPage'
import MerchantPage from './pages/MerchantPage'
import AssessmentPage from './pages/AssessmentPage'
import ReviewPage from './pages/ReviewPage'
import GpuBenchmarkPage from './pages/GpuBenchmarkPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/merchants" element={<MerchantsPage />} />
        <Route path="/merchants/:id" element={<MerchantPage />} />
        <Route path="/assessment/:id" element={<AssessmentPage />} />
        <Route path="/review/:id" element={<ReviewPage />} />
        <Route path="/benchmark" element={<GpuBenchmarkPage />} />
      </Route>
    </Routes>
  )
}