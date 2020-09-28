import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientPairComponent } from './patient-pair.component';

describe('PatientPairComponent', () => {
  let component: PatientPairComponent;
  let fixture: ComponentFixture<PatientPairComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientPairComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientPairComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
