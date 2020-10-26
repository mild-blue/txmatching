import { Component, ElementRef, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { AbstractControl, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { Configuration } from '@app/model/Configuration';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import { PatientList } from '@app/model/PatientList';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss']
})
export class ConfigurationComponent implements OnInit, OnChanges {

  @Input() isOpened: boolean = false;
  @Input() configuration?: Configuration;
  @Input() patients?: PatientList;
  @Output() configSubmitted: EventEmitter<Configuration> = new EventEmitter<Configuration>();
  @Output() configClosed: EventEmitter<void> = new EventEmitter<void>();

  @ViewChild('configElement') configElement?: ElementRef;

  public configForm?: FormGroup;
  public closeIcon = faTimes;

  constructor(private _formBuilder: FormBuilder) {
  }

  ngOnInit(): void {
    this._buildFormFromConfig();
  }

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes && changes.isOpened) {
      const wasOpened = changes.isOpened.previousValue;
      const isOpened = changes.isOpened.currentValue;
      if (!wasOpened && isOpened) {
        this._scrollTop();
      }
    }
  }

  public close(): void {
    this.configClosed.emit();
  }

  public submitAction(): void {
    if (this.configForm && this.configuration) {
      const { manual_donor_recipient_scores, forbidden_country_combinations, required_patient_db_ids } = this.configuration;

      this.configSubmitted.emit({
        ...this.configForm.value,
        manual_donor_recipient_scores,
        forbidden_country_combinations,
        required_patient_db_ids
      });
    }
  }

  private _scrollTop(): void {
    if (this.configElement) {
      const element = this.configElement.nativeElement;
      element.scrollTop = 0;
    }
  }

  private _buildFormFromConfig(): void {
    if (!this.configuration) {
      return;
    }

    const group: { [key: string]: AbstractControl; } = {};

    const names: string[] = Object.keys(this.configuration);
    for (const name of names) {
      const value = this.configuration[name];
      // check if value is primitive
      if (value !== Object(value)) {
        group[name] = new FormControl(value);
      }
    }

    this.configForm = new FormGroup(group);
  }
}
