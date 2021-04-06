import { ParsingErrorGenerated } from '../generated';
import { ParsingError } from '../model/ParsingError';

export const parseParsingError = (data: ParsingErrorGenerated): ParsingError => {
  return {
    hlaCode: data.hla_code,
    hlaCodeProcessingResultDetail: data.hla_code_processing_result_detail,
    message: data.message,
    medicalId: data.medical_id,
    eventId: data.txm_event_id
  };
};
