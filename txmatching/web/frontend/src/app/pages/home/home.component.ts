import { Component, OnInit } from '@angular/core';
import { User } from '@app/model/User';
import { AuthService } from '@app/services/auth/auth.service';
import { faSlidersH } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  public user?: User;
  public configIcon = faSlidersH;

  constructor(private _authService: AuthService) {
  }

  ngOnInit(): void {
    this.user = this._authService.currentUserValue;
  }

}
