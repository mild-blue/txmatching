import { Injectable } from "@angular/core";
import { environment } from "@environments/environment";
import { map } from "rxjs/operators";
import { HttpClient } from "@angular/common/http";
import { TxmEvent, TxmEvents } from "@app/model/Event";
import { TxmEventGenerated, TxmEventsGenerated } from "@app/generated";
import { parseTxmEvent, parseTxmEvents } from "@app/parsers/event.parsers";
import { AuthService } from "@app/services/auth/auth.service";
import { firstValueFrom, Subscription } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class EventService {
  private _txmEvents?: Promise<TxmEvents>;
  private _defaultTxmEvent?: Promise<TxmEvent>;
  private _userSubscription: Subscription;
  // TODO: move elsewhere https://github.com/mild-blue/txmatching/issues/481
  private _configId?: number;

  constructor(private _http: HttpClient, private _authService: AuthService) {
    // Remove cached events when user changes
    this._userSubscription = this._authService.currentUser.subscribe((_) => {
      this._txmEvents = undefined;
      this._defaultTxmEvent = undefined;
      this._configId = undefined;
    });
  }

  public invalidateTxmEvents() {
    this._txmEvents = undefined;
    this._defaultTxmEvent = undefined;
  }

  public async getEvents(): Promise<TxmEvents> {
    if (!this._txmEvents) {
      this._txmEvents = firstValueFrom(
        this._http.get<TxmEventsGenerated>(`${environment.apiUrl}/txm-event`).pipe(map(parseTxmEvents))
      );
    }
    return this._txmEvents;
  }

  public async getDefaultEvent(): Promise<TxmEvent> {
    if (!this._defaultTxmEvent) {
      this._defaultTxmEvent = firstValueFrom(
        this._http.get<TxmEvent>(`${environment.apiUrl}/txm-event/default`).pipe(map(parseTxmEvent))
      );
    }
    return this._defaultTxmEvent;
  }

  public async setDefaultEvent(eventId: number): Promise<TxmEvent> {
    this._defaultTxmEvent = firstValueFrom(
      this._http
        .put<TxmEventGenerated>(`${environment.apiUrl}/txm-event/default`, {
          id: eventId,
        })
        .pipe(map(parseTxmEvent))
    );

    this._configId = undefined;
    return this._defaultTxmEvent;
  }

  // TODO: move elsewhere https://github.com/mild-blue/txmatching/issues/481
  public setConfigId(configId: number) {
    this._configId = configId;
  }

  public getConfigId(): number | undefined {
    return this._configId;
  }
}
