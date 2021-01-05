import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AntibodiesComponent } from './antibodies.component';

describe('AntibodiesComponent', () => {
  let component: AntibodiesComponent;
  let fixture: ComponentFixture<AntibodiesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [AntibodiesComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AntibodiesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
