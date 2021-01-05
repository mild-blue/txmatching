import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientRecipientDetailComponent } from './patient-recipient-detail.component';

describe('PatientDetailRecipientComponent', () => {
  let component: PatientRecipientDetailComponent;
  let fixture: ComponentFixture<PatientRecipientDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientRecipientDetailComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientRecipientDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
