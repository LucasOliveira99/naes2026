from django import template

from ia.permissions import has_ia_admin_access


register = template.Library()
register.filter("has_ia_admin_access", has_ia_admin_access)
