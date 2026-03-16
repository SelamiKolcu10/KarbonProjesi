import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/dashboard/page";
import UploadPage from "./pages/upload/page";
import EmissionPage from "./pages/emission/page";
import StrategyPage from "./pages/strategy/page";
import ReportsPage from "./pages/reports/page";
import SettingsPage from "./pages/settings/page";
import NotificationsPage from "./pages/notifications/page";
import ProjectionPage from "./pages/projection/page";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <Toaster theme="dark" position="bottom-right" richColors closeButton />
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/belge-yukle" element={<UploadPage />} />
          <Route path="/emisyon-analizi" element={<EmissionPage />} />
          <Route path="/emisyon-projeksiyonu" element={<ProjectionPage />} />
          <Route path="/strateji-raporu" element={<StrategyPage />} />
          <Route path="/raporlar" element={<ReportsPage />} />
          <Route path="/ayarlar" element={<SettingsPage />} />
          <Route path="/bildirimler" element={<NotificationsPage />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
