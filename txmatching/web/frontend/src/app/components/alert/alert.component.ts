import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Alert, AlertType } from '@app/model/Alert';
import { Subscription } from 'rxjs';
import { NavigationStart, Router } from '@angular/router';
import { AlertService } from '@app/services/alert/alert.service';

@Component({
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss']
})
export class AlertComponent implements OnInit, OnDestroy {

  @Input() id = 'default-alert';
  @Input() fade = true;

  alerts: Alert[] = [];
  alertSubscription?: Subscription;
  routeSubscription?: Subscription;

  constructor(private router: Router,
              private alertService: AlertService) {
  }

  ngOnInit(): void {
    this.alertSubscription = this.alertService.onAlert(this.id)
    .subscribe(alert => this.alerts.push(alert));

    this.routeSubscription = this.router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        this.alertService.clear(this.id);
      }
    });
  }

  ngOnDestroy(): void {
    this.alertSubscription?.unsubscribe();
    this.routeSubscription?.unsubscribe();
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
    }, 250);
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

    if(alert.type) {
      classes.push(alertTypeClass[alert.type]);
    }

    if (alert.fade) {
      classes.push('fade');
    }

    return classes.join(' ');
  }

}
