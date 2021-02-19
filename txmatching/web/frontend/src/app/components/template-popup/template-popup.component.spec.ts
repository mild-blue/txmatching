import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TemplatePopupComponent } from './template-popup.component';

describe('TemplatePopupComponent', () => {
  let component: TemplatePopupComponent;
  let fixture: ComponentFixture<TemplatePopupComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [TemplatePopupComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TemplatePopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
