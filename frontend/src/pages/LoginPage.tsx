import { useState, type FormEvent } from "react";
import { Navigate, Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Eye, EyeOff, Mail, Lock, Sparkles, Target, Briefcase, BookOpen } from "lucide-react";

const FEATURES = [
  { icon: Sparkles, text: "AI Career Recommendations" },
  { icon: Target, text: "Skill Gap Analysis" },
  { icon: Briefcase, text: "Job Matching" },
  { icon: BookOpen, text: "Personalized Learning" },
];

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    const msg = error.message;
    if (msg.includes("Invalid email or password")) {
      return "Email or password is incorrect.";
    }
    if (msg.includes("Account is deactivated")) {
      return "Your account is currently inactive. Please contact support.";
    }
    if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
      return "Unable to connect to SkillBridge. Please try again.";
    }
    if (msg.includes("Request failed: 5")) {
      return "Something went wrong. Please try again later.";
    }
    return msg;
  }
  return "Something went wrong. Please try again later.";
}

export function LoginPage() {
  const { user, isLoading: authLoading, login } = useAuth();
  const location = useLocation();
  const isAdminLogin = location.pathname === "/admin/login";
  const successMessage = location.state?.message as string | undefined;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="relative h-10 w-10">
          <div className="absolute inset-0 rounded-full border-2 border-primary/20" />
          <div className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </div>
    );
  }

  if (user) {
    return <Navigate to={user.role === "admin" ? "/admin" : "/profile"} replace />;
  }

  function validate(): boolean {
    const errors: { email?: string; password?: string } = {};

    if (!email.trim()) {
      errors.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = "Please enter a valid email address.";
    }

    if (!password) {
      errors.password = "Password is required.";
    } else if (password.length < 8) {
      errors.password = "Password must be at least 8 characters.";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const result = await login({ email: email.trim(), password });

      if (isAdminLogin && result.role !== "admin") {
        setError(
          "This account is not an admin account. Please use the student login."
        );
        return;
      }

      if (!isAdminLogin && result.role !== "student") {
        setError(
          "This account is not registered as a student. Please use the admin login."
        );
        return;
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left hero section - hidden on mobile */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-primary/5 via-primary/10 to-background overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,hsl(var(--primary)/0.08),transparent_60%)]" />
        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-16 w-full">
          <div className="space-y-8 max-w-lg">
            <div className="space-y-2">
              <h1 className="text-3xl xl:text-4xl font-bold tracking-tight text-foreground">
                SkillBridge
              </h1>
              <p className="text-lg text-muted-foreground">
                {isAdminLogin ? "Admin Panel" : "AI-Powered Career & Skill Intelligence Platform"}
              </p>
            </div>

            <p className="text-xl text-foreground/80 leading-relaxed">
              {isAdminLogin
                ? "Manage and monitor the SkillBridge platform."
                : "Discover your career path. Build the skills employers need."}
            </p>

            {!isAdminLogin && (
              <div className="space-y-4 pt-4">
                {FEATURES.map((feature) => {
                  const Icon = feature.icon;
                  return (
                    <div key={feature.text} className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Icon className="h-5 w-5" />
                      </div>
                      <span className="text-sm font-medium text-foreground/80">
                        {feature.text}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right login card */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile header */}
          <div className="lg:hidden text-center space-y-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              SkillBridge
            </h1>
            <p className="text-sm text-muted-foreground">
              {isAdminLogin ? "Admin Panel" : "AI-Powered Career & Skill Intelligence Platform"}
            </p>
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-bold tracking-tight text-foreground">
              {isAdminLogin ? "Admin Sign In" : "Welcome Back"}
            </h2>
            <p className="text-sm text-muted-foreground">
              {isAdminLogin
                ? "Sign in to access the admin dashboard."
                : "Sign in to continue your career journey."}
            </p>
          </div>

          {successMessage && (
            <div
              role="status"
              className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-200"
            >
              {successMessage}
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="rounded-lg border border-destructive/20 bg-destructive/5 p-4 text-sm text-destructive"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            <div className="space-y-2">
              <label
                htmlFor="email"
                className="text-sm font-medium text-foreground"
              >
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                autoComplete="email"
                aria-required="true"
                aria-invalid={!!fieldErrors.email}
                aria-describedby={fieldErrors.email ? "email-error" : undefined}
                icon={<Mail className="h-4 w-4" />}
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (fieldErrors.email) {
                    setFieldErrors((prev) => ({ ...prev, email: undefined }));
                  }
                }}
              />
              {fieldErrors.email && (
                <p id="email-error" className="text-xs text-destructive" role="alert">
                  {fieldErrors.email}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label
                htmlFor="password"
                className="text-sm font-medium text-foreground"
              >
                Password
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  aria-required="true"
                  aria-invalid={!!fieldErrors.password}
                  aria-describedby={
                    fieldErrors.password ? "password-error" : undefined
                  }
                  icon={<Lock className="h-4 w-4" />}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (fieldErrors.password) {
                      setFieldErrors((prev) => ({
                        ...prev,
                        password: undefined,
                      }));
                    }
                  }}
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              {fieldErrors.password && (
                <p
                  id="password-error"
                  className="text-xs text-destructive"
                  role="alert"
                >
                  {fieldErrors.password}
                </p>
              )}
            </div>

            <Button
              type="submit"
              loading={isSubmitting}
              disabled={isSubmitting}
              className="w-full"
              size="lg"
            >
              {isSubmitting ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          {!isAdminLogin && (
            <>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    or
                  </span>
                </div>
              </div>

              <p className="text-center text-sm text-muted-foreground">
                Don&apos;t have an account?{" "}
                <Link
                  to="/student/register"
                  className="font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Create Student Account
                </Link>
              </p>
            </>
          )}

          {isAdminLogin && (
            <p className="text-center text-sm text-muted-foreground">
              <Link
                to="/student/login"
                className="font-medium text-primary hover:text-primary/80 transition-colors"
              >
                Student Sign In
              </Link>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
