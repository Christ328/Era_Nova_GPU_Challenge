import { Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import DashboardPage from './pages/DashboardPage'
import MerchantsPage from './pages/MerchantsPage'
import MerchantPage from './pages/MerchantPage'
import AssessmentPage from './pages/AssessmentPage'
import CustomScorePage from './pages/CustomScorePage'
import RulesPage from './pages/RulesPage'
import ReviewPage from './pages/ReviewPage'
import GpuBenchmarkPage from './pages/GpuBenchmarkPage'
import AgentPage from './pages/AgentPage'
import IMFAdminPage from './pages/IMFAdminPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/merchants" element={<MerchantsPage />} />
        <Route path="/merchants/:id" element={<MerchantPage />} />
        <Route path="/assessment/:id" element={<AssessmentPage />} />
        <Route path="/custom" element={<CustomScorePage />} />
        <Route path="/rules" element={<RulesPage />} />
        <Route path="/review/:id" element={<ReviewPage />} />
        <Route path="/benchmark" element={<GpuBenchmarkPage />} />
        <Route path="/agent" element={<AgentPage />} />
        <Route path="/imf" element={<IMFAdminPage />} />
      </Route>
    </Routes>
  )
}
