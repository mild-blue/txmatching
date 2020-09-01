import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchingTransplantComponent } from './matching-transplant.component';

describe('MatchingTransplantComponent', () => {
  let component: MatchingTransplantComponent;
  let fixture: ComponentFixture<MatchingTransplantComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MatchingTransplantComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MatchingTransplantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
