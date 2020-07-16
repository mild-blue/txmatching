import logging

from kidney_exchange.scorers.hla_additive_scorer import BLOOD_GROUP_COMPATIBILITY_BONUS
from kidney_exchange.utils.blood_groups import COMPATIBLE_BLOOD_GROUPS
from kidney_exchange.web import create_app

app = create_app()
logger = logging.getLogger(__name__)


@app.template_filter('intersect')
def intersect(a, b):
    return list(set(a) & set(b))


@app.template_filter('filtered_count_by_prefix')
def filtered_count(items, prefix):
    return len(list(x for x in items if x.lower().startswith(prefix.lower())))


@app.template_filter('blood_group_compatibility_bonus')
def blood_group_compatibility_bonus(donor_bg, recipient_bg):
    if donor_bg in COMPATIBLE_BLOOD_GROUPS[recipient_bg]:
        return BLOOD_GROUP_COMPATIBILITY_BONUS
    else:
        return 0.0


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
