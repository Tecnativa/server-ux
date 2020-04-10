odoo.define('base_search_custom_field_filter.search_inputs_related_field', function (require) {
"use strict";

var core = require('web.core');
var search_inputs = require('web.search_inputs');
var ManyToOneField = core.search_widgets_registry.map.many2one;

search_inputs.Field.include({
    make_domain: function (name, operator, facetValue) {
        name = this.attrs.custom_filter_path || name;
        return this._super(name, operator, facetValue);
    },
});

ManyToOneField.include({
    make_domain: function (name, operator, facetValue) {
        name = this.attrs.custom_filter_path || name;
        return this._super(name, operator, facetValue);
    },
});

});
