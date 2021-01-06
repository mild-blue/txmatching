import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientDonorDetailComponent } from './patient-donor-detail.component';

describe('PatientDetailDonorComponent', () => {
  let component: PatientDonorDetailComponent;
  let fixture: ComponentFixture<PatientDonorDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientDonorDetailComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientDonorDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
