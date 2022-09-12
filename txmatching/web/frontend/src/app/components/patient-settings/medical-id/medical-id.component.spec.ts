import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { MedicalIdComponent } from "./medical-id.component";

describe("MedicalIdComponent", () => {
  let component: MedicalIdComponent;
  let fixture: ComponentFixture<MedicalIdComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MedicalIdComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MedicalIdComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
