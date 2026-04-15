import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import TeamsTab from './components/TeamsTab';
import MembersTab from './components/MembersTab';
import AchievementsTab from './components/AchievementsTab';
import InsightsTab from './components/InsightsTab';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected shell — all /app/* routes render inside AppLayout */}
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index              element={<Navigate to="insights" replace />} />
            <Route path="insights"     element={<InsightsTab />} />
            <Route path="teams"        element={<TeamsTab />} />
            <Route path="members"      element={<MembersTab />} />
            <Route path="achievements" element={<AchievementsTab />} />
          </Route>

          {/* Legacy /dashboard redirect */}
          <Route path="/dashboard" element={<Navigate to="/app/insights" replace />} />
          <Route path="/"          element={<Navigate to="/app/insights" replace />} />
          <Route path="*"          element={<Navigate to="/app/insights" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
