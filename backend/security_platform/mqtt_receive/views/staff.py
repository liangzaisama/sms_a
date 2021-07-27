from collections import OrderedDict

from core.generics import SwiftCommonLabelResource, time_format_conversion

from security_platform.utils.commen import blank_get
from operations.models import StaffInfo


class StaffResource(SwiftCommonLabelResource):

    model_class = StaffInfo

    def get_create_or_update_label(self):
        label = OrderedDict()
        label['pass_card_number'] = self.label['passcard_id']
        label['work_number'] = self.label['person_job_number']
        label['staff_name'] = self.label['person_name']
        label['sex'] = StaffInfo.SexType.FEMALE if self.label['sex'] else StaffInfo.SexType.MALE
        label['identity_card'] = self.label['identity_card']
        label['birthday'] = time_format_conversion(self.label['birth'], format='%Y%m%d')
        label['phone_number'] = self.label['person_phone']
        label['address'] = self.label['person_address']
        label['country'] = self.label['country']
        label['nation'] = self.label['nation']
        label['jobs'] = self.label['post']
        label['entry_date'] = time_format_conversion(self.label['entry'], format='%Y%m%d')
        label['department_name'] = self.label['deparment']
        label['son_department_name'] = blank_get(self.label, 'son_deparment')
        label['picture'] = self.label['PerPicturePath']
        label['pass_area'] = self.label['pass_area']
        label['entrances_area'] = self.label['entrances_area']
        label['pass_card_type'] = self.label['passcard_type'].upper()
        label['card_create_time'] = time_format_conversion(self.label['create_time'], format='%Y%m%d')
        label['card_handle_time'] = time_format_conversion(self.label['handle_time'], format='%Y%m%d')
        label['card_expire_time'] = time_format_conversion(self.label['expire_time'], format='%Y%m%d')
        label['is_black'] = self.label['black']
        label['black_reason'] = blank_get(self.label, 'black_res')
        label['is_lock'] = self.label['lock']
        label['lock_reason'] = blank_get(self.label, 'lock_res')
        label['card_status'] = self.label['card_status']
        label['score'] = self.label['score']
        label['pass_card_max_count'] = self.label.get('passcard_max')
        label['pass_card_current_count'] = self.label.get('passcard_cur')

        return label

    def get_object_label(self):
        return {'work_number': self.label['person_job_number']}
