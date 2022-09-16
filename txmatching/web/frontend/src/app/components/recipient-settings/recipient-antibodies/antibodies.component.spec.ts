import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { RecipientAntibodiesComponent } from "./antibodies.component";

describe("AntibodiesComponent", () => {
  let component: RecipientAntibodiesComponent;
  let fixture: ComponentFixture<RecipientAntibodiesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [RecipientAntibodiesComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RecipientAntibodiesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
