import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '@app/services/auth/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private _router: Router,
              private _authService: AuthService) {
  }

  canActivate(): boolean {
    const currentUser = this._authService.currentUserValue;
    const isTokenValid = this._authService.isLoggedIn;

    if (currentUser && isTokenValid) {
      return true;
    } else {
      this._router.navigate(['login']);
      return false;
    }
  }
}
