import { ComponentFixture, TestBed } from "@angular/core/testing";

import { WarningPillComponent } from "./warning-pill.component";

describe("WarningPillComponent", () => {
  let component: WarningPillComponent;
  let fixture: ComponentFixture<WarningPillComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [WarningPillComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WarningPillComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
