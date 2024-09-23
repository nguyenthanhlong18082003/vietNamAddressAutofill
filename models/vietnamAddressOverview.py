from odoo import models, fields, api


class VietnamAddressOverview(models.Model):
    _name = 'vietnam.address.overview'
    _description = 'Vietnam Address Overview'
    
    province_name = fields.Char(string="Tỉnh/Thành phố")
    province_code = fields.Char(string="Mã TP")
    district_name = fields.Char(string="Quận/Huyện")
    district_code = fields.Char(string="Mã QH")
    ward_name = fields.Char(string="Phường/Xã")
    ward_code = fields.Char(string="Mã PX")
    level = fields.Char(string="Cấp")
    english_name = fields.Char(string="Tên Tiếng Anh")

    @api.model
    def refresh_data(self):
        self.search([]).unlink()  # Xóa dữ liệu cũ
        provinces = self.env['vietnam.province'].search([])
        for province in provinces:
            for district in province.district_ids:
                for ward in district.ward_ids:
                    self.create({
                        'province_name': province.name,
                        'province_code': province.code,
                        'district_name': district.name,
                        'district_code': district.code,
                        'ward_name': ward.name,
                        'ward_code': ward.code,
                        'level': ward.level,
                        'english_name': ward.english_name,
                    })
        return True
    