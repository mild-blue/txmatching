import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { AuthService } from "@app/services/auth/auth.service";
import { UserTokenType } from "@app/model/enums/UserTokenType";

@Injectable({
  providedIn: "root",
})
export class OtpGuard implements CanActivate {
  constructor(private _router: Router, private _authService: AuthService) {}

  canActivate(): boolean {
    const currentUser = this._authService.currentUserValue;

    if (currentUser) {
      if (currentUser.decoded.type === UserTokenType.OTP) {
        return true;
      }

      if (this._authService.isLoggedIn) {
        return false;
      }
    }

    this._router.navigate(["login"]);
    return false;
  }
}
