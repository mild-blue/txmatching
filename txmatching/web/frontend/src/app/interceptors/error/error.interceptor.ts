import { Injectable } from '@angular/core';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '@app/services/auth/auth.service';
import { catchError } from 'rxjs/operators';
import { ResponseStatusCode } from '@app/services/auth/auth.interface';
import { TokenType } from '@app/model/User';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {

  constructor(private _authService: AuthService) {
  }

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(catchError(err => {

      if (err.status === ResponseStatusCode.UNAUTHORIZED) {
        // auto logout if 401 response returned from api
        // and token does not have OTP type
        if (this._authService.currentUserValue?.decoded.type !== TokenType.OTP) {
          this._authService.logout();
        }
      }

      let error = err.error.error || err.statusText;

      if (err.error.detail) {
        error += ` ${err.error.detail}`;
      }

      throw new Error(error);
    }));
  }
}
