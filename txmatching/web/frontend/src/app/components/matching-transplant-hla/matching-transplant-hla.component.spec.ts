import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MatchingTransplantHlaComponent } from './matching-transplant-hla.component';

describe('MatchingTransplantHlaComponent', () => {
  let component: MatchingTransplantHlaComponent;
  let fixture: ComponentFixture<MatchingTransplantHlaComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MatchingTransplantHlaComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MatchingTransplantHlaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
