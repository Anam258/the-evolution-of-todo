/**
 * Better Auth configuration for the frontend application.
 * This file configures the Better Auth client for JWT authentication.
 */

// Note: This is a conceptual implementation as Better Auth for frontend
// would typically be configured differently in a real application.

interface AuthConfig {
  baseURL: string;
  basePath: string;
  cookieName: string;
  tokenType: string;
}

// Configuration based on environment
const authConfig: AuthConfig = {
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
  basePath: process.env.NEXT_PUBLIC_BETTER_AUTH_BASE_PATH || '/api/auth',
  cookieName: 'better-auth.session_token',
  tokenType: 'Bearer'
};

/**
 * Get the authorization header with the JWT token.
 * @param token - The JWT token to include in the header
 * @returns Authorization header object
 */
function getAuthHeader(token?: string): { Authorization?: string } {
  if (!token) {
    // Try to get token from localStorage or cookies
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null;
    if (!storedToken) {
      return {};
    }
    token = storedToken;
  }

  return {
    Authorization: `${authConfig.tokenType} ${token}`
  };
}

/**
 * Store the JWT token in browser storage.
 * @param token - The JWT token to store
 */
function storeToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('jwt_token', token);
  }
}

/**
 * Retrieve the JWT token from browser storage.
 * @returns The stored JWT token or null if not found
 */
function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('jwt_token');
  }
  return null;
}

/**
 * Remove the JWT token from browser storage.
 */
function removeToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('jwt_token');
  }
}

/**
 * Perform logout by clearing the token and redirecting to sign-in.
 * @param redirectTo - Optional path to redirect to after logout (defaults to '/auth/sign-in')
 */
function logout(redirectTo: string = '/auth/sign-in'): void {
  removeToken();

  // Clear any other auth-related data from storage
  if (typeof window !== 'undefined') {
    sessionStorage.clear();

    // Redirect to sign-in page
    window.location.href = redirectTo;
  }
}

/**
 * Validate if the current token is still valid (not expired).
 * @returns True if token is valid, false otherwise
 */
function isValidToken(): boolean {
  const token = getToken();
  if (!token) {
    return false;
  }

  try {
    // Split the token to get the payload
    const parts = token.split('.');
    if (parts.length !== 3) {
      return false;
    }

    // Decode the payload (second part)
    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp > currentTime;
  } catch (error) {
    console.error('Error validating token:', error);
    return false;
  }
}

/**
 * Check if the user is authenticated.
 * @returns True if user is authenticated, false otherwise
 */
function isAuthenticated(): boolean {
  return isValidToken();
}

export {
  authConfig,
  getAuthHeader,
  storeToken,
  getToken,
  removeToken,
  isValidToken,
  isAuthenticated
};

export type { AuthConfig };