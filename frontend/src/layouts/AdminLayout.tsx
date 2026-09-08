import { useState } from "react";
import { Link, useLocation, Outlet, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import {
  LayoutDashboard,
  Users,
  Wrench,
  Briefcase,
  Building2,
  BookOpen,
  BarChart3,
  Bot,
  Settings,
  FileText,
  ChevronLeft,
  Menu,
  ExternalLink,
  LogOut,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Dashboard", path: "/admin", icon: LayoutDashboard },
  { label: "Users", path: "/admin/users", icon: Users },
  { label: "Skills", path: "/admin/skills", icon: Wrench },
  { label: "Careers", path: "/admin/careers", icon: Briefcase },
  { label: "Jobs", path: "/admin/jobs", icon: Building2 },
  { label: "Resources", path: "/admin/resources", icon: BookOpen },
  { label: "Learning", path: "/admin/learning", icon: BarChart3 },
  { label: "AI Assistant", path: "/admin/ai", icon: Bot },
  { label: "System", path: "/admin/system", icon: Settings },
  { label: "Audit Logs", path: "/admin/audit", icon: FileText },
];

export function AdminLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const isActive = (path: string) => {
    if (path === "/admin") return location.pathname === "/admin";
    return location.pathname.startsWith(path);
  };

  function handleLogout() {
    logout();
    setShowLogoutConfirm(false);
    navigate("/admin/login", { state: { message: "You have been logged out successfully." } });
  }

  const SidebarContent = () => (
    <>
      <div className="flex items-center gap-2 px-4 py-4 border-b border-border/50">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
          SB
        </div>
        {sidebarOpen && (
          <div>
            <span className="text-sm font-bold tracking-tight">SkillBridge</span>
            <span className="block text-[10px] text-muted-foreground font-medium">Admin Panel</span>
          </div>
        )}
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
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
            <p className="text-xs font-medium text-foreground truncate">
              {user.email}
            </p>
            <p className="text-[10px] text-muted-foreground truncate">Admin</p>
          </div>
        )}
        <Link
          to="/"
          onClick={() => setMobileOpen(false)}
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          title="Student View"
        >
          <ExternalLink className="h-5 w-5 flex-shrink-0" />
          {sidebarOpen && <span>Student View</span>}
        </Link>
        <button
          onClick={() => {
            setShowLogoutConfirm(true);
            setMobileOpen(false);
          }}
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors w-full"
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
          "hidden lg:flex border-r border-border/50 bg-card flex-col transition-all duration-200 relative",
          sidebarOpen ? "w-64" : "w-16"
        )}
      >
        <SidebarContent />
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-4 -right-3 hidden lg:flex h-6 w-6 items-center justify-center rounded-full border bg-card text-muted-foreground hover:text-foreground transition-colors z-10"
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
        <div className="lg:hidden flex items-center gap-3 px-4 py-3 border-b border-border/50 bg-card/80 backdrop-blur-sm sticky top-0 z-30">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 rounded-lg hover:bg-accent text-muted-foreground"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground font-bold text-xs">
            SB
          </div>
          <span className="text-sm font-semibold">Admin Panel</span>
          <div className="ml-auto">
            <button
              onClick={() => setShowLogoutConfirm(true)}
              className="p-2 rounded-lg hover:bg-accent text-muted-foreground"
              title="Sign Out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>

        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Logout confirmation dialog */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
          <div className="fixed inset-0 bg-black/50" onClick={() => setShowLogoutConfirm(false)} />
          <div className="relative bg-card rounded-xl shadow-xl max-w-sm w-full p-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/10">
                <LogOut className="h-5 w-5 text-destructive" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">Sign Out</h3>
                <p className="text-sm text-muted-foreground">Are you sure you want to sign out?</p>
              </div>
            </div>
            <div className="flex gap-3 justify-end pt-2">
              <button
                onClick={() => setShowLogoutConfirm(false)}
                className="px-4 py-2 rounded-lg border border-border text-sm font-medium hover:bg-accent transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-lg bg-destructive text-destructive-foreground text-sm font-medium hover:bg-destructive/90 transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
