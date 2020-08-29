import { Component, Input, OnInit } from '@angular/core';
import { User } from '@app/model/User';
import { faQuestionCircle, faUserAlt } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  @Input() user?: User;

  public userIcon = faUserAlt;
  public infoIcon = faQuestionCircle;

  constructor() {
  }

  ngOnInit(): void {
  }

}
