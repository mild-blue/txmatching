import { DonorTypeLabelPipe } from '@app/pipes/donor-type-label/donor-type-label.pipe';

describe('DonorTypeLabelPipe', () => {
  it('create an instance', () => {
    const pipe = new DonorTypeLabelPipe();
    expect(pipe).toBeTruthy();
  });
});
