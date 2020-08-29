import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { Configuration } from '@app/model/Configuration';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss']
})
export class ConfigurationComponent implements OnInit {

  @Input() isOpened: boolean = false;
  @Input() configuration?: Configuration;
  @Output() configSubmitted: EventEmitter<Configuration> = new EventEmitter<Configuration>();
  public configForm?: FormGroup;

  constructor(private _formBuilder: FormBuilder) {
  }

  ngOnInit(): void {
    this._buildFormFromConfig();
  }

  private _buildFormFromConfig(): void {
    if (!this.configuration) {
      return;
    }

    const group: { [key: string]: AbstractControl; } = {};

    const names: string[] = Object.keys(this.configuration);
    for (let name of names) {
      const value = this.configuration[name];
      group[name] = new FormControl(value);
    }

    this.configForm = new FormGroup(group);
  }

  public submitAction(): void {
    if (this.configForm) {
      this.configSubmitted.emit(this.configForm.value);
    }
  }
}
