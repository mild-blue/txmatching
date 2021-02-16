import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { DonorType } from '@app/model';
import { DonorEditable } from '@app/model/DonorEditable';
import { RecipientEditable } from '@app/model/RecipientEditable';
import { PatientService } from '@app/services/patient/patient.service';
import { TxmEvent } from '@app/model/Event';

@Component({
  selector: 'app-add-new-patient',
  templateUrl: './add-new-patient.component.html',
  styleUrls: ['./add-new-patient.component.scss']
})
export class AddNewPatientComponent implements OnInit {

  @Input() defaultTxmEvent?: TxmEvent;
  @Output() patientsAdded: EventEmitter<void> = new EventEmitter<void>();

  public DonorType: typeof DonorType = DonorType;

  public donor: DonorEditable = new DonorEditable();
  public recipient: RecipientEditable = new RecipientEditable();

  public loading: boolean = false;
  public success: boolean = false;

  constructor(private _patientService: PatientService) {
  }

  ngOnInit() {
  }

  public handleSubmit() {

    console.log(this.donor, this.recipient);
    if (!this.defaultTxmEvent) {
      return;
    }

    const recipient = this.donor.type === DonorType.DONOR.valueOf() ? this.recipient : undefined;

    this._patientService.addNewPair(this.defaultTxmEvent.id, this.donor, recipient)
    .then(() => this.patientsAdded.emit());
  }
}
