import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FormControlErrorsComponent } from './form-control-errors.component';

describe('FormControlErrorsComponent', () => {
  let component: FormControlErrorsComponent;
  let fixture: ComponentFixture<FormControlErrorsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [FormControlErrorsComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FormControlErrorsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
