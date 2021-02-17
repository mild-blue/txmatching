import { DonorEditable } from '../../model/DonorEditable';
import { DonorModelToUpdateGenerated } from '../../generated';
import { fromPatientEditable } from './patient.parsers';

export const fromDonorEditable = ( donor: DonorEditable, donorId: number ): DonorModelToUpdateGenerated => {
  return {
    ...fromPatientEditable(donor, donorId),
    active: true // donor.active // TODOO
  };
};
