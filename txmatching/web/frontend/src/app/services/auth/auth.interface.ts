export interface AuthResponse {
  status: string;
  auth_token: string;
}

export interface DecodedToken {
  user_id: number;
  role: string;
  iat: number;
  exp: number;
}
