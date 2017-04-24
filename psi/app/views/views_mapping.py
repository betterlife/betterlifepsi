# encoding=utf-8
from psi.app.models import PurchaseOrder
from psi.app import const

views_mapping = {
    # The key should be
    'purchaseorder' : {
        const.DIRECT_PO_TYPE_KEY : 'dpo',
        const.FRANCHISE_PO_TYPE_KEY : 'fpo'
    },
}


def get_endpoint_by_type_attr(value, low_case_model_name):
    """
    Get endpoint of an object based on it's type code
    If there's no type attribute exists for the object,
    It's low case model name will be returned by default
    :param value: value of the object
    :param low_case_model_name: low case model name
    :return: endpoint of the view
    """
    try:
        type_code = value.type.code
        endpoint = views_mapping.get(low_case_model_name).get(type_code)
        if endpoint is None:
            endpoint = low_case_model_name
    except:
        endpoint = low_case_model_name
    return endpoint


