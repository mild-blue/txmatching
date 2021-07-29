import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ReportConfig } from '@app/components/generate-report/generate-report.interface';

@Component({
  selector: 'app-generate-report',
  templateUrl: './generate-report.component.html',
  styleUrls: ['./generate-report.component.scss']
})
export class GenerateReportComponent implements OnInit {

  @Input() loading: boolean = false;
  @Output() reportConfigSubmitted: EventEmitter<ReportConfig> = new EventEmitter<ReportConfig>();

  public reportConfigForm: FormGroup;

  constructor(private _formBuilder: FormBuilder) {
    this.reportConfigForm = this._formBuilder.group({
      matchingsBelowChosen: [0, [Validators.required, Validators.min(0)]],
      includePatientsSection: [false, Validators.required]
    });
  }

  ngOnInit(): void {
  }

  public onSubmit() {
    if (!this.isValid) {
      return;
    }

    const { matchingsBelowChosen, includePatientsSection } = this.reportConfigForm.controls;

    this.reportConfigSubmitted.emit({
      matchingsBelowChosen: matchingsBelowChosen.value,
      includePatientsSection: includePatientsSection.value
    });
  }

  public get isValid(): boolean {
    return !this.reportConfigForm.invalid;
  }
}
