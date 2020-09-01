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

  public success(message: string): void {
    this.alert(new Alert({ type: AlertType.Success, message }));
  }

  public error(message: string): void {
    this.alert(new Alert({ type: AlertType.Error, message }));
  }

  public info(message: string): void {
    this.alert(new Alert({ type: AlertType.Info, message }));
  }

  public warn(message: string): void {
    this.alert(new Alert({ type: AlertType.Warning, message }));
  }

  public alert(alert: Alert): void {
    alert.id = alert.id || this._defaultId;
    this._subject.next(alert);
  }

  public clear(id = this._defaultId): void {
    this._subject.next(new Alert({ id }));
  }
}
