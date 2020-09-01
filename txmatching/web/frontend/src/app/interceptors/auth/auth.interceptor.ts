import { Injectable } from '@angular/core';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '@app/services/auth/auth.service';
import { LoggerService } from '@app/services/logger/logger.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private _authService: AuthService,
              private _logger: LoggerService) {
  }

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (this._authService.isLoggedIn) {
      const currentUser = this._authService.currentUserValue;

      if (currentUser) {
        this._logger.log('Adding auth headers to request');
        request = request.clone({
          setHeaders: {
            Authorization: `Bearer ${currentUser.token}`
          }
        });
      }
    }

    this._logger.log('Proceeding to handle the request');
    return next.handle(request);
  }
}
