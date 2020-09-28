import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientItemComponent } from './patient-item.component';

describe('PatientItemComponent', () => {
  let component: PatientItemComponent;
  let fixture: ComponentFixture<PatientItemComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientItemComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
