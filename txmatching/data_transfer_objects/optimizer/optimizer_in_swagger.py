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

StatisticsJson = optimizer_api.model('Statistics', {
    'number_of_found_cycles': fields.Integer(required=False),
    'number_of_found_transplants': fields.Integer(required=False)
})

OptimizerReturnObjectJson = optimizer_api.model('OptimizerReturn', {
    'cycles_and_chains': fields.List(required=True,
                                     cls_or_instance=fields.List(cls_or_instance=fields.Nested(DonorToRecipientJson))),
    'statistics': fields.Nested(StatisticsJson, reqired=True)
})

PairJson = optimizer_api.model('Pair', {
    'donor_id': fields.Integer(required=True),
    'recipient_id': fields.Integer(reqired=False)
})

LimitationsJson = optimizer_api.model('Limitations', {
    'max_cycle_length': fields.Integer(reqired=False),
    'max_chain_length': fields.Integer(reqired=False),
    # todo optional
    'custom_algorithm_settings': DictItem(attribute="calling_args")
})

OptimizerConfigurationJson = optimizer_api.model('OptimizerConfiguration', {
    'limitations': fields.Nested(LimitationsJson, reqired=False),
    'scoring': fields.List(required=False, cls_or_instance=fields.List(requred=True, cls_or_instance=DictItem(
        attribute="calling_args"))),
})

OptimizerRequestObjectJson = optimizer_api.model('OptimizerRequest', {
    'compatibility_graph': fields.List(required=True, cls_or_instance=DictItem(attribute="calling_args")),
    'pairs': fields.Nested(PairJson, reqired=True),
    'configuration': fields.Nested(OptimizerConfigurationJson, required=True)
})
