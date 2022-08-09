from flask_restx import fields

from txmatching.web.web_utils.namespaces import optimizer_api

class DictItem(fields.Raw):
    def output(self, key, obj, *args, **kwargs):
        try:
            dct = getattr(obj, self.attribute)
        except AttributeError:
            return {}
        return dct or {}

DonorToRecipientJson = optimizer_api.model('DonorToRecipient', {
    'donor_id': fields.Integer(required=True),
    'recipient_id': fields.Integer(required=True),
    'score': fields.List(required=True, cls_or_instance=fields.Integer)
})

OptimizerReturnObjectJson = optimizer_api.model('OptimizerReturn', {
    'cycles_and_chains': fields.List(required=True, cls_or_instance=fields.Nested(
        fields.List(cls_or_instance=fields.Nested(DonorToRecipientJson)))),
    'statistics': DictItem(attribute="calling_args")
})
