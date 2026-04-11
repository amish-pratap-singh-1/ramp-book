/**
 * Auth helpers — token storage and decoding
 */

const TOKEN_KEY = "access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function decodeToken(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

export function getTokenPayload(): Record<string, unknown> | null {
  const token = getToken();
  if (!token) return null;
  return decodeToken(token);
}

export function getUserRole(): string | null {
  const payload = getTokenPayload();
  if (!payload) return null;
  return payload["role"] as string;
}

export function getUserId(): number | null {
  const payload = getTokenPayload();
  if (!payload) return null;
  return parseInt(payload["sub"] as string, 10);
}

export function isTokenExpired(): boolean {
  const payload = getTokenPayload();
  if (!payload) return true;
  const exp = payload["exp"] as number;
  return Date.now() / 1000 > exp;
}

export function isAuthenticated(): boolean {
  return !!getToken() && !isTokenExpired();
}
