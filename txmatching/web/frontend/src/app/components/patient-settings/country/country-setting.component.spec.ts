import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { CountrySettingComponent } from "./country-setting.component";

describe("CountryComponent", () => {
  let component: CountrySettingComponent;
  let fixture: ComponentFixture<CountrySettingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [CountrySettingComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CountrySettingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
