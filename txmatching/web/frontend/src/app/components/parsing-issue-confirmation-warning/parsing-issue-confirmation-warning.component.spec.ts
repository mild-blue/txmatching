import { ComponentFixture, TestBed } from "@angular/core/testing";

import { ParsingIssueConfirmationWarningComponent } from "./parsing-issue-confirmation-warning.compontent";

describe("ParsingIssueConfirmationWarningComponent", () => {
  let component: ParsingIssueConfirmationWarningComponent;
  let fixture: ComponentFixture<ParsingIssueConfirmationWarningComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ParsingIssueConfirmationWarningComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ParsingIssueConfirmationWarningComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
