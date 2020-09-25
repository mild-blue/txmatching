export interface User {
  email: string;
  token: string;
  decoded: DecodedToken;
}

export interface DecodedToken {
  user_id: number;
  role: Role;
  iat: number;
  exp: number;
}

export enum Role {
  ADMIN = 'ADMIN',
  VIEWER = 'VIEWER',
  EDITOR = 'EDITOR'
}
