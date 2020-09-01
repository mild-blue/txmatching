import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Alert, AlertType, fadeDuration } from '@app/model/Alert';
import { Subscription } from 'rxjs';
import { NavigationStart, Router } from '@angular/router';
import { AlertService } from '@app/services/alert/alert.service';

@Component({
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss']
})
export class AlertComponent implements OnInit, OnDestroy {

  @Input() id: string = 'default-alert';
  @Input() fade: boolean = true;
  public alerts: Alert[] = [];
  private _alertSubscription?: Subscription;
  private _routeSubscription?: Subscription;

  constructor(private _router: Router,
              private _alertService: AlertService) {
  }

  ngOnInit(): void {
    this._alertSubscription = this._alertService.onAlert(this.id)
    .subscribe(alert => this.alerts.push(alert));

    this._routeSubscription = this._router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        this._alertService.clear(this.id);
      }
    });
  }

  ngOnDestroy(): void {
    this._alertSubscription?.unsubscribe();
    this._routeSubscription?.unsubscribe();
  }

  public removeAlert(alert: Alert): void {
    // check if already removed to prevent error on auto close
    if (!this.alerts.includes(alert)) {
      return;
    }

    // fade out alert
    const foundAlert = this.alerts.find(x => x === alert);
    if (foundAlert) {
      foundAlert.fade = true;
    }

    // remove alert after faded out
    setTimeout(() => {
      this.alerts = this.alerts.filter(x => x !== alert);
    }, fadeDuration);
  }

  public getClass(alert: Alert): string {
    if (!alert) {
      return '';
    }

    const classes = ['alert', 'alert-dismissable'];

    const alertTypeClass = {
      [AlertType.Success]: 'alert alert-success',
      [AlertType.Error]: 'alert alert-danger',
      [AlertType.Info]: 'alert alert-info',
      [AlertType.Warning]: 'alert alert-warning'
    };

    if (alert.type) {
      classes.push(alertTypeClass[alert.type]);
    }

    if (alert.fade) {
      classes.push('fade');
    }

    return classes.join(' ');
  }

}
