import { useState } from "react";
import { Link, useLocation, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import {
  LayoutDashboard,
  Briefcase,
  BarChart3,
  BookOpen,
  MessageSquare,
  GraduationCap,
  Settings,
  ChevronLeft,
  Menu,
  Shield,
  LogOut,
} from "lucide-react";

const STUDENT_NAV = [
  { label: "Dashboard", path: "/profile", icon: LayoutDashboard },
  { label: "My Skills", path: "/skills", icon: BarChart3 },
  { label: "Career Explorer", path: "/careers", icon: Briefcase },
  { label: "Job Board", path: "/jobs", icon: GraduationCap },
  { label: "Learning", path: "/learning-resources", icon: BookOpen },
  { label: "AI Assistant", path: "/assistant", icon: MessageSquare },
];

function AppShell() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) => {
    if (path === "/profile") return location.pathname === "/profile" || location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  const SidebarContent = () => (
    <>
      <div className="flex items-center gap-2 px-4 py-4 border-b border-border/50">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
          SB
        </div>
        {sidebarOpen && (
          <span className="text-lg font-bold tracking-tight">SkillBridge</span>
        )}
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {STUDENT_NAV.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileOpen(false)}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive(item.path)
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
              title={item.label}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="px-3 py-4 border-t border-border/50 space-y-1">
        {user && sidebarOpen && (
          <div className="px-3 py-2 mb-1">
            <p className="text-xs text-muted-foreground truncate">
              {user.student_profile?.full_name || user.email}
            </p>
          </div>
        )}
        <Link
          to="/admin"
          onClick={() => setMobileOpen(false)}
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          title="Admin Panel"
        >
          <Shield className="h-5 w-5 flex-shrink-0" />
          {sidebarOpen && <span>Admin Panel</span>}
        </Link>
        <Link
          to="/profile/edit"
          onClick={() => setMobileOpen(false)}
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          title="Settings"
        >
          <Settings className="h-5 w-5 flex-shrink-0" />
          {sidebarOpen && <span>Settings</span>}
        </Link>
        <button
          onClick={() => {
            logout();
            setMobileOpen(false);
          }}
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-colors w-full"
          title="Sign Out"
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          {sidebarOpen && <span>Sign Out</span>}
        </button>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop sidebar */}
      <aside
        className={cn(
          "hidden lg:flex border-r border-border/50 bg-card flex-col transition-all duration-200",
          sidebarOpen ? "w-64" : "w-16"
        )}
      >
        <SidebarContent />
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-4 -right-3 hidden lg:flex h-6 w-6 items-center justify-center rounded-full border bg-card text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform", !sidebarOpen && "rotate-180")} />
        </button>
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black/40" onClick={() => setMobileOpen(false)} />
          <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border flex flex-col animate-slide-in">
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-border/50 bg-card/80 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="p-2 rounded-lg hover:bg-accent text-muted-foreground"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground font-bold text-xs">
              SB
            </div>
            <span className="text-sm font-semibold">SkillBridge</span>
          </div>
          <button
            onClick={logout}
            className="p-2 rounded-lg hover:bg-accent text-muted-foreground"
            title="Sign Out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>

        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

export { AppShell };
