import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SimpleNumberComponent } from './simple-number.component';

describe('SimpleNumberComponent', () => {
  let component: SimpleNumberComponent;
  let fixture: ComponentFixture<SimpleNumberComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [SimpleNumberComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SimpleNumberComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
