import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Alert, fadeDurationMs } from '@app/model/Alert';
import { Subscription } from 'rxjs';
import { NavigationStart, Router } from '@angular/router';
import { AlertService } from '@app/services/alert/alert.service';
import { AlertType } from '@app/model/enums/AlertType';
import Timeout = NodeJS.Timeout;

@Component({
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss']
})
export class AlertComponent implements OnInit, OnDestroy {

  private _alertSubscription?: Subscription;
  private _routeSubscription?: Subscription;
  private _timeouts: Map<string, Timeout> = new Map<string, Timeout>(); // timeout for each alert id

  @Input() id: string = 'default-alert';
  @Input() fade: boolean = true;
  public alerts: Alert[] = [];

  constructor(private _router: Router,
              private _alertService: AlertService) {
  }

  ngOnInit(): void {
    this._alertSubscription = this._alertService.onAlert(this.id)
    .subscribe(alert => this._showAlert(alert));
  }

  ngOnDestroy(): void {
    this._alertSubscription?.unsubscribe();
    this._routeSubscription?.unsubscribe();

    if (this._timeouts) {
      this._timeouts.forEach((t, key) => clearTimeout(t));
    }
  }

  public removeAlert(alert: Alert): void {
    // check if already removed
    if (!this.alerts.includes(alert)) {
      return;
    }

    // remove alert
    this.alerts = this.alerts.filter(x => x !== alert);
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

    if (alert.type !== undefined) {
      classes.push(alertTypeClass[alert.type]);
    }

    if (alert.fade) {
      classes.push('fade');
    }

    return classes.join(' ');
  }

  public onMouseEnter(alert: Alert): void {
    // cancel fading out
    alert.fade = false;

    // clear timeout for removal
    const timeout = this._timeouts.get(alert.uuid);
    if (timeout) {
      clearTimeout(timeout);
    }
  }

  public onMouseLeave(alert: Alert): void {
    this._fadeOutAlert(alert);
  }

  private _showAlert(alert: Alert): void {
    // add to start
    this.alerts.unshift(alert);
    // begin fading out
    // wait 100ms for previous command
    setTimeout(() => this._fadeOutAlert(alert), 100);
  }

  private _fadeOutAlert(alert: Alert): void {
    if (alert.fadeAutomatically === false) {
      return;
    }

    alert.fade = true;

    // remove alert after faded out
    const timeout = setTimeout(() => this.removeAlert(alert), fadeDurationMs);

    // save timeout for this alert
    this._timeouts.set(alert.uuid, timeout);
  }

  public handleAlertActionClick(alert: Alert): void {
    if (!alert.action) {
      return;
    }

    alert.action();
    this.removeAlert(alert);
  }
}
