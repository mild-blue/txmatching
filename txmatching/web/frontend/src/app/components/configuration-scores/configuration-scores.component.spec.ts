import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { ConfigurationScoresComponent } from "./configuration-scores.component";

describe("ConfigurationScoresComponent", () => {
  let component: ConfigurationScoresComponent;
  let fixture: ComponentFixture<ConfigurationScoresComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ConfigurationScoresComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationScoresComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
