import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Report } from '@app/services/report/report.interface';

const otherMatchingsCount = 10;

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  constructor(private _http: HttpClient) {
  }

  public downloadMatchingPdfReport(txmEventId: number, configId: number | undefined, matchingId: number): Observable<Report> {
    const httpOptions: Object = {
      responseType: 'blob',
      observe: 'response'
    };
    const configIdStr = configId !== undefined ? configId.toString() : 'default';
    // &v=${Date.now()} is done according to https://stackoverflow.com/questions/53207420/how-to-download-new-version-of-file-without-using-the-client-cache
    return this._http.get<HttpResponse<Blob>>(
      `${environment.apiUrl}/txm-event/${txmEventId}/reports/configs/${configIdStr}/matchings/${matchingId}/pdf` +
      `?matchingsBelowChosen=${otherMatchingsCount}` +
      `&includePatientsSection=foo` +
      `&v=${Date.now()}`,
      httpOptions
    ).pipe(
      map((response: HttpResponse<Blob>) => {
        const data = response.body as Blob;
        const filename = response.headers.get('x-filename') ?? this._generateFilename();
        return { data, filename };
      })
    );
  }

  public downloadPatientsXlsxReport(txmEventId: number, configId: number | undefined): Observable<Report> {
    const httpOptions: Object = {
      responseType: 'blob',
      observe: 'response'
    };
    const configIdStr = configId !== undefined ? configId.toString() : 'default';
    // &v=${Date.now()} is done according to https://stackoverflow.com/questions/53207420/how-to-download-new-version-of-file-without-using-the-client-cache
    return this._http.get<HttpResponse<Blob>>(
      `${environment.apiUrl}/txm-event/${txmEventId}/reports/configs/${configIdStr}/patients/xlsx?v=${Date.now()}`,
      httpOptions
    ).pipe(
      map((response: HttpResponse<Blob>) => {
        const data = response.body as Blob;
        const filename = response.headers.get('x-filename') ?? this._generateFilename();
        return { data, filename };
      })
    );
  }

  private _generateFilename(): string {
    const date = new Date();
    return `report_${date.getDate()}_${date.getMonth() + 1}_${date.getFullYear()}.pdf`;
  }
}
