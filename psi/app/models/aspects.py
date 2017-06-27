"""
Logics applies to multiple models can be put here
"""

from sqlalchemy import event
from datetime import datetime
import re

from psi.app.models import Customer, Supplier, Product


@event.listens_for(Customer, 'before_insert')
@event.listens_for(Customer, 'before_update')
@event.listens_for(Supplier, 'before_insert')
@event.listens_for(Supplier, 'before_update')
@event.listens_for(Product, 'before_insert')
@event.listens_for(Product, 'before_update')
def update_menemonic(mapper, conn, target):
    from psi.app.utils import get_pinyin_first_letters
    if hasattr(target, 'get_value_for_mnemonic'):
        val = target.get_value_for_mnemonic()
    else:
        val = target.name
    if val is not None:
        mnemonic = get_pinyin_first_letters(val)
        if mnemonic is not None and hasattr(target, 'mnemonic'):
            try:
                type_str = str(mapper.all_orm_descriptors._data.get('mnemonic').prop.columns[0].type)
                length_str = re.search("([0-9])+", type_str).group(0)
                length = int(length_str)
            except:
                length = 64
            setattr(target, 'mnemonic', mnemonic[:length])


@event.listens_for(Supplier, 'before_insert')
@event.listens_for(Product, 'before_insert')
def update_create_date(mapper, conn, target):
    if hasattr(target, 'create_date'):
        setattr(target, 'create_date', datetime.now())
