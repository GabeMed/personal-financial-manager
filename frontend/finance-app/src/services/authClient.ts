import { jwtDecode } from "jwt-decode";
import { getErrorMessage } from "@/services/errors";
import { loginGateway, meGateway, registerGateway } from "@/services/gateway";
import {
  loginSchema,
  registerSchema,
  type LoginCredentials,
  type RegisterCredentials,
  type User,
} from "@/schemas/auth";

const TOKEN_KEY = "token";
const USER_KEY = "user";

export type LoginResult = { token: string; user: User };

function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}
function saveUser(user: User) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}
function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
function tokenExpired(token: string): boolean {
  try {
    const { exp } = jwtDecode<{ exp: number }>(token);
    return Date.now() >= exp * 1000;
  } catch {
    return true;
  }
}
function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? (JSON.parse(raw) as User) : null;
}

export const authService = {
  async login(credentials: LoginCredentials) {
    loginSchema.parse(credentials);

    try {
      const { access_token } = await loginGateway(credentials);
      saveToken(access_token);
      const user = await meGateway();
      saveUser(user);
      return { token: access_token, user };
    } catch (err) {
      throw new Error(getErrorMessage(err, "Login failed"));
    }
  },

  async register(credentials: RegisterCredentials): Promise<LoginResult> {
    registerSchema.parse(credentials);

    try {
      await registerGateway(credentials);
    } catch (err) {
      throw new Error(getErrorMessage(err, "Register failed"));
    }
    // Sign the new user in right away.
    return authService.login({
      username: credentials.username,
      password: credentials.password,
    });
  },

  isAuthenticated(): boolean {
    const token = getToken();
    return token ? !tokenExpired(token) : false;
  },

  logout() {
    clearSession();
    window.location.reload();
  },

  getCurrentUser(): User | null {
    if (!this.isAuthenticated()) return null;
    return getStoredUser();
  },
};
