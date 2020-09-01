import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchingDetailComponent } from './matching-detail.component';

describe('MatchingDetailComponent', () => {
  let component: MatchingDetailComponent;
  let fixture: ComponentFixture<MatchingDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MatchingDetailComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MatchingDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
