# coding=utf-8
from flask_babelex import gettext

from flask import url_for, request, flash, has_request_context
from flask_admin._compat import as_unicode
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_security import current_user
from app.utils.security_util import get_user_roles, has_organization_field, is_super_admin
from sqlalchemy import func
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import ValidationError


class ModelViewWithAccess(ModelView):
    def is_accessible(self):
        return self.can()

    @property
    def can_create(self):
        return self.can(operation='create')

    @property
    def can_delete(self):
        return self.can(operation='delete')

    @property
    def can_edit(self):
        return self.can(operation='edit')

    @property
    def can_export(self):
        """
        See https://github.com/flask-admin/flask-admin/issues/1263 and https://github.com/flask-admin/flask-admin/pull/1264
        for the background
        :return:
        """
        return False

    @property
    def can_view_details(self):
        """
        See https://github.com/flask-admin/flask-admin/issues/1263 and https://github.com/flask-admin/flask-admin/pull/1264
        for the background
        :return:
        """
        return True

    def can(self, operation='view'):
        tablename = self.model.__tablename__
        obj_id = get_mdict_item_or_list(request.args, 'id') if has_request_context() else None
        obj = None if obj_id is None else self.get_one(obj_id)
        if obj is None:
            same_org = True
        else:
            same_org = (obj.organization == current_user.organization) if has_organization_field(obj) else True
        return (is_super_admin()) or (same_org and current_user.is_authenticated and (tablename + '_' + operation in get_user_roles()))

    def handle_view_exception(self, exc):
        if isinstance(exc, ValidationError):
            flash(as_unicode(exc), category='error')
            return True
        return super(ModelViewWithAccess, self).handle_view_exception(exc)

    def get_query(self):
        if has_organization_field(self.model):
            return self.session.query(self.model).filter(self.model.organization == current_user.organization)
        else:
            return super(ModelViewWithAccess, self).get_query()

    def get_count_query(self):
        if has_organization_field(self.model):
            return self.session.query(func.count('*')).filter(self.model.organization == current_user.organization)
        else:
            return super(ModelViewWithAccess, self).get_count_query()

    def on_model_change(self, form, model, is_created):
        if has_organization_field(self.model):
            if is_created:
                model.organization = current_user.organization
            elif model.organization != current_user.organization:
                ValidationError(gettext('You are not allowed to change this record'))

    def on_model_delete(self, model):
        if has_organization_field(model) and model.organization != current_user.organization:
            ValidationError(gettext('You are not allowed to delete this record'))

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class DeleteValidator(object):
    @staticmethod
    def validate_status_for_change(model, status_code, error_msg):
        if model.status.code == status_code:
            raise ValidationError(error_msg)


class CycleReferenceValidator(object):
    @staticmethod
    def validate(form, model, object_type="Object ", parent="parent", children="child", is_created=False):
        if is_created is False and \
                        form[parent] is not None and \
                        form[parent].data is not None and \
                        form[parent].data.id == model.id:
            raise ValidationError(gettext("Can not set %(ot)s's parent to itself[%(data)s]", ot=gettext(object_type), data=model))
        if is_created is False and \
                        form[parent] is not None and \
                        form[parent].data is not None and \
                        form[parent].data in getattr(model, children):
            raise ValidationError(gettext("Can not set %(ot)s's parent to it's child[%(data)s]", ot=gettext(object_type), data=form[parent].data))
        if hasattr(form, children) and \
                        form[children] is not None and \
                        form[children].data is not None and \
                        model in form[children].data:
            raise ValidationError(gettext("Can not set %(ot)s's child to itself[%(data)s]", ot=gettext(object_type), data=model))
