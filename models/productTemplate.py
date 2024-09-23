import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'vietnam.address.mixin']
