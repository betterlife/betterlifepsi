# coding=utf-8
from flask import url_for, request, flash
from flask.ext.admin._compat import as_unicode
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.security import current_user
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

    def can(self, operation='view'):
        tablename = self.model.__tablename__
        return current_user.is_authenticated() and (
            current_user.has_role('admin') or
            current_user.has_role(tablename + '_' + operation))

    def handle_view_exception(self, exc):
        if isinstance(exc, ValidationError):
            flash(as_unicode(exc), category='error')
            return True
        return super(ModelView, self).handle_view_exception(exc)

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated():
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
