from odoo import models, fields, api


class VietnamProvince(models.Model):
    _name = 'vietnam.province'
    _description = 'Vietnam Province'

    name = fields.Char(string="Tên tỉnh/thành phố", required=True)
    code = fields.Char(string="Mã tỉnh/thành phố", required=True)
    english_name = fields.Char(string="Tên tiếng Anh")
    level = fields.Char(string="Cấp")
    district_ids = fields.One2many(
        'vietnam.district', 'province_id', string="Quận/Huyện")


class VietnamDistrict(models.Model):
    _name = 'vietnam.district'
    _description = 'Vietnam District'

    name = fields.Char(string="Tên quận/huyện", required=True)
    code = fields.Char(string="Mã quận/huyện", required=True)
    english_name = fields.Char(string="Tên tiếng Anh")
    level = fields.Char(string="Cấp")
    province_id = fields.Many2one(
        'vietnam.province', string="Tỉnh/Thành phố", required=True)
    ward_ids = fields.One2many(
        'vietnam.ward', 'district_id', string="Phường/Xã")


class VietnamWard(models.Model):
    _name = 'vietnam.ward'
    _description = 'Vietnam Ward'

    name = fields.Char(string="Tên phường/xã", required=True)
    code = fields.Char(string="Mã phường/xã", required=True)
    english_name = fields.Char(string="Tên tiếng Anh")
    level = fields.Char(string="Cấp")
    district_id = fields.Many2one(
        'vietnam.district', string="Quận/Huyện", required=True)
