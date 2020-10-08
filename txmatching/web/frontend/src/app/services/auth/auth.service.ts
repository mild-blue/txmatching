import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { DecodedToken, TokenType, User } from '@app/model/User';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';
import { AuthResponse } from '@app/services/auth/auth.interface';
import * as jwt_decode from 'jwt-decode';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private _currentUserSubject: BehaviorSubject<User | undefined> = new BehaviorSubject<User | undefined>(undefined);
  public currentUser: Observable<User | undefined> = this._currentUserSubject.asObservable();

  constructor(private _http: HttpClient,
              private _router: Router) {
    this._setCurrentUser();
  }

  get currentUserValue(): User | undefined {
    return this._currentUserSubject.value;
  }

  get isLoggedIn(): boolean {
    const user = this.currentUserValue;
    const token = user?.decoded;

    if (!token) {
      return false;
    }

    // check if token is valid
    return token.type !== TokenType.OTP && token.exp >= Date.now() / 1000;
  }

  public login(email: string, password: string): Observable<User> {
    return this._http.post(
      `${environment.apiUrl}/user/login`,
      { email, password }
    ).pipe(
      map((r: Object) => {
        const response = r as AuthResponse;
        const token = response.auth_token;
        const decoded = jwt_decode(token) as DecodedToken;
        const user: User = { email, token, decoded };

        localStorage.setItem('user', JSON.stringify(user));
        this._currentUserSubject.next(user);

        return user;
      })
    );
  }

  public verify(otp: string): Observable<User> {
    return this._http.post(
      `${environment.apiUrl}/user/otp`,
      { otp }
    ).pipe(
      map((r: Object) => {
        const response = r as AuthResponse;
        const token = response.auth_token;
        if (!token) {
          throw new Error('No access token was present in response');
        }

        const updatedUser = this._updateUserToken(token);
        if (!updatedUser) {
          throw new Error('No user was found');
        }

        return updatedUser;
      })
    );
  }

  public logout(): void {
    localStorage.removeItem('user');
    this._currentUserSubject.next(undefined);
    this._router.navigate(['/login']);
  }

  private _setCurrentUser(): void {
    const lsUser = localStorage.getItem('user');
    if (lsUser) {
      this._currentUserSubject.next(JSON.parse(lsUser));
      this.currentUser = this._currentUserSubject.asObservable();
    }
  }

  private _updateUserToken(token: string): User | undefined {
    const user = this.currentUserValue;
    if (!user) {
      return undefined;
    }

    user.token = token;
    user.decoded = jwt_decode(token) as DecodedToken;

    localStorage.setItem('user', JSON.stringify(user));
    this._currentUserSubject.next(user);

    return user;
  }
}
