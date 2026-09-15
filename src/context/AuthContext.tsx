import React from "react";
import { SessionUser, getSessionUser } from "../lib/session";
import { getToken } from "../lib/apiClient";
import * as authService from "../services/authService";

interface AuthContextValue {
  user: SessionUser | null;
  loading: boolean;
  loginWithIdentifier: (identifier: string, password: string) => Promise<void>;
  registerFarmer: (data: authService.FarmerRegisterInput) => Promise<void>;
  registerBuyer: (data: authService.BuyerRegisterInput) => Promise<void>;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<SessionUser | null>(getSessionUser());
  const [loading, setLoading] = React.useState<boolean>(!!getToken());

  React.useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    authService.restoreSession().then((restored) => {
      setUser(restored);
      setLoading(false);
    });
  }, []);

  const loginWithIdentifier = async (identifier: string, password: string) => {
    const sessionUser = await authService.login(identifier, password);
    setUser(sessionUser);
  };

  const registerFarmer = async (data: authService.FarmerRegisterInput) => {
    const sessionUser = await authService.registerFarmer(data);
    setUser(sessionUser);
  };

  const registerBuyer = async (data: authService.BuyerRegisterInput) => {
    const sessionUser = await authService.registerBuyer(data);
    setUser(sessionUser);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginWithIdentifier, registerFarmer, registerBuyer, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
