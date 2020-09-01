import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { User } from '@app/model/User';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';
import { AuthResponse, DecodedToken } from '@app/services/auth/auth.interface';
import * as jwt_decode from 'jwt-decode';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private _currentUserSubject: BehaviorSubject<User | undefined> = new BehaviorSubject<User | undefined>(undefined);
  public currentUser: Observable<User | undefined> = this._currentUserSubject.asObservable();

  constructor(private _http: HttpClient) {
    this._setCurrentUser();
  }

  get currentUserValue(): User | undefined {
    return this._currentUserSubject.value;
  }

  get isLoggedIn(): boolean {
    // check if user exists
    const user = this.currentUserValue;
    if (!user) {
      return false;
    }

    // check if token is valid
    const decoded = jwt_decode(user.token) as DecodedToken;
    return decoded.exp >= Date.now() / 1000;
  }

  public login(email: string, password: string): Observable<User> {
    return this._http.post(
      `${environment.apiUrl}/user/login`,
      { email, password }
    ).pipe(
      map((r: Object) => {
        const response = r as AuthResponse;
        const token = response.auth_token;
        const user: User = { email, token };
        localStorage.setItem('user', JSON.stringify(user));
        this._currentUserSubject.next(user);
        return user;
      })
    );
  }

  public logout(): void {
    localStorage.removeItem('user');
    this._currentUserSubject.next(undefined);
  }

  private _setCurrentUser(): void {
    const lsUser = localStorage.getItem('user');
    if (lsUser) {
      this._currentUserSubject.next(JSON.parse(lsUser));
      this.currentUser = this._currentUserSubject.asObservable();
    }
  }
}
