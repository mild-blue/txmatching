import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DonorSettingsComponent } from './donor-settings.component';

describe('DonorSettingsComponent', () => {
  let component: DonorSettingsComponent;
  let fixture: ComponentFixture<DonorSettingsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [DonorSettingsComponent]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DonorSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
