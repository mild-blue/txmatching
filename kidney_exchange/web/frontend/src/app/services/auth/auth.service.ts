import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { User } from '@app/model/User';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';
import { AuthResponse } from '@app/services/auth/auth.interface';
import decode from 'jwt-decode';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  public currentUser: Observable<User>;
  private currentUserSubject: BehaviorSubject<User>;

  constructor(private http: HttpClient) {
    this.currentUserSubject = new BehaviorSubject(JSON.parse(localStorage.getItem('user')));
    this.currentUser = this.currentUserSubject.asObservable();
  }

  get currentUserValue(): User {
    return this.currentUserSubject.value;
  }

  get isTokenValid(): boolean {
    const user = this.currentUserValue;
    if (!user) {
      return false;
    }

    const decoded = decode(user.token);
    return decoded.exp >= Date.now() / 1000;
  }

  login(email: string, password: string) {
    return this.http.post(
      `${environment.apiUrl}/user/login`,
      { email, password }
    ).pipe(
      map((response: AuthResponse) => {
        const token = response.auth_token;
        const user: User = { email, token };
        localStorage.setItem('user', JSON.stringify(user));
        this.currentUserSubject.next(user);
        return user;
      })
    );
  }

  logout() {
    localStorage.removeItem('user');
    this.currentUserSubject.next(null);
  }
}
