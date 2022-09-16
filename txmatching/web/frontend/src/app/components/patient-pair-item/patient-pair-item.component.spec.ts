import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { PatientPairItemComponent } from "./patient-pair-item.component";

describe("PatientPairItemComponent", () => {
  let component: PatientPairItemComponent;
  let fixture: ComponentFixture<PatientPairItemComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [PatientPairItemComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientPairItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
