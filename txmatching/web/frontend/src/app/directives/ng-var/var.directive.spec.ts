import { VarDirective } from './var.directive';
import { TestBed } from '@angular/core/testing';

describe('NgVarDirective', () => {
  let directive: VarDirective;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    directive = TestBed.inject(VarDirective);
  });

  it('should create an instance', () => {
    expect(directive).toBeTruthy();
  });
});
