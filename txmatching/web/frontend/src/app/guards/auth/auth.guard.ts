import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '@app/services/auth/auth.service';
import { TokenType } from '@app/model/User';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private _router: Router,
              private _authService: AuthService) {
  }

  canActivate(): boolean {
    const currentUser = this._authService.currentUserValue;
    const isLoggedIn = this._authService.isLoggedIn;

    if (currentUser) {
      if (currentUser.decoded.type === TokenType.OTP) {
        this._router.navigate(['authentication']);
        return false;
      }

      if (isLoggedIn) {
        return true;
      }
    }

    this._router.navigate(['login']);
    return false;
  }
}
