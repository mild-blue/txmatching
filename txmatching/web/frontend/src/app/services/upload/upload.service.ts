import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { environment } from "@environments/environment";
import { LoggerService } from "@app/services/logger/logger.service";
import { AlertService } from "@app/services/alert/alert.service";
import { getErrorMessage } from "@app/helpers/error";

@Injectable({
  providedIn: "root",
})
export class UploadService {
  constructor(private _http: HttpClient, private _alertService: AlertService, private _logger: LoggerService) {}

  public uploadFile(txmEventId: number, callbackLabel?: string, callbackAction?: Function): void {
    const input = document.createElement("input");
    input.type = "file";
    input.dispatchEvent(new MouseEvent("click"));
    input.addEventListener("change", () => {
      const fileToUpload = input.files?.item(0);
      if (!fileToUpload) {
        return;
      }

      this._handleUpload(txmEventId, fileToUpload, callbackLabel, callbackAction);
    });
  }

  private _handleUpload(txmEventId: number, file: File, callbackLabel?: string, callbackAction?: Function): void {
    const formData: FormData = new FormData();
    formData.append("file", file, file.name);

    this._http
      .put<File>(`${environment.apiUrl}/txm-event/${txmEventId}/patients/add-patients-file`, formData)
      .subscribe(
        () => {
          this._alertService.success("Patients were uploaded successfully.", callbackLabel, callbackAction);
        },
        (e: Error) => {
          this._alertService.error(`Error uploading patients: "${getErrorMessage(e)}"`);
          this._logger.error(`Error uploading patients: "${getErrorMessage(e)}"`);
        }
      );
  }
}
