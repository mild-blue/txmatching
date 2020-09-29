import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientPairDetailComponent } from './patient-pair-detail.component';

describe('PatientPairDetailComponent', () => {
  let component: PatientPairDetailComponent;
  let fixture: ComponentFixture<PatientPairDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientPairDetailComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientPairDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
