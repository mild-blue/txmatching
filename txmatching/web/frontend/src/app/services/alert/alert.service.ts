import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { Alert, AlertType } from '@app/model/Alert';
import { filter } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AlertService {

  private _subject: Subject<Alert> = new Subject<Alert>();
  private _defaultId: string = 'default-alert';

  public onAlert(id = this._defaultId): Observable<Alert> {
    return this._subject.asObservable().pipe(filter(x => x && x.id === id));
  }

  public success(message: string, actionLabel?: string, action?: Function): void {
    this.alert(new Alert({ type: AlertType.Success, message, actionLabel, action }));
  }

  public error(message: string, actionLabel?: string, action?: Function): void {
    this.alert(new Alert({ type: AlertType.Error, message, actionLabel, action }));
  }

  public info(message: string, actionLabel?: string, action?: Function): void {
    this.alert(new Alert({ type: AlertType.Info, message, actionLabel, action }));
  }

  public warn(message: string, actionLabel?: string, action?: Function): void {
    this.alert(new Alert({ type: AlertType.Warning, message, actionLabel, action }));
  }

  public alert(alert: Alert): void {
    alert.id = alert.id || this._defaultId;
    this._subject.next(alert);
  }

  public clear(): void {
    this._subject.next(undefined);
  }
}
