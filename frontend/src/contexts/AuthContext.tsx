import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authApi, type CurrentUserResponse, type LoginRequest, type RegisterRequest } from "@/lib/api";

interface AuthContextType {
  user: CurrentUserResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<{ role: string }>;
  register: (data: RegisterRequest) => Promise<{ role: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_KEY = "token";

function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setIsLoading(false);
      return;
    }

    authApi
      .getMe()
      .then((data) => {
        setUser(data);
      })
      .catch(() => {
        clearToken();
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const login = useCallback(
    async (data: LoginRequest) => {
      const response = await authApi.login(data);
      storeToken(response.access_token);
      const me = await authApi.getMe();
      setUser(me);
      return { role: response.user.role };
    },
    []
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      const response = await authApi.register(data);
      clearToken();
      setUser(null);
      return { role: response.user.role };
    },
    []
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
