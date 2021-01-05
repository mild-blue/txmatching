import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientDetailDonorComponent } from './patient-detail-donor.component';

describe('PatientDetailDonorComponent', () => {
  let component: PatientDetailDonorComponent;
  let fixture: ComponentFixture<PatientDetailDonorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientDetailDonorComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientDetailDonorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
