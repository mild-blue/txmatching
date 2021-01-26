import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { first, map } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { LoggerService } from '@app/services/logger/logger.service';
import { TxmEvent, TxmEvents } from '@app/model/Event';
import { TxmEventsGenerated } from '@app/generated';
import { parseTxmEvent, parseTxmEvents } from '@app/parsers/event.parsers';

@Injectable({
  providedIn: 'root'
})
export class EventService {

  txmEvents: Promise<TxmEvents>;
  defaultTxmEvent: Promise<TxmEvent>;

  constructor(private _http: HttpClient,
              private _logger: LoggerService) {
    this.txmEvents = this._http.get<TxmEventsGenerated>(
      `${environment.apiUrl}/txm-event`
    ).pipe(
      first(),
      map(parseTxmEvents)
    ).toPromise();

    this.defaultTxmEvent = this._http.get<TxmEvent>(
      `${environment.apiUrl}/txm-event/default`
    ).pipe(
      first(),
      map(parseTxmEvent)
    ).toPromise();

  }

  public async getEvents(): Promise<TxmEvents> {
    return this.txmEvents;
  }

  public getDefaultEvent(): Promise<TxmEvent> {
    return this.defaultTxmEvent;
  }

  public setDefaultEvent(event_id: number): Promise<TxmEvent> {
    this.defaultTxmEvent = this._http.put<TxmEvent>(
      `${environment.apiUrl}/txm-event/default`,
      {
        id: event_id
      }
    ).pipe(
      first(),
      map(parseTxmEvent)
    ).toPromise();

    return this.defaultTxmEvent;
  }
}
