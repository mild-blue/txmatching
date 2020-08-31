import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LoggerService {

  constructor() {
  }

  public log(text: string, args?: any[]): void {
    if (!environment.production) {
      console.log(text);
      if (args) {
        console.log(...args);
      }
    }
  }
}
