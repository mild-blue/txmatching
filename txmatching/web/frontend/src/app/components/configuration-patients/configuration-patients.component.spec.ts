import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurationPatientsComponent } from './configuration-patients.component';

describe('ConfigurationPatientsComponent', () => {
  let component: ConfigurationPatientsComponent;
  let fixture: ComponentFixture<ConfigurationPatientsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ConfigurationPatientsComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationPatientsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
