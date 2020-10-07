import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LoggerService {

  public log(text: string, args?: unknown[]): void {
    if (!environment.production) {
      console.log(text);
      if (args) {
        console.log(...args);
      }
    }
  }

  public error(text: string, args?: unknown[]): void {
    console.error(text);
    if (args) {
      console.error(...args);
    }
  }
}
