import { Injectable } from '@angular/core';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { AuthService } from '@app/services/auth/auth.service';
import { catchError } from 'rxjs/operators';
import { ResponseStatusCode } from '@app/services/auth/auth.interface';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {

  constructor(private _authService: AuthService) {
  }

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(catchError(err => {
      if (err.status === ResponseStatusCode.UNAUTHORIZED) {
        // auto logout if 401 response returned from api
        this._authService.logout();
      }

      const error = err.error.message || err.statusText;
      return throwError(error);
    }));
  }
}
