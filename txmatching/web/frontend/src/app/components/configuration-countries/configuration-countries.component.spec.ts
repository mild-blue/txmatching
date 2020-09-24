import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurationCountriesComponent } from './configuration-countries.component';

describe('ConfigurationCountriesComponent', () => {
  let component: ConfigurationCountriesComponent;
  let fixture: ComponentFixture<ConfigurationCountriesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ConfigurationCountriesComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationCountriesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
