import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { PatientDonorItemComponent } from "./patient-donor-item.component";

describe("PatientDonorItemComponent", () => {
  let component: PatientDonorItemComponent;
  let fixture: ComponentFixture<PatientDonorItemComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientDonorItemComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientDonorItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
