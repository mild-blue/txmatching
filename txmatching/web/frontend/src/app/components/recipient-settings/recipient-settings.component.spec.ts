import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { RecipientSettingsComponent } from "./recipient-settings.component";

describe("RecipientSettingsComponent", () => {
  let component: RecipientSettingsComponent;
  let fixture: ComponentFixture<RecipientSettingsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [RecipientSettingsComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RecipientSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
