import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { first } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

const otherMatchingsCount = 5;

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  constructor(private _http: HttpClient) {
  }

  public downloadReport(matchingId: number): Observable<Blob> {
    const httpOptions: Object = {
      responseType: 'blob'
    };

    return this._http.get<Blob>(
      `${environment.apiUrl}/reports/${matchingId}?matchingsBelowChosen=${otherMatchingsCount}`,
      httpOptions
    ).pipe(first());
  }
}
