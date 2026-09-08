import { Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "./layouts/AppShell";
import { AdminLayout } from "./layouts/AdminLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ProfilePage } from "./pages/ProfilePage";
import { EditProfilePage } from "./pages/EditProfilePage";
import { SkillsPage } from "./pages/SkillsPage";
import { CareersPage } from "./pages/CareersPage";
import { JobsPage } from "./pages/JobsPage";
import { SkillGapPage } from "./pages/SkillGapPage";
import { LearningResourcesPage } from "./pages/LearningResourcesPage";
import { AssistantPage } from "./pages/AssistantPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { AdminUsersPage } from "./pages/admin/AdminUsersPage";
import { AdminStudentsPage } from "./pages/admin/AdminStudentsPage";
import { AdminSkillsPage } from "./pages/admin/AdminSkillsPage";
import { AdminCareersPage } from "./pages/admin/AdminCareersPage";
import { AdminJobsPage } from "./pages/admin/AdminJobsPage";
import { AdminResourcesPage } from "./pages/admin/AdminResourcesPage";
import { AdminLearningPage } from "./pages/admin/AdminLearningPage";
import { AdminAIPage } from "./pages/admin/AdminAIPage";
import { AdminSystemPage } from "./pages/admin/AdminSystemPage";
import { AdminAuditPage } from "./pages/admin/AdminAuditPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        {/* Legacy redirects */}
        <Route path="/login" element={<Navigate to="/student/login" replace />} />
        <Route path="/register" element={<Navigate to="/student/register" replace />} />

        {/* Public student auth routes */}
        <Route path="/student/login" element={<LoginPage />} />
        <Route path="/student/register" element={<RegisterPage />} />

        {/* Public admin auth route */}
        <Route path="/admin/login" element={<LoginPage />} />

        {/* Protected student routes */}
        <Route element={<ProtectedRoute requiredRole="student" loginPath="/student/login" />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<ProfilePage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/profile/edit" element={<EditProfilePage />} />
            <Route path="/skills" element={<SkillsPage />} />
            <Route path="/careers" element={<CareersPage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/skill-gap" element={<SkillGapPage />} />
            <Route path="/skill-gap/:careerName" element={<SkillGapPage />} />
            <Route path="/learning-resources" element={<LearningResourcesPage />} />
            <Route path="/assistant" element={<AssistantPage />} />
          </Route>
        </Route>

        {/* Admin routes */}
        <Route path="/admin" element={<ProtectedRoute requiredRole="admin" loginPath="/admin/login" />}>
          <Route element={<AdminLayout />}>
            <Route index element={<AdminDashboardPage />} />
            <Route path="users" element={<AdminUsersPage />} />
            <Route path="students" element={<AdminStudentsPage />} />
            <Route path="skills" element={<AdminSkillsPage />} />
            <Route path="careers" element={<AdminCareersPage />} />
            <Route path="jobs" element={<AdminJobsPage />} />
            <Route path="resources" element={<AdminResourcesPage />} />
            <Route path="learning" element={<AdminLearningPage />} />
            <Route path="ai" element={<AdminAIPage />} />
            <Route path="system" element={<AdminSystemPage />} />
            <Route path="audit" element={<AdminAuditPage />} />
          </Route>
        </Route>
      </Routes>
    </QueryClientProvider>
  );
}

export default App;
