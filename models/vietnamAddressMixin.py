from unidecode import unidecode
import re
from odoo import models, fields, api
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class VietnamAddressMixin(models.AbstractModel):
    _name = 'vietnam.address.mixin'
    _description = 'Vietnam Address Mixin'
    checkStreet = fields.Boolean(string='Check Street', default=False)
    province_id = fields.Many2one(
        'vietnam.province', string="Tỉnh/Thành phố", required=True)
    district_id = fields.Many2one(
        'vietnam.district', string="Quận/Huyện", domain="[('province_id', '=', province_id)]", required=True)
    ward_id = fields.Many2one(
        'vietnam.ward', string="Phường/Xã", domain="[('district_id', '=', district_id)]", required=True)
    street = fields.Char(string="Đường/Hẻm/Số nhà", required=True)

    @api.onchange('street')
    def _onchange_full_address(self):
        self.checkStreet = False
        if self.street:
            self.checkStreet = True
            full_address = self._normalize_location_name(self.street)

            # Định nghĩa các từ khóa cho mỗi cấp hành chính
            ward_keywords = r'\b(phường|xã|thị trấn)\b'
            district_keywords = r'\b(quận|huyện|thị xã|thành phố)\b'
            province_keywords = r'\b(tỉnh|thành phố)\b'

            # Tìm vị trí của từng cấp hành chính
            matches = list(re.finditer(
                f"{province_keywords}|{district_keywords}|{ward_keywords}", full_address, re.IGNORECASE))

            province_name = ''
            district_name = ''
            ward_name = ''
            street_address = full_address

            if matches:
                matches.reverse()  # Xử lý từ phải sang trái
                last_end = len(full_address)
                for match in matches:
                    keyword = match.group().lower()
                    start_index = match.start()

                    if 'tỉnh' in keyword or ('thành phố' in keyword and not province_name):
                        province_name = full_address[start_index:last_end].strip(
                        )
                        last_end = start_index
                    elif 'quận' in keyword or 'huyện' in keyword or 'thị xã' in keyword or ('thành phố' in keyword and not district_name):
                        district_name = full_address[start_index:last_end].strip(
                        )
                        last_end = start_index
                    elif 'phường' in keyword or 'xã' in keyword or 'thị trấn' in keyword:
                        ward_name = full_address[start_index:last_end].strip()
                        last_end = start_index

                street_address = full_address[:last_end].strip()

            # Viết hoa chữ cái đầu của mỗi từ trong street_address
            street_address = self._capitalize_address(street_address)
            # Cập nhật các trường
            self.street = street_address

            # Normalize input
            province_name = self._normalize_location_name(province_name)
            district_name = self._normalize_location_name(district_name)
            ward_name = self._normalize_location_name(ward_name)

            # Tìm kiếm và cập nhật tỉnh/thành phố, quận/huyện, phường/xã
            self._update_location(
                'province_id', 'vietnam.province', province_name)
            self._update_location('district_id', 'vietnam.district', district_name,
                                  province_id=self.province_id.id if self.province_id else False)
            self._update_location('ward_id', 'vietnam.ward', ward_name,
                                  district_id=self.district_id.id if self.district_id else False)

    def _capitalize_address(self, address):
        # Danh sách các từ không cần viết hoa
        lower_words = ['và', 'hoặc', 'của',
                       'trong', 'ngoài', 'trên', 'dưới', 'với']

        # Tách địa chỉ thành các từ
        words = address.split()

        # Viết hoa chữ cái đầu của mỗi từ, trừ các từ trong danh sách lower_words
        capitalized_words = [word.capitalize() if word.lower(
        ) not in lower_words else word.lower() for word in words]

        # Ghép các từ lại thành chuỗi
        return ' '.join(capitalized_words)

    def _update_location(self, field_name, model, name, **kwargs):
        if name:
            location = self._find_location(model, name, **kwargs)
            if location:
                setattr(self, field_name, location)
            else:
                setattr(self, field_name, False)
        else:
            setattr(self, field_name, False)

    def _normalize_location_name(self, name):
        # Loại bỏ khoảng trắng thừa và chuyển về chữ thường
        # Loại bỏ dấu chấm
        name = name.replace('.', ' ')
        name = name.replace(',', ' ')
        name = ' '.join(name.lower().split())
        # Thay thế các từ viết tắt phổ biến
        replacements = {
            'tp': 'thành phố',
            'thphố': 'thành phố',
            'q': 'quận',
            'h': 'huyện',
            'p': 'phường',
            'x': 'xã',
            'tt': 'thị trấn',
            't': 'tỉnh',
            'tx': 'thị xã',
            'thx': 'thị xã',
            'thxã': 'thị xã',
            'thxa': 'thị xã',
            'hcm': 'Hồ Chí Minh',
            'tphcm': 'Thành Phố Hồ Chí Minh',
            'tphn': 'Thành Phố Hà Nội',
            'hn': 'Thành Phố Hà Nội',
        }
        for abbr, full in replacements.items():
            name = re.sub(r'\b' + re.escape(abbr) + r'\b', full, name)

        # Xử lý các trường hợp đặc biệt như "Q4", "P10", "Q1", v.v.
        name = re.sub(
            r'\b([qph])(\d+)\b', lambda m: f"{replacements[m.group(1)]} {m.group(2)}", name)

        # Xử lý các trường hợp đặc biệt như "Q 4", "P 10", v.v.
        name = re.sub(r'\b(quận|phường|xã)\s*(\d+)\b', r'\1 \2', name)

       # Chuẩn hóa số, ví dụ "4" thành "04" nếu cần
        def normalize_number(match):
            num = match.group(2)
            return f"{match.group(1)} {int(num):02d}"

        name = re.sub(r'\b(quận|phường|xã)\s+(\d+)\b', normalize_number, name)

        return name

    def _find_location(self, model, name, **kwargs):
        domain = [('name', 'ilike', name)]
        domain.extend((k, '=', v) for k, v in kwargs.items())

        location = self.env[model].sudo().search(domain, limit=1)
        _logger.info(name)
        if not location:
            # Thử tìm kiếm với các biến thể khác
            variations = self._generate_name_variations(name)
            for variation in variations:
                domain[0] = ('name', 'ilike', variation)
                location = self.env[model].sudo().search(domain, limit=1)
                if location:
                    break

            # If still not found, try with specific Vietnamese character replacements
            if not location:
                specific_replacements = {
                    'òa': 'oà', 'oà': 'òa',
                    'óa': 'oá', 'oá': 'óa',
                    'òe': 'oè', 'oè': 'òe',
                    'óe': 'oé', 'oé': 'óe',
                    'ùy': 'uỳ', 'uỳ': 'ùy',
                    'úy': 'uý', 'uý': 'úy'
                }
                words = name.split()
                for i, word in enumerate(words):
                    for old, new in specific_replacements.items():
                        if old in word:
                            words[i] = word.replace(old, new)
                            break
                _logger.info(words)
                if words != name.split():
                    specific_variation = ' '.join(words)
                    domain[0] = ('name', 'ilike', specific_variation)
                    location = self.env[model].sudo().search(domain, limit=1)

            # If still not found, try replacing 'y' with 'i' and vice versa
            if not location:
                y_variations = ['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ']
                i_variations = ['i', 'ì', 'í', 'ỉ', 'ĩ', 'ị']
                def replace_all_variations(text, from_chars, to_chars):
                    for f, t in zip(from_chars, to_chars):
                        text = text.replace(f, t)
                    return text
                y_i_variations = [
                    replace_all_variations(name, y_variations, i_variations),
                    replace_all_variations(name, i_variations, y_variations),
                ]
                for y_i_variation in y_i_variations:
                    _logger.info(y_i_variation)
                    if y_i_variation != name:
                        domain[0] = ('name', 'ilike', y_i_variation)
                        location = self.env[model].sudo().search(
                            domain, limit=1)
                        if location:
                            _logger.info(
                                f"Found location using y/i variation: {y_i_variation}")
                            break

        return location

    def _generate_name_variations(self, name):
        variations = [name]
        # Thêm biến thể không có số 0 đứng trước
        variations.append(re.sub(r'\b0(\d)\b', r'\1', name))
        # Thêm biến thể có số 0 đứng trước cho số một chữ số
        variations.append(re.sub(r'\b(\d)\b', r'0\1', name))
        # Thêm biến thể không dấu (chỉ sử dụng khi cần thiết)
        variations.append(unidecode(name))
        return variations

    @api.onchange('province_id')
    def _onchange_province_id(self):
        if not self.province_id:
            self.district_id = False
        else:
            if not self.checkStreet:
                self.district_id = False
                self.ward_id = False
                self.street = False

    @api.onchange('district_id')
    def _onchange_district_id(self):
        if not self.district_id:
            self.ward_id = False
        else:
            if not self.checkStreet:
                self.ward_id = False
                self.street = False

    @api.onchange('ward_id')
    def _onchange_ward_id(self):
        if not self.checkStreet:
            self.street = False
