/**
 * TypeScript interfaces for authentication-related types.
 */

/**
 * JWT token payload structure.
 * Contains the claims and metadata from the decoded JWT token.
 */
export interface JWTPayload {
  /** Subject (user ID) */
  sub: string;

  /** User email address */
  email: string;

  /** Token expiration timestamp (seconds since epoch) */
  exp: number;

  /** Issued at timestamp (seconds since epoch) */
  iat: number;

  /** Additional custom claims can be added here */
  [key: string]: any;
}

/**
 * Authentication response from the backend API.
 * Returned after successful login or registration.
 */
export interface AuthResponse {
  /** Success status */
  success: boolean;

  /** Response data containing token and user information */
  data: {
    /** JWT access token */
    token: string;

    /** User ID */
    user_id: number;

    /** User email address */
    email: string;
  };

  /** Optional error information */
  error?: {
    /** Error message */
    message: string;

    /** Error code */
    code?: string;
  };
}

/**
 * User authentication state.
 * Represents the current authentication status of the user.
 */
export interface AuthState {
  /** Whether the user is authenticated */
  isAuthenticated: boolean;

  /** The current user's information */
  user: {
    id: number;
    email: string;
  } | null;

  /** The JWT access token */
  token: string | null;

  /** Whether authentication is being checked */
  isLoading: boolean;
}

/**
 * Login credentials for signing in.
 */
export interface LoginCredentials {
  /** User email address */
  email: string;

  /** User password */
  password: string;
}

/**
 * Registration credentials for signing up.
 */
export interface RegisterCredentials {
  /** User email address */
  email: string;

  /** User password */
  password: string;

  /** Password confirmation */
  confirmPassword?: string;
}

/**
 * Error response from the authentication API.
 */
export interface AuthError {
  /** Error message */
  message: string;

  /** HTTP status code */
  statusCode?: number;

  /** Error code */
  code?: string;

  /** Field-specific errors */
  details?: Record<string, string>;
}
