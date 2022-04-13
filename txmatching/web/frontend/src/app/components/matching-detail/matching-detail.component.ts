import { Component, Input, OnDestroy } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { Matching } from '@app/model/Matching';
import { Subscription } from 'rxjs';
import { UiInteractionsService } from '@app/services/ui-interactions/ui-interactions.service';
import { PatientService } from '@app/services/patient/patient.service';
import { scrollableDetailClass } from '@app/services/ui-interactions/ui-iteractions';
import { Configuration } from '@app/model/Configuration';
import { PatientList } from '@app/model/PatientList';
import { DonorType } from '@app/model/enums/DonorType';
import { countAllMessages } from '@app/helpers/messages';

@Component({
  selector: 'app-matching-detail',
  templateUrl: './matching-detail.component.html',
  styleUrls: ['./matching-detail.component.scss']
})
export class MatchingDetailComponent extends ListItemDetailAbstractComponent implements OnDestroy {

  private _activeTransplantSubscription: Subscription = new Subscription();

  @Input() item?: Matching;
  @Input() patients?: PatientList;
  @Input() configuration?: Configuration;

  public donorTypes: typeof DonorType = DonorType;
  public allMessagesCount: number = 0;

  public testData: string[] =
    ['Cupcake ipsum dolor sit amet gummi bears.',
      'Cotton candy tootsie roll donut gummies tart.',
      'Gummi bears gummi bears croissant wafer tiramisu dessert sweet dessert.'];

  constructor(private _patientsService: PatientService,
              private _uiInteractionsService: UiInteractionsService) {
    super();

    this._activeTransplantSubscription = this._uiInteractionsService.focusedTransplantId.subscribe(id => {
      if (id) {
        this._scrollToTransplant(id);
      }
    });
  }

  ngOnDestroy(): void {
    this._activeTransplantSubscription.unsubscribe();
  }

  countAllMessages = countAllMessages;

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
