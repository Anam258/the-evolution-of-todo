/**
 * Authentication utilities for handling logout and other auth-related functions.
 */

import { removeToken } from '@/auth/auth-config';

/**
 * Perform logout by clearing the token and redirecting to sign-in.
 * @param redirectTo - Optional path to redirect to after logout (defaults to '/auth/sign-in')
 */
export function logout(redirectTo: string = '/auth/sign-in'): void {
  // Remove the JWT token from storage
  removeToken();

  // Clear any other auth-related data from storage
  if (typeof window !== 'undefined') {
    // Clear session storage if needed
    sessionStorage.clear();

    // Redirect to sign-in page
    window.location.href = redirectTo;
  }
}

/**
 * Hook for handling logout in React components.
 * This could be used in a React component to handle logout.
 */
export function useLogout(): () => void {
  return () => logout();
}

/**
 * Check if the current token is expired.
 * @returns True if the token is expired, false otherwise
 */
export function isTokenExpired(): boolean {
  const token = localStorage.getItem('jwt_token');
  if (!token) {
    return true; // No token is considered expired
  }

  try {
    // Split the token to get the payload
    const parts = token.split('.');
    if (parts.length !== 3) {
      return true; // Malformed token is considered expired
    }

    // Decode the payload (second part)
    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true; // If there's an error, treat as expired
  }
}

/**
 * Function to handle token expiration.
 * Clears the token and redirects to sign-in.
 */
export function handleTokenExpiration(): void {
  console.warn('Token has expired. Redirecting to sign-in.');
  logout('/auth/sign-in');
}

/**
 * Verify if the token is still valid and handle expiration if needed.
 * @returns True if token is still valid, false if expired
 */
export function verifyAndHandleTokenExpiration(): boolean {
  if (isTokenExpired()) {
    handleTokenExpiration();
    return false;
  }
  return true;
}