import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AbstractLoggedComponent } from './abstract-logged.component';

describe('AbstractLoggedComponent', () => {
  let component: AbstractLoggedComponent;
  let fixture: ComponentFixture<AbstractLoggedComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AbstractLoggedComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AbstractLoggedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
