import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UiInteractionsService {

  private _focusedTransplantId: BehaviorSubject<number | undefined> = new BehaviorSubject<number | undefined>(undefined);
  public focusedTransplantId: Observable<number | undefined> = this._focusedTransplantId.asObservable();

  constructor() {
  }

  getFocusedTransplantId(): number | undefined {
    return this._focusedTransplantId.value;
  }

  setFocusedTransplantId(id: number): void {
    this._focusedTransplantId.next(id);
  }
}
