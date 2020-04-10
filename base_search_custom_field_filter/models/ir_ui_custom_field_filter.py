# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models
from odoo.tools import ormcache


class IrUiCustomFilter(models.Model):
    _name = "ir.ui.custom.field.filter"
    _description = "Custom UI field filter"
    _order = "model_id, sequence, id"

    sequence = fields.Integer()
    model_id = fields.Many2one(comodel_name="ir.model", required=True)
    model_name = fields.Char(
        related="model_id.model", store=True, readonly=True, index=True,
        string="Model name",
    )
    name = fields.Char(required=True, translate=True)
    expression = fields.Char(required=True)
    position_after = fields.Char(
        help="Optional field name for putting the filter after that one. "
             "If empty or not found, it will be put at the end.",
    )

    def _get_related_field(self):
        """Determine the chain of fields."""
        self.ensure_one()
        related = self.expression.split('.')
        target = self.env[self.model_name]
        for name in related:
            field = target._fields[name]
            target = target[name]
        return field

    @api.model
    @ormcache('model_name')
    def _get_custom_filters(self, model_name):
        filters_info = []
        for custom_filter in self.search([("model_name", "=", model_name)]):
            filters_info.append({
                'id': custom_filter.id,
                'name': custom_filter.name,
                'expression': custom_filter.expression,
                'position_after': custom_filter.position_after,
                'related_field': custom_filter._get_related_field(),
            })
        return filters_info

    @api.constrains('model_id', 'expression')
    def _check_expression(self):
        for record in self:
            try:
                record._get_related_field()
            except KeyError:
                raise exceptions.ValidationError(_("Incorrect expression."))

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._get_custom_filters.clear_cache(self)
        return res

    def write(self, vals):
        res = super().write(vals)
        self._get_custom_filters.clear_cache(self)
        return res
