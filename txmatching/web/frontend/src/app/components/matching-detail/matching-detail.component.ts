import { Component, Input } from '@angular/core';
import { DonorType, PatientList } from '@app/model/Patient';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { Matching } from '@app/model/Matching';
import { Subscription } from 'rxjs';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';
import { PatientService } from '@app/services/patient/patient.service';
import { scrollableDetailClass } from '@app/services/ui-interactions/ui-iteractions';
import { Configuration } from '@app/model/Configuration';

@Component({
  selector: 'app-matching-detail',
  templateUrl: './matching-detail.component.html',
  styleUrls: ['./matching-detail.component.scss']
})
export class MatchingDetailComponent extends ListItemDetailAbstractComponent {

  private _activeTransplantSubscription: Subscription = new Subscription();

  @Input() item?: Matching;
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public donorTypes: typeof DonorType = DonorType;

  constructor(private _patientsService: PatientService,
              private _uiInteractionsService: UiInteractionsService) {
    super();

    this._activeTransplantSubscription = this._uiInteractionsService.focusedTransplantId.subscribe(id => {
      if (id) {
        this._scrollToTransplant(id);
      }
    });
  }

  public getDonorTypeLabel(type: DonorType): string {
    return type === DonorType.BRIDGING_DONOR ? 'bridging donor' : type === DonorType.NON_DIRECTED ? 'non-directed donor' : '';
  }

  private _scrollToTransplant(id: number): void {
    const scrollable = document.querySelector(`.${scrollableDetailClass}`);
    const activeTransplantElement: HTMLElement | null = document.querySelector(`#transplant-${id}`);

    if (!scrollable || !activeTransplantElement) {
      return;
    }

    // wait for element to have .active class
    setTimeout(() => {
      scrollable.scrollTop = activeTransplantElement.offsetTop;
    }, 10); // wait 10ms for execution, see https://stackoverflow.com/a/779785/7169288
  }
}
