# coding=utf-8
from gettext import gettext

from flask import url_for, request, flash
from flask.ext.admin._compat import as_unicode
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.security import current_user
from app.utils.security_util import get_user_roles, is_super_admin, has_organization_field
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
        return False

    @property
    def can_view_details(self):
        return True

    def can(self, operation='view'):
        tablename = self.model.__tablename__
        return current_user.is_authenticated and (tablename + '_' + operation in get_user_roles())

    def handle_view_exception(self, exc):
        if isinstance(exc, ValidationError):
            flash(as_unicode(exc), category='error')
            return True
        return super(ModelView, self).handle_view_exception(exc)

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
    def validate(form, model, object_type="Object ", parent="parent", children="child"):
        if form[parent] is not None and \
                        form[parent].data is not None and \
                        form[parent].data.id == model.id:
            raise ValidationError("%s can not be itself's parent" % object_type)
        if form[children] is not None and \
                        form[children].data is not None and \
                        model in form[children].data:
            raise ValidationError('%s can not be itself\'s child' % object_type)
