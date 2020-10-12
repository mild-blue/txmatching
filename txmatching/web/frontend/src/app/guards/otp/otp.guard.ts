import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { TokenType } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';

@Injectable({
  providedIn: 'root'
})
export class OtpGuard implements CanActivate {

  constructor(private _router: Router,
              private _authService: AuthService) {
  }

  canActivate(): boolean {
    const currentUser = this._authService.currentUserValue;

    if (currentUser) {
      if (currentUser.decoded.type === TokenType.OTP) {
        return true;
      }

      if (this._authService.isLoggedIn) {
        return false;
      }
    }

    this._router.navigate(['login']);
    return false;
  }
}
