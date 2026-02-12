/**
 * Utility functions for handling JWT token operations including expiration detection.
 */

import type { JWTPayload } from '@/types/auth';

/**
 * Parse and decode a JWT token to extract its payload.
 * @param token - The JWT token to parse
 * @returns The decoded JWT payload, or null if token is invalid
 */
export function parseJWT(token?: string): JWTPayload | null {
  if (!token) {
    token = (typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null) ?? undefined;
  }

  if (!token) {
    return null;
  }

  try {
    // Split the token to get the payload
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null; // Malformed token
    }

    // Decode the payload (second part)
    const payload = JSON.parse(atob(parts[1]));

    return payload as JWTPayload;
  } catch (error) {
    console.error('Error parsing JWT token:', error);
    return null;
  }
}

/**
 * Check if the current token is expired.
 * @returns True if the token is expired, false otherwise
 */
export function isTokenExpired(token?: string): boolean {
  if (!token) {
    token = (typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null) ?? undefined;
  }

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
 * Get the expiration time of the token in milliseconds since epoch.
 * @param token - Optional token to check, defaults to token from localStorage
 * @returns Expiration time in milliseconds, or null if token is invalid
 */
export function getTokenExpiration(token?: string): number | null {
  if (!token) {
    token = (typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null) ?? undefined;
  }

  if (!token) {
    return null;
  }

  try {
    // Split the token to get the payload
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null; // Malformed token
    }

    // Decode the payload (second part)
    const payload = JSON.parse(atob(parts[1]));

    // Return expiration time in milliseconds
    return payload.exp * 1000;
  } catch (error) {
    console.error('Error getting token expiration:', error);
    return null;
  }
}

/**
 * Get the time remaining before token expiration in milliseconds.
 * @param token - Optional token to check, defaults to token from localStorage
 * @returns Time remaining in milliseconds, or null if token is invalid
 */
export function getTimeUntilExpiration(token?: string): number | null {
  const expirationTime = getTokenExpiration(token);
  if (expirationTime === null) {
    return null;
  }

  const currentTime = Date.now();
  return Math.max(0, expirationTime - currentTime);
}

/**
 * Schedule a callback to execute when the token is about to expire.
 * @param callback - Function to call when token is about to expire
 * @param bufferMs - Buffer time in milliseconds before actual expiration to trigger the callback (default: 60000ms = 1 minute)
 * @returns Timeout ID that can be used to cancel the scheduled callback
 */
export function scheduleTokenRefresh(callback: () => void, bufferMs: number = 60000): number | null {
  const timeUntilExp = getTimeUntilExpiration();

  if (timeUntilExp === null) {
    console.warn('Cannot schedule token refresh: invalid token');
    return null;
  }

  // Adjust the timeout to fire before actual expiration by the buffer time
  const timeoutMs = Math.max(0, timeUntilExp - bufferMs);

  return window.setTimeout(() => {
    callback();
  }, timeoutMs);
}

/**
 * Cancel a scheduled token refresh.
 * @param timeoutId - The timeout ID returned by scheduleTokenRefresh
 */
export function cancelTokenRefresh(timeoutId: number | null): void {
  if (timeoutId !== null) {
    clearTimeout(timeoutId);
  }
}

/**
 * Function to handle token expiration.
 * Clears the token and redirects to sign-in.
 */
export function handleTokenExpiration(): void {
  console.warn('Token has expired. Redirecting to sign-in.');

  if (typeof window !== 'undefined') {
    // Remove the expired token
    localStorage.removeItem('jwt_token');

    // Clear any other auth-related data from storage
    sessionStorage.clear();

    // Redirect to sign-in page
    window.location.href = '/auth/sign-in';
  }
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

/**
 * Higher-order function that wraps an API call and checks for token expiration before making the call.
 * @param apiCall - The API call function to wrap
 * @returns A function that checks token validity before making the API call
 */
export function withTokenValidation<T extends (...args: any[]) => any>(apiCall: T): T {
  return ((...args: Parameters<T>): ReturnType<T> => {
    // Check if token is still valid before making the API call
    if (!verifyAndHandleTokenExpiration()) {
      // If token is expired, throw an error or return a rejected promise
      throw new Error('Token expired. Please log in again.');
    }

    // If token is valid, proceed with the API call
    return apiCall(...args);
  }) as T;
}