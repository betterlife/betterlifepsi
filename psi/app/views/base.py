# coding=utf-8
from flask_admin import expose
from flask_babelex import gettext
from flask_babelex import lazy_gettext

from flask import url_for, request, flash, has_request_context
from flask_admin._compat import as_unicode
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_security import current_user
from psi.app.utils import get_user_roles, has_organization_field, is_super_admin
from sqlalchemy import func
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import ValidationError


class ModelViewWithAccess(ModelView):
    """
    This base object controls the delete, view detail and edit permission
    on view definition level,
    If object level access control is needed, please implement DataSecurityMixin
    in the corresponding model.
    """

    column_default_sort = ('id', True)
    """
    By default records in all list view is sorted by id descending
    """


    """
    Default placeholder for the search box
    """
    search_placeholder = lazy_gettext('Search(Support first letter of Pinyin)')


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

    @property
    def role_identify(self):
        return self.model.__tablename__

    def can(self, operation='view'):
        obj_id = get_mdict_item_or_list(request.args, 'id') if has_request_context() else None
        obj = None if obj_id is None else self.get_one(obj_id)
        if obj is None:
            same_org = True
        else:
            if has_organization_field(obj):
                if obj.organization is None:
                    same_org = False
                else:
                    same_org = (obj.organization.id == current_user.organization.id)
            else:
                same_org = True
        role_assigned = same_org and current_user.is_authenticated and (self.role_identify + '_' + operation in get_user_roles())
        return (is_super_admin()) or (role_assigned)

    def handle_view_exception(self, exc):
        from sqlalchemy.exc import InvalidRequestError
        if isinstance(exc, ValidationError):
            flash(as_unicode(exc), category='error')
            return True
        elif isinstance(exc, InvalidRequestError):
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

    def get_model_return_url(self):
        from flask_admin.helpers import get_redirect_target
        return_url = get_redirect_target() or self.get_url('.index_view')
        model_id = get_mdict_item_or_list(request.args, 'id')
        model = self.get_one(model_id)
        return model, return_url

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view with model specific can_edit support
            Whether the model could be edit will be decided by model.
        """
        model, return_url = self.get_model_return_url()
        if model is not None and not model.can_edit():
            flash(gettext('You are not allowed to edit this object'))
            return redirect(return_url)
        return super(ModelViewWithAccess, self).edit_view()

    @expose('/details/')
    def details_view(self):
        """
            Details model view with model specific can_view_details support.
            Whether the model detail could be viewed will be decided by model
        """
        model, return_url = self.get_model_return_url()
        if model is not None and not model.can_view_details():
            flash(gettext('You are not allowed to view detail of this object'))
            return redirect(return_url)
        return super(ModelViewWithAccess, self).details_view()

    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
            Whether the model could be deleted is decided by model
        """
        from flask_admin.helpers import get_redirect_target
        return_url = get_redirect_target() or self.get_url('.index_view')
        form = self.delete_form()
        if self.validate_form(form):
             # id is InputRequired()
            model_id = form.id.data
            model = self.get_one(model_id)
            if model is not None and not model.can_delete():
                flash(gettext('You are not allowed to delete this object'))
                return redirect(return_url)
        return super(ModelViewWithAccess, self).delete_view()


class DeleteValidator(object):
    @staticmethod
    def validate_status_for_change(model, status_code, error_msg):
        if model.status.code == status_code:
            raise ValidationError(error_msg)

class ModelWithLineFormatter(object):
    line_fields = []

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
            try:
                raise ValidationError(gettext("Can not set %(ot)s's child to itself[%(data)s]", ot=gettext(object_type), data=model))
            except BaseException:
                raise ValidationError(gettext("Can not set %(ot)s's child to itself", ot=gettext(object_type)))
