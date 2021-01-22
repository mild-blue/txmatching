import logging


class PatientAdapter(logging.LoggerAdapter):
    """
    To be used when we need to provided context of a patient to a logging message
    """
    def process(self, msg, kwargs):
        return '[%s] %s' % (self.extra['patient_medical_id'], msg), kwargs
