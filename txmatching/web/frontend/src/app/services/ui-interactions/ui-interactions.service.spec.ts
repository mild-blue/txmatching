import { TestBed } from '@angular/core/testing';

import { UiInteractionsService } from './ui-interactions.service';

describe('UiInteractionsService', () => {
  let service: UiInteractionsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UiInteractionsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
