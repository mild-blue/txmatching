import { Component, EventEmitter, Input, KeyValueChanges, KeyValueDiffer, KeyValueDiffers, Output, ViewChild } from '@angular/core';
import { DonorType } from '@app/model';
import { DonorEditable } from '@app/model/DonorEditable';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { PatientService } from '@app/services/patient/patient.service';
import { TxmEvent } from '@app/model/Event';
import { PatientEditable } from '@app/model/PatientEditable';
import { Country } from '@app/model/Country';

@Component({
  selector: 'app-add-new-patient',
  templateUrl: './add-new-patient.component.html',
  styleUrls: ['./add-new-patient.component.scss']
})
export class AddNewPatientComponent {

  private _donorDiffer: KeyValueDiffer<string, unknown>;
  private _recipientDiffer: KeyValueDiffer<string, unknown>;

  @Input() defaultTxmEvent?: TxmEvent;
  @Output() patientsAdded: EventEmitter<void> = new EventEmitter<void>();
  @ViewChild('formElement') form?: HTMLFormElement;

  public DonorType: typeof DonorType = DonorType;

  public donor: DonorEditable = new DonorEditable();
  public recipient: RecipientEditable = new RecipientEditable();

  public loading: boolean = false;
  public success: boolean = false;

  constructor(private _patientService: PatientService,
              private _differs: KeyValueDiffers) {
    this._donorDiffer = this._differs.find(this.donor).create();
    this._recipientDiffer = this._differs.find(this.recipient).create();
  }

  ngDoCheck(): void {
    const donorChanges = this._donorDiffer.diff((this.donor as unknown) as Map<string, unknown>);
    const recipientChanges = this._recipientDiffer.diff((this.recipient as unknown) as Map<string, unknown>);
    if (donorChanges) {
      this._changeOtherPatientCountry(donorChanges, this.recipient);
    } else if (recipientChanges) {
      this._changeOtherPatientCountry(recipientChanges, this.donor);
    }
  }

  public handleSubmit() {

    console.log(this.form, this.donor, this.recipient, this.donor.type.valueOf() === DonorType.DONOR.valueOf());
    if (!this.defaultTxmEvent || !this.donor.country || !this.recipient.country ||
      !this.donor.medicalId || !this.recipient.medicalId) {
      return;
    }

    this._patientService.addNewPair(this.defaultTxmEvent.id, this.donor, this.recipient)
    .then(() => this.patientsAdded.emit());
  }

  private _changeOtherPatientCountry(changes: KeyValueChanges<string, unknown>, otherPatient: PatientEditable) {
    changes.forEachChangedItem((record) => {
      if (record.key === 'country') {
        otherPatient.country = record.currentValue as Country;
      }
    });
  }
}
