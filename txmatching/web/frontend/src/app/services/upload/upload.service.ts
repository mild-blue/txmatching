import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UploadService {

  constructor(private _http: HttpClient) {
  }

  public uploadFile(file: File): Observable<boolean> {
    const formData: FormData = new FormData();
    formData.append('file', file, file.name);
    return this._http.put<File>(
      `${environment.apiUrl}/patients/add-patients-file`,
      formData
    ).pipe(
      map(() => {
        return true;
      })
    );
  }
}
