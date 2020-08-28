import { Component } from '@angular/core';
import { User } from '@app/model/User';
import { Router } from '@angular/router';
import { AuthService } from '@app/services/auth/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  currentUser?: User;

  constructor(private _router: Router,
              private _authService: AuthService
  ) {
    this._authService.currentUser.subscribe(x => this.currentUser = x);
  }

  logout() {
    this._authService.logout();
    this._router.navigate(['/login']);
  }
}
