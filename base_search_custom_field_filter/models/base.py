# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from lxml import etree


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _add_custom_filters(self, res, custom_filters):
        arch = etree.fromstring(res['arch'])
        for custom_filter in custom_filters:
            node = False
            if custom_filter.position_after:
                node = arch.xpath(
                    "//field[@name='%s']" % custom_filter.position_after)
            if not node:
                node = arch.xpath("//field[last()]")
            if node:
                elem = etree.Element('field', {
                    'name': 'ir_ui_custom_filter_%s' % custom_filter.id,
                    'string': custom_filter.name,
                    'filter_domain': (
                        "[('%s', '=', self)]" % custom_filter.expression),
                })
                node[0].addnext(elem)
        res['arch'] = etree.tostring(arch)
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Inject fields field in search views."""
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'search':
            custom_filters = self.env['ir.ui.custom.field.filter'].search(
                [("model_name", "=", res.get("model"))])
            if custom_filters:
                res = self._add_custom_filters(res, custom_filters)
        return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Inject field definition. Needed to overwrite this as well due to
        subsequent call to this after `fields_view_get`.
        """
        res = super().fields_get(allfields=allfields, attributes=attributes)
        if self.env.context.get('custom_field_filter'):
            custom_filters = self.env['ir.ui.custom.field.filter'].search(
                [("model_name", "=", self._name)])
            for custom_filter in custom_filters:
                field = custom_filter._get_related_field()
                res['ir_ui_custom_filter_%s' % custom_filter.id] = (
                    field.get_description(self.env))
        return res

    @api.model
    def load_views(self, views, options=None):
        """Inject context for returning an altered fields list for UI ."""
        return super(Base, self.with_context(
            custom_field_filter=True,
        )).load_views(views, options=options)
