import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchingsExplorerComponent } from './matchings-explorer.component';

describe('MatchingExplorerComponent', () => {
  let component: MatchingsExplorerComponent;
  let fixture: ComponentFixture<MatchingsExplorerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MatchingsExplorerComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MatchingsExplorerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
