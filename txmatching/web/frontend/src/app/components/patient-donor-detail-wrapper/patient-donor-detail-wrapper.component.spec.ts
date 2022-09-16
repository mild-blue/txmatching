import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { PatientDonorDetailWrapperComponent } from "./patient-donor-detail-wrapper.component";

describe("PatientDonorDetailWrapperComponent", () => {
  let component: PatientDonorDetailWrapperComponent;
  let fixture: ComponentFixture<PatientDonorDetailWrapperComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientDonorDetailWrapperComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientDonorDetailWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
