import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AbstractFormHandlerComponent } from './abstract-form-handler.component';

describe('AbstractFormHandlerComponent', () => {
  let component: AbstractFormHandlerComponent;
  let fixture: ComponentFixture<AbstractFormHandlerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [AbstractFormHandlerComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AbstractFormHandlerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
