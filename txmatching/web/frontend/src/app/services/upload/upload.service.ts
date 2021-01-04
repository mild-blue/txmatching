import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments/environment';
import { LoggerService } from '@app/services/logger/logger.service';
import { AlertService } from '@app/services/alert/alert.service';

@Injectable({
  providedIn: 'root'
})
export class UploadService {

  constructor(private _http: HttpClient,
              private _alertService: AlertService,
              private _logger: LoggerService) {
  }

  public uploadFile(callbackLabel?: string, callbackAction?: Function): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.dispatchEvent(new MouseEvent('click'));
    input.addEventListener('change', () => {
      const fileToUpload = input.files?.item(0);
      if (!fileToUpload) {
        return;
      }

      this._handleUpload(fileToUpload, callbackLabel, callbackAction);
    });
  }

  private _handleUpload(file: File, callbackLabel?: string, callbackAction?: Function): void {

    const formData: FormData = new FormData();
    formData.append('file', file, file.name);

    this._http.put<File>(
      `${environment.apiUrl}/patients/add-patients-file`,
      formData
    ).subscribe(
      () => {
        this._alertService.success('Patients were uploaded successfully.', callbackLabel, callbackAction);
      },
      (e: Error) => {
        this._alertService.error(`Error uploading patients: "${e.message || e}"`);
        this._logger.error(`Error uploading patients: "${e.message || e}"`);
      });
  }
}
