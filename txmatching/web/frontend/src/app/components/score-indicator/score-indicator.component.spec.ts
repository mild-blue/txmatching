import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScoreIndicatorComponent } from './score-indicator.component';

describe('ScoreIndicatorComponent', () => {
  let component: ScoreIndicatorComponent;
  let fixture: ComponentFixture<ScoreIndicatorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ScoreIndicatorComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScoreIndicatorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
