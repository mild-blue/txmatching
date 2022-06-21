import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParsingIssueConfirmationComponent } from './parsing-issue-confirmation.compontent';

describe('ParsingIssueConfirmationComponent', () => {
  let component: ParsingIssueConfirmationComponent;
  let fixture: ComponentFixture<ParsingIssueConfirmationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ParsingIssueConfirmationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ParsingIssueConfirmationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
