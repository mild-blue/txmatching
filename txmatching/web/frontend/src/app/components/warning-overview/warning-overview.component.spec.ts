import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WarningOverviewComponent } from './warning-overview.component';

describe('WarningOverviewComponent', () => {
  let component: WarningOverviewComponent;
  let fixture: ComponentFixture<WarningOverviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WarningOverviewComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WarningOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
