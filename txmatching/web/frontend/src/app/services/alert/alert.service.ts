import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";
import { Alert } from "@app/model/Alert";
import { filter } from "rxjs/operators";
import { AlertType } from "@app/model/enums/AlertType";
import { ParsingIssue } from "@app/model/ParsingIssue";
import { ParsingIssuePublic } from "@app/model/ParsingIssuePublic";

@Injectable({
  providedIn: "root",
})
export class AlertService {
  private _subject: Subject<Alert> = new Subject<Alert>();
  private _defaultId: string = "default-alert";

  public onAlert(id = this._defaultId): Observable<Alert> {
    return this._subject.asObservable().pipe(filter((x) => x && x.id === id));
  }

  public success(message: string, actionLabel?: string, action?: Function, fadeAutomatically?: boolean): void {
    this.alert(new Alert({ type: AlertType.Success, message, actionLabel, action, fadeAutomatically }));
  }

  public error(message: string, actionLabel?: string, action?: Function, fadeAutomatically?: boolean): void {
    this.alert(new Alert({ type: AlertType.Error, message, actionLabel, action, fadeAutomatically }));
  }

  public info(message: string, actionLabel?: string, action?: Function, fadeAutomatically?: boolean): void {
    this.alert(new Alert({ type: AlertType.Info, message, actionLabel, action, fadeAutomatically }));
  }

  public warn(message: string, actionLabel?: string, action?: Function, fadeAutomatically?: boolean): void {
    this.alert(new Alert({ type: AlertType.Warning, message, actionLabel, action, fadeAutomatically }));
  }

  public infoWithParsingIssues(message: string, parsingIssues: ParsingIssuePublic[]): void {
    const parsingIssuesStr = parsingIssues
      .map((parsingIssue) => {
        if (parsingIssue.hlaCodeOrGroup != null) {
          return `<strong>${parsingIssue.hlaCodeOrGroup}</strong>: ${parsingIssue.message}`;
        } else {
          return `${parsingIssue.message}`;
        }
      })
      .join("<br>");
    this.info(`${message}<br><br>${parsingIssuesStr}`);
  }

  public alert(alert: Alert): void {
    alert.id = alert.id || this._defaultId;
    this._subject.next(alert);
  }
}
