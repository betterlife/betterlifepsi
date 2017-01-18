# encoding=utf-8
from functools import partial

from psi.app.models import Organization
from psi.app.utils.security_util import is_super_admin, is_root_organization
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form import Select2Widget
from flask_babelex import lazy_gettext, gettext
from flask_login import current_user
from sqlalchemy import func
from wtforms import ValidationError

from psi.app.views.base import CycleReferenceValidator
from psi.app.views.base import ModelViewWithAccess


class OrganizationAdmin(ModelViewWithAccess):

    from psi.app.views.formatter import organization_formatter

    uos = 'UPDATE ' + Organization.__tablename__ + ' SET'

    @property
    def can_create(self):
        return is_super_admin()

    @property
    def can_delete(self):
        return is_super_admin()

    def get_query(self):
        return self.get_query_based_on_user(self.model)

    def get_count_query(self):
        return self.get_query_based_on_user(func.count('*'))

    def get_query_based_on_user(self, return_query):
        all_ids = Organization.get_children_self_ids(current_user.organization)
        return (self.session.query(return_query).filter(self.model.id.in_(all_ids))
                if not is_super_admin() else self.session.query(return_query))

    column_list = ('id', 'name', 'description', 'type', 'parent',
                   'immediate_children',)

    column_sortable_list = ('id', 'name', 'description', 'type')

    column_searchable_list = ('name', 'description', 'parent.name',
                              'parent.description', 'lft', 'rgt',
                              'type.code', 'type.display')

    column_labels = dict(
        id=lazy_gettext('id'),
        name=lazy_gettext('Name'),
        description=lazy_gettext('Description'),
        parent=lazy_gettext('Parent Organization'),
        lft=lazy_gettext('Left'),
        rgt=lazy_gettext('Right'),
        type=lazy_gettext('Type'),
        immediate_children=lazy_gettext('Immediate Children'),
        all_children=lazy_gettext('All Children'),
    )

    form_args = dict(
        type=dict(query_factory=Organization.type_filter)
    )

    column_formatters = {
        'immediate_children': organization_formatter,
        'all_children': organization_formatter,
        'parent': organization_formatter
    }
    column_editable_list = ('description',)

    form_excluded_columns = ('lft', 'rgt',)

    form_extra_fields = {
        'parent': QuerySelectField(
            label=lazy_gettext('Parent Organization'),
            query_factory=lambda: Organization.query.all(),
            widget=Select2Widget(),
            allow_blank=False,
        )
    }

    def edit_form(self, obj=None):
        form = super(OrganizationAdmin, self).edit_form(obj)
        # form.parent._data_list is None at this moment, so it's not feasible to change the _data_list attribute directly here
        # to set the query_factory function is the right way to implement a filter.
        form.parent.query_factory = partial(Organization.children_remover, obj)
        # For root organization, allow blank
        if is_root_organization(obj):
            form.parent.allow_blank = True
            # Does not allow to change type for root organization
            delattr(form, "type")
        return form

    column_details_list = ('id', 'name', 'description', 'lft', 'rgt', 'parent', 'immediate_children', 'all_children')

    def after_model_change(self, form, model, is_created):
        """
        :param form: form object from the UI
        :param model: model, when on after_model_change, it has got id field and necessary default value from DB.
        :param is_created: True if model was created, False if model was updated
        :return: None
        Update left and right field of all impacted organization vai raw sql, and also update left and right
        of the newly added organization to it's parent's current right and current right + 1
        """
        from sqlalchemy import text
        from psi.app.service import Info
        db = Info.get_db()
        str_id = getattr(form, "parent").raw_data[0]
        int_id = int(str_id) if str_id is not None and str_id != u"__None" and len(str_id) > 0 else None
        parent = db.session.query(Organization).get(int_id) if int_id is not None else None
        if is_created:  # New create
            # update all exiting node with right and left bigger than current parent's right - 1
            if parent is not None:
                model.parent = parent
        elif parent is not None:
            # Changing parent of a subtree or leaf.
            # Refer to http://stackoverflow.com/questions/889527/move-node-in-nested-set for detail.
            lft = model.lft
            rgt = model.rgt
            parent_rgt = parent.rgt
            ts = int(rgt - lft + 1)
            # step 1: temporary "remove" moving node, change lft and right to negative integer
            # step 2: decrease left and/or right position values of currently 'lower' items (and parents)
            # step 3: increase left and/or right position values of future 'lower' items (and parents)
            # step 4: move node (ant it's subtree) and update it's parent item id
            c = parent_rgt - ts if parent_rgt > rgt else parent_rgt
            d = parent_rgt - rgt - 1 if parent_rgt > rgt else parent_rgt - rgt - 1 + ts
            sql = ['{u} lft = 0 - lft, rgt = 0 - rgt where lft >= {lft} and rgt <={rgt}'.format(u=self.uos, lft=lft, rgt=rgt),
                   '{u} lft = lft - {ts} where lft > {rgt}'.format(u=self.uos, ts=ts, rgt=rgt),
                   '{u} rgt = rgt - {ts} where rgt > {rgt}'.format(u=self.uos, ts=ts, rgt=rgt),
                   '{u} lft = lft + {ts} where lft >= {c}'.format(ts=ts, c=c, u=self.uos),
                   '{u} rgt = rgt + {ts} where rgt >= {c}'.format(ts=ts, c=c, u=self.uos),
                   '{u} lft = 0-lft+{d}, rgt = 0-rgt + {d} where lft <= 0-{lft} and rgt >= 0-{rgt}'.format(d=d, lft=lft, rgt=rgt, u=self.uos)]
            for s in sql:
                db.engine.execute(text(s))
            db.session.commit()

    def on_model_change(self, form, model, is_created):
        """Check whether the parent organization or child organization is same as the value being edited"""
        super(OrganizationAdmin, self).on_model_change(form, model, is_created)
        if (not is_root_organization(model)) and (getattr(form, "parent") is None or getattr(form, "parent")._data is None):
            raise ValidationError(gettext('Please specify parent organization(creation of top level organization not allowed)'))
        CycleReferenceValidator.validate(form, model, object_type='Organization', parent='parent',
                                         children='all_children', is_created=is_created)

    def on_model_delete(self, model):
        """
        Validate model with child organization should not be deleted
        :param model: The model to delete
        :return: None
        """
        if len(model.all_children) > 0:
            raise ValidationError(gettext('Can not delete an organization with child organisation exists'))

    def after_model_delete(self, model):
        """
        Adjust left and right value for organizations in DB after deleting the model.
        :param model: Model to delete
        :return: None
        """
        from sqlalchemy import text
        from psi.app.service import Info
        db = Info.get_db()
        width = model.rgt - model.lft + 1
        sql = text("{u} rgt = rgt-{w} WHERE rgt > {rgt};{u} lft = lft-{w} WHERE lft > {lft}".format(rgt=model.rgt, lft=model.lft, w=width, u=self.uos))
        db.engine.execute(sql)
        db.session.commit()
