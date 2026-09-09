import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import DashboardLayout from "./components/layout/DashboardLayout";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import PublicRoute from "./components/auth/PublicRoute";

import Dashboard from "./pages/dashboard/Dashboard";
import ResumeAnalysis from "./pages/resume-analysis/ResumeAnalysis";
import ResumeLibrary from "./pages/resume-library/ResumeLibrary";
import JobMatching from "./pages/job-matching/JobMatching";
import ATSIntelligence from "./pages/ats-intelligence/ATSIntelligence";
import Settings from "./pages/settings/Settings";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* =====================================================
            PUBLIC AUTHENTICATION
        ====================================================== */}

        <Route element={<PublicRoute />}>
          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/register"
            element={<Register />}
          />
        </Route>

        {/* =====================================================
            PROTECTED APPLICATION
        ====================================================== */}

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route
              path="/"
              element={
                <Navigate
                  to="/dashboard"
                  replace
                />
              }
            />

            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/resume-analysis"
              element={<ResumeAnalysis />}
            />

            <Route
              path="/resume-library"
              element={<ResumeLibrary />}
            />

            <Route
              path="/ats-intelligence"
              element={<ATSIntelligence />}
            />

            <Route
              path="/job-matching"
              element={<JobMatching />}
            />

            <Route
              path="/settings"
              element={<Settings />}
            />
          </Route>
        </Route>

        {/* =====================================================
            FALLBACK
        ====================================================== */}

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

