import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientDetailRecipientComponent } from './patient-detail-recipient.component';

describe('PatientDetailRecipientComponent', () => {
  let component: PatientDetailRecipientComponent;
  let fixture: ComponentFixture<PatientDetailRecipientComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientDetailRecipientComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientDetailRecipientComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
