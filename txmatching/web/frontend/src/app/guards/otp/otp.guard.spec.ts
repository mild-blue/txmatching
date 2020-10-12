import { TestBed } from '@angular/core/testing';

import { OtpGuard } from './otp.guard';

describe('OtpGuard', () => {
  let guard: OtpGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(OtpGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
