import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { AntigensComponent } from "./antigens.component";

describe("AntigensComponent", () => {
  let component: AntigensComponent;
  let fixture: ComponentFixture<AntigensComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [AntigensComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AntigensComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
