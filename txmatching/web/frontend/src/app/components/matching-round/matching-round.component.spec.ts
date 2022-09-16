import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { MatchingRoundComponent } from "./matching-round.component";

describe("MatchingRoundComponent", () => {
  let component: MatchingRoundComponent;
  let fixture: ComponentFixture<MatchingRoundComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MatchingRoundComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MatchingRoundComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
