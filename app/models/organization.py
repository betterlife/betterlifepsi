# encoding=utf-8
from app.database import DbInfo
from app.models.data_security_mixin import DataSecurityMixin
from app.utils.db_util import id_query_to_obj
from sqlalchemy import Integer, select, desc, func, between
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased
from sqlalchemy.sql.elements import and_
from flask_login import current_user

db = DbInfo.get_db()


class Organization(db.Model, DataSecurityMixin):
    """
    Organization, for data isolation
    """
    __tablename__ = 'organization'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    lft = db.Column(Integer, unique=True, nullable=False, default=0)
    rgt = db.Column(Integer, unique=True, nullable=False, default=0)

    @hybrid_property
    def parent(self):
        if self.lft is None or self.rgt is None:
            return None
        return db.session.query(Organization).filter(and_(Organization.lft < self.lft, Organization.rgt > self.rgt)).order_by(desc(Organization.lft)).first()

    @parent.setter
    def parent(self, value):
        pass

    @parent.expression
    def parent(self):
        return (select([Organization]).where(Organization.lft < self.lft).where(Organization.rgt > self.rgt).label('parent'))

    @hybrid_property
    def all_children(self):
        """
        Get immediate children of the organization
        Reference:
        http://mikehillyer.com/articles/managing-hierarchical-data-in-mysql/
        http://www.sitepoint.com/hierarchical-data-database/
        Generated SQL Sample:
        SELECT node.name, (COUNT(parent.name) - (sub_tree.depth + 1)) AS depth
        FROM nested_category AS node,
             nested_category AS parent,
             nested_category AS sub_parent,
             (
              SELECT node.name, (COUNT(parent.name) - 1) AS depth
              FROM nested_category AS node,
              nested_category AS parent
              WHERE node.lft BETWEEN parent.lft AND parent.rgt
              AND node.name = 'PORTABLE ELECTRONICS'
              GROUP BY node.name
              ORDER BY node.lft
             )AS sub_tree
             WHERE node.lft BETWEEN parent.lft AND parent.rgt
             AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
             AND sub_parent.name = sub_tree.name
             GROUP BY node.name
             ORDER BY node.lft;
        """
        s_node = aliased(Organization, name='s_node')
        s_parent = aliased(Organization, name='s_parent')
        sub_tree = db.session.query(s_node.id, (func.count(s_parent.name) - 1).label('depth')). \
            filter(and_(between(s_node.lft, s_parent.lft, s_parent.rgt), s_node.id == self.id)) \
            .group_by(s_node.id, s_node.lft).order_by(s_node.lft).subquery()

        t_node = aliased(Organization, name='t_node')
        t_parent = aliased(Organization, name='t_parent')
        t_sub_parent = aliased(Organization, name='t_sub_parent')
        # Postgres does not support label as (func.count(t_parent.name) - (sub_tree.c.depth + 1)).label('xxx')
        # And have the field in having clause will cause issue.
        query = (db.session.query(t_node.id, t_node.name, (func.count(t_parent.name) - (sub_tree.c.depth + 1))).
                 filter(and_(between(t_node.lft, t_parent.lft, t_parent.rgt),
                             between(t_node.lft, t_sub_parent.lft, t_sub_parent.rgt),
                             t_node.id != self.id,  # Exclude current node --> itself
                             t_sub_parent.id == sub_tree.c.id))
                 .group_by(t_node.id, t_node.name, t_node.lft, 'depth')
                 .order_by(t_node.lft))
        obj_result = id_query_to_obj(Organization, query)
        return obj_result

    @all_children.setter
    def all_children(self, val):
        pass

    @all_children.expression
    def all_children(self):
        pass

    @hybrid_property
    def immediate_children(self):
        """
        Get immediate children of the organization
        Reference:
        http://mikehillyer.com/articles/managing-hierarchical-data-in-mysql/
        http://www.sitepoint.com/hierarchical-data-database/
        Generated SQL Sample:
        SELECT node.name, (COUNT(parent.name) - (sub_tree.depth + 1)) AS depth
        FROM nested_category AS node,
             nested_category AS parent,
             nested_category AS sub_parent,
             (
              SELECT node.name, (COUNT(parent.name) - 1) AS depth
              FROM nested_category AS node,
              nested_category AS parent
              WHERE node.lft BETWEEN parent.lft AND parent.rgt
              AND node.name = 'PORTABLE ELECTRONICS'
              GROUP BY node.name
              ORDER BY node.lft
             )AS sub_tree
             WHERE node.lft BETWEEN parent.lft AND parent.rgt
             AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
             AND sub_parent.name = sub_tree.name
             GROUP BY node.name
             HAVING depth <= 1
             ORDER BY node.lft;
        """
        s_node = aliased(Organization, name='s_node')
        s_parent = aliased(Organization, name='s_parent')
        sub_tree = db.session.query(s_node.id, (func.count(s_parent.name) - 1).label('depth')). \
            filter(and_(between(s_node.lft, s_parent.lft, s_parent.rgt), s_node.id == self.id)) \
            .group_by(s_node.id, s_node.lft).order_by(s_node.lft).subquery()

        t_node = aliased(Organization, name='t_node')
        t_parent = aliased(Organization, name='t_parent')
        t_sub_parent = aliased(Organization, name='t_sub_parent')
        # Postgres does not support label as (func.count(t_parent.name) - (sub_tree.c.depth + 1)).label('xxx')
        # And have the field in having clause will cause issue.
        query = (db.session.query(t_node.id, t_node.name, (func.count(t_parent.name) - (sub_tree.c.depth + 1))).
                 filter(and_(between(t_node.lft, t_parent.lft, t_parent.rgt),
                             between(t_node.lft, t_sub_parent.lft, t_sub_parent.rgt),
                             t_node.id != self.id,  # Exclude current node --> itself
                             t_sub_parent.id == sub_tree.c.id))
                 .group_by(t_node.id, t_node.name, t_node.lft, 'depth')
                 .having((func.count(t_parent.name) - (sub_tree.c.depth + 1)) <= 1)
                 .order_by(t_node.lft))
        return id_query_to_obj(Organization, query)

    @immediate_children.setter
    def immediate_children(self, val):
        pass

    @immediate_children.expression
    def immediate_children(self):
        pass

    def __unicode__(self):
        return self.name

    def can_edit(self, user=current_user):
        return self in Organization.children_self_filter(user.organization)

    def can_view_detail(self, user=current_user):
        l = Organization.children_self_filter(user.organization)
        l.append(user.organization.parent)
        return self in l

    def can_delete(self):
        if self.parent is None:
            return False
        if hasattr(self, "immediate_children"):
            return len(self.immediate_children) == 0
        if hasattr(self, "all_children"):
            return len(self.all_children) == 0
        return True

    @staticmethod
    def children_remover(organization):
        from flask_login import current_user
        all_org = Organization.query.all()
        orgs = [org for org in all_org if (org not in organization.all_children and org != organization)]
        return [org for org in orgs if (org in current_user.organization.all_children or org == current_user.organization)]

    @staticmethod
    def children_self_filter(organization):
        result = organization.all_children
        result.append(organization)
        return result

    @staticmethod
    def get_children_self_ids(organization):
        all_orgs = Organization.children_self_filter(organization)
        return [obj.id for obj in all_orgs]
