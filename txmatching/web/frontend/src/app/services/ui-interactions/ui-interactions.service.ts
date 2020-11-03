import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UiInteractionsService {

  private _focusedTransplantId: BehaviorSubject<number | undefined> = new BehaviorSubject<number | undefined>(undefined);
  private _lastViewedItemId: BehaviorSubject<number | undefined> = new BehaviorSubject<number | undefined>(undefined);

  public focusedTransplantId: Observable<number | undefined> = this._focusedTransplantId.asObservable();
  public lastViewedItemId: Observable<number | undefined> = this._lastViewedItemId.asObservable();

  setFocusedTransplantId(id: number): void {
    this._focusedTransplantId.next(id);
  }

  setLastViewedPair(id: number): void {
    this._lastViewedItemId.next(id);
  }

  getLastViewedItemId(): number | undefined {
    return this._lastViewedItemId.value;
  }
}
