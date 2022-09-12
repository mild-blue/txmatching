import { ComponentFixture, TestBed } from "@angular/core/testing";

import { IncompatibilityPillComponent } from "./incompatibility-pill.component";

describe("IncompatibilityPillComponent", () => {
  let component: IncompatibilityPillComponent;
  let fixture: ComponentFixture<IncompatibilityPillComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [IncompatibilityPillComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IncompatibilityPillComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
