from odoo import models, fields, api
import xlrd
import base64
import logging
_logger = logging.getLogger(__name__)


class ImportVietnamAddress(models.TransientModel):
    _name = 'import.vietnam.address'
    _description = 'Import Vietnam Address from Excel'

    file = fields.Binary(string='File Excel', required=True)
    filename = fields.Char(string='Tên file')

    @api.model
    def create(self, vals):
        new_record = super(ImportVietnamAddress, self).create(vals)
        return new_record

    def import_address(self):

        if not self.file:
            return {'type': 'ir.actions.act_window_close'}

        try:
            # Xóa dữ liệu cũ
            self.env['vietnam.ward'].search([]).unlink()
            self.env['vietnam.district'].search([]).unlink()
            self.env['vietnam.province'].search([]).unlink()
            # Đọc file Excel
            book = xlrd.open_workbook(
                file_contents=base64.b64decode(self.file))
            sheet = book.sheet_by_index(0)

            for row in range(1, sheet.nrows):  # Bỏ qua hàng tiêu đề
                try:
                    province_name = sheet.cell(row, 0).value
                    province_code = sheet.cell(row, 1).value
                    district_name = sheet.cell(row, 2).value
                    district_code = sheet.cell(row, 3).value
                    ward_name = sheet.cell(row, 4).value
                    ward_code = sheet.cell(row, 5).value
                    level = sheet.cell(row, 6).value
                    english_name = sheet.cell(row, 7).value

                    # Xử lý tỉnh/thành phố
                    province = self.env['vietnam.province'].search(
                        [('code', '=', province_code)], limit=1)
                    if not province:
                        province = self.env['vietnam.province'].create({
                            'name': province_name,
                            'code': province_code,
                            'english_name': english_name if level == 'Tỉnh/Thành phố' else False,
                            'level': level if level == 'Tỉnh/Thành phố' else False
                        })

                    # Xử lý quận/huyện
                    district = self.env['vietnam.district'].search(
                        [('code', '=', district_code)], limit=1)
                    if not district:
                        district = self.env['vietnam.district'].create({
                            'name': district_name,
                            'code': district_code,
                            'province_id': province.id,
                            'english_name': english_name,
                            'level': level
                        })

                    # Xử lý phường/xã
                    if level in ['Phường', 'Xã', 'Thị trấn']:
                        district = self.env['vietnam.district'].search(
                            [('code', '=', district_code)], limit=1)
                        if district:
                            ward = self.env['vietnam.ward'].search(
                                [('code', '=', ward_code)], limit=1)
                            if not ward:
                                self.env['vietnam.ward'].create({
                                    'name': ward_name,
                                    'code': ward_code,
                                    'district_id': district.id,
                                    'english_name': english_name,
                                    'level': level
                                })
                        else:
                            _logger.warning(
                                f"Không tìm thấy quận/huyện với mã {district_code} cho phường/xã {ward_name}")

                except Exception as e:
                    _logger.error(
                        f"Lỗi khi xử lý dòng {row + 1}: {str(e)}")
            self.env.cr.commit()
            self.env['vietnam.address.overview'].refresh_data()
            self.search([]).unlink()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành công',
                    'message': 'Dữ liệu đã được nhập thành công',
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window_close'
                    }
                }
            }

        except Exception as e:
            _logger.error(f"Lỗi khi nhập dữ liệu: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Lỗi',
                    'message': 'Có lỗi xảy ra khi nhập dữ liệu. Vui lòng kiểm tra lại file và thử lại.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
