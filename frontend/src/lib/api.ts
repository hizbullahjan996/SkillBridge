import { apiClient } from "./client";

// ── Auth types ──────────────────────────────────────────────
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
  full_name: string;
}

export interface UserResponse {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface CurrentUserResponse {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
  student_profile: {
    id: number;
    full_name: string;
    age: number | null;
    gender: string | null;
    university_year: string | null;
    major: string | null;
    cgpa: number | null;
  } | null;
}

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>("/auth/login", data),

  register: (data: RegisterRequest) =>
    apiClient.post<TokenResponse>("/auth/register", data),

  getMe: () => apiClient.get<CurrentUserResponse>("/auth/me"),
};

// ── Student profile types ───────────────────────────────────
export interface StudentProfile {
  id: number;
  user_id: number;
  full_name: string;
  age: number | null;
  gender: string | null;
  university_year: string | null;
  major: string | null;
  cgpa: number | null;
  attendance_percentage: number | null;
  study_hours_per_week: number | null;
  projects_completed: number | null;
  certifications_count: number | null;
  internships: number | null;
  communication_skills: number | null;
  teamwork: number | null;
  problem_solving: number | null;
  interest_domain: string | null;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: number;
  name: string;
  normalized_name: string;
  category: string;
}

export interface StudentSkill {
  id: number;
  student_id: number;
  skill_id: number;
  proficiency: number;
  skill: Skill | null;
  created_at: string;
}

export interface ProfileCompletion {
  percentage: number;
  completed_fields: string[];
  missing_fields: string[];
  total_required: number;
  completed_count: number;
}

export interface MLReadiness {
  ready: boolean;
  missing_fields: string[];
  missing_skills: string[];
  profile_completion: number;
  skills_count: number;
}

export interface ProfileUpdate {
  full_name?: string;
  age?: number;
  gender?: string;
  university_year?: string;
  major?: string;
  cgpa?: number;
  attendance_percentage?: number;
  study_hours_per_week?: number;
  projects_completed?: number;
  certifications_count?: number;
  internships?: number;
  communication_skills?: number;
  teamwork?: number;
  problem_solving?: number;
  interest_domain?: string;
}

export interface SkillCreate {
  skill_id: number;
  proficiency: number;
}

export interface LearningResource {
  id: number;
  title: string;
  provider: string;
  description: string | null;
  url: string | null;
  resource_type: string;
  difficulty: string | null;
  is_free: boolean;
  skills: Array<{ id: number; name: string; normalized_name: string }>;
  created_at: string;
  updated_at: string;
}

export interface RecommendedResource {
  resource: LearningResource;
  relevance_score: number;
  matched_skill: string;
  skill_priority: string;
}

export interface LearningProgressRecord {
  id: number;
  resource_id: number;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface LearningProgressSummary {
  total: number;
  not_started: number;
  in_progress: number;
  completed: number;
}

export interface AssistantChatResponse {
  answer: string;
  sources: Array<{ type: string; reference: string }>;
  conversation_id: number;
}

export interface AssistantConversation {
  id: number;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssistantMessage {
  id: number;
  role: string;
  content: string;
  created_at: string;
}

export const profileApi = {
  getMyProfile: () => apiClient.get<StudentProfile>("/students/me"),

  updateMyProfile: (data: ProfileUpdate) =>
    apiClient.put<StudentProfile>("/students/me", data),

  getProfileCompletion: () =>
    apiClient.get<ProfileCompletion>("/students/me/profile-completion"),

  getMLReadiness: () => apiClient.get<MLReadiness>("/students/me/ml-readiness"),
};

export const skillsApi = {
  getSkills: (params?: Record<string, string>) =>
    apiClient.get<Skill[]>("/skills", params),

  getMySkills: () => apiClient.get<StudentSkill[]>("/students/me/skills"),

  addSkill: (data: SkillCreate) =>
    apiClient.post<StudentSkill>("/skills/me", data),

  removeSkill: (skillId: number) =>
    apiClient.delete(`/skills/me/${skillId}`),
};

export const learningResourcesApi = {
  getResources: (params?: {
    skill?: string;
    resource_type?: string;
    difficulty?: string;
    is_free?: string;
    search?: string;
    page?: string;
    page_size?: string;
  }) => apiClient.get<{ items: LearningResource[]; total: number; page: number; page_size: number; pages: number }>("/learning-resources", params as Record<string, string>),

  getResource: (id: number) =>
    apiClient.get<LearningResource>(`/learning-resources/${id}`),

  getRecommended: () =>
    apiClient.get<{ resources: RecommendedResource[]; total: number; career_name: string }>("/learning-resources/recommended"),

  getProgress: () =>
    apiClient.get<{ records: LearningProgressRecord[]; summary: LearningProgressSummary }>("/learning-progress"),

  startResource: (resourceId: number) =>
    apiClient.post<LearningProgressRecord>(`/learning-progress?resource_id=${resourceId}`),

  updateProgress: (resourceId: number, status: string) =>
    apiClient.put<LearningProgressRecord>(`/learning-progress/${resourceId}`, { status }),
};

export const assistantApi = {
  chat: (message: string, conversationId?: number) =>
    apiClient.post<AssistantChatResponse>("/assistant/chat", {
      message,
      conversation_id: conversationId,
    }),

  getConversations: () =>
    apiClient.get<AssistantConversation[]>("/assistant/conversations"),

  getConversation: (id: number) =>
    apiClient.get<{ conversation: AssistantConversation; messages: AssistantMessage[] }>(`/assistant/conversations/${id}`),

  deleteConversation: (id: number) =>
    apiClient.delete(`/assistant/conversations/${id}`),
};

export const roadmapApi = {
  getDefault: () =>
    apiClient.get("/learning-roadmap"),

  getWithResources: () =>
    apiClient.get("/learning-roadmap/with-resources"),
};

export const adminApi = {
  getDashboard: () => apiClient.get<{
    users: number;
    students: number;
    jobs: number;
    skills: number;
    learning_resources: number;
    career_recommendations: number;
    ai_conversations: number;
    learning_progress_records: number;
  }>("/admin/dashboard"),

  getUsers: (params?: { search?: string; role?: string; status?: string; page?: string; page_size?: string }) =>
    apiClient.get<{ items: Array<{ id: number; email: string; role: string; is_active: boolean; created_at: string; has_profile: boolean }>; total: number; page: number; page_size: number; pages: number }>("/admin/users", params as Record<string, string>),

  getUser: (id: number) => apiClient.get(`/admin/users/${id}`),

  getStudents: (params?: { search?: string; page?: string; page_size?: string }) =>
    apiClient.get<{ items: Array<{ id: number; user_id: number; email: string; full_name: string; major: string | null; university_year: string | null; skills_count: number; recommendations_count: number }>; total: number; page: number; page_size: number; pages: number }>("/admin/students", params as Record<string, string>),

  getStudent: (id: number) => apiClient.get(`/admin/students/${id}`),

  getSkills: (params?: { search?: string; page?: string; page_size?: string }) =>
    apiClient.get<{ items: Array<{ skill_id: number; skill_name: string; category: string; student_count: number; job_count: number }>; total: number; page: number; page_size: number; pages: number }>("/admin/skills", params as Record<string, string>),

  getCareers: () => apiClient.get<Array<{ career_id: number; career_name: string; recommendation_count: number; job_count: number; skill_count: number }>>("/admin/careers"),

  getJobAnalytics: () => apiClient.get<{ total_jobs: number; top_cities: Array<{ name: string; count: number }>; top_sectors: Array<{ name: string; count: number }>; top_skills: Array<{ name: string; count: number }> }>("/admin/jobs/analytics"),

  getResources: (params?: { search?: string; resource_type?: string; page?: string; page_size?: string }) =>
    apiClient.get<{ items: Array<{ id: number; title: string; provider: string; resource_type: string; difficulty: string | null; is_free: boolean; skills: Array<{ id: number; name: string }> }>; total: number; page: number; page_size: number; pages: number }>("/admin/resources", params as Record<string, string>),

  getLearningAnalytics: () => apiClient.get<{ total_resources: number; total_progress_records: number; started: number; completed: number; completion_rate: number; most_popular_resources: Array<{ title: string; count: number }>; most_studied_skills: Array<{ name: string; count: number }> }>("/admin/learning/analytics"),

  getAIAnalytics: () => apiClient.get<{ total_conversations: number; total_messages: number; active_users: number; avg_messages_per_conversation: number }>("/admin/ai/analytics"),

  getSystemHealth: () => apiClient.get<{ api_status: string; database_status: string; ml_model_status: string; llm_provider_status: string }>("/admin/system/health"),

  getAuditLogs: (params?: { action?: string; resource_type?: string; date_from?: string; date_to?: string; page?: string; page_size?: string }) =>
    apiClient.get<{ items: Array<{ id: number; admin_user_id: number; admin_email: string | null; action: string; resource_type: string | null; resource_id: number | null; metadata: Record<string, unknown> | null; timestamp: string }>; total: number; page: number; page_size: number; pages: number }>("/admin/audit-logs", params as Record<string, string>),
};
