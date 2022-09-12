export interface AuthResponse {
  status: string;
  auth_token: string;
}

export enum ResponseStatusCode {
  OK = 200,
  UNAUTHORIZED = 401,
}
