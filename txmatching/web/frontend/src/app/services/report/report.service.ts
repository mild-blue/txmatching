import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { first } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  constructor(private _http: HttpClient) {
  }

  public async downloadReport(matchingId: number): Promise<unknown> {
    return this._http.get<unknown>(
      `${environment.apiUrl}/reports/${matchingId}`
    ).pipe(first()).toPromise();
  }
}
