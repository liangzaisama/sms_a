"""安保事件模块单元测试"""
from collections import OrderedDict
from datetime import datetime

from rest_framework.test import APIRequestFactory, APITestCase, APIClient

from devices.models import DeviceInfo, CameraDevice
from .models import DeviceAlarmEvent, PersonAlarmEvent, AlarmEvent, EventWorkSheet
from users.models import User


class AlarmEventViewSetTestClass(APITestCase):
    """安保事件视图集接口测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/alarm/events'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_event_count = 5
        self.person_event_count = 3
        self.device_events = []
        self.person_events = []
        self.devices = []
        self.create_person_event()
        self.create_camera_devices()
        self.create_device_event()

    def create_camera_devices(self):
        """创建摄像机设备"""
        count = self.device_event_count
        for i in range(count):
            index = i + 1
            device = CameraDevice.objects.create(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )
            self.devices.append(device)

    def create_person_event(self):
        """创建人工报警事件"""
        count = self.person_event_count
        for i in range(count):
            index = i + 6
            person_event = PersonAlarmEvent(
                id=index,
                event_type=AlarmEvent.EventType.ARTIFICIAL.value,
                event_state=PersonAlarmEvent.EventState.UNAUDITED.value,
                event_code=f'device_code:{index}',
                event_name=f'device_name:{index}',
                alarm_person_name=f'alarm_person_name:{index}',
                alarm_person_type=PersonAlarmEvent.AlarmPersonType.PASSENGERS.value,
                alarm_time=datetime.now(),
                handled_time=datetime.now(),

            )
            person_event.save()
            self.person_events.append(person_event)

    def create_device_event(self):
        """创建系统报警事件"""
        count = self.device_event_count
        for i in range(count):
            index = i + 1
            device_event = DeviceAlarmEvent.objects.create(
                id=index,
                event_type=AlarmEvent.EventType.DEVICE.value,
                device=self.devices[i],
                event_state=DeviceAlarmEvent.EventState.UNDISPOSED.value,
                alarm_type=f'排队报警',
                event_code=f'device_code:{index}',
                event_name=f'device_name:{index}',
                alarm_time=datetime.now(),
                belong_system=DeviceInfo.BelongSystem.ANALYSIS.label,
                subsystem_event_id=f'subsystem_event_id:{index}',

            )
            self.device_events.append(device_event)

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success_basic(self):
        """测试成功获取基础报警事件列表"""
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 8)

    def test_get_success_devices(self):
        """测试成功获取自动报警事件列表"""
        data = OrderedDict()
        data['event_type'] = AlarmEvent.EventType.DEVICE
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 5)
        self.assertEqual(response.data['data']['objects'][0]['event_type'], 1)

    def test_get_success_persons(self):
        """测试成功获取人工报警事件列表"""
        data = OrderedDict()
        data['event_type'] = AlarmEvent.EventType.ARTIFICIAL
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 3)
        self.assertEqual(response.data['data']['objects'][0]['event_type'], 2)

    def test_get_success_filter(self):
        """测试成功获取过滤条件报警事件列表"""
        data = OrderedDict()
        data['event_name'] = 1
        data['event_code'] = 1
        data['start_time'] = datetime.now()
        data['end_time'] = datetime.now()

        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_get_error_filter(self):
        """测试失败获取过滤条件报警事件列表"""
        data = OrderedDict()
        data['event_name'] = 1
        data['event_code'] = 1
        data['start_time'] = datetime.now()
        data['end_time'] = 123

        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '结束时间格式错误')

    def test_get_success_device(self):
        """测试成功获取自动报警事件详情"""
        self.contact_url = self.contact_url + '/1'
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['data'])
        self.assertEqual(response.data['data']['subsystem_event_id'], 'subsystem_event_id:1')

    def test_get_success_person(self):
        """测试成功获取人工报警事件详情"""
        self.contact_url = self.contact_url + '/6'
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['data'])
        self.assertEqual(response.data['data']['alarm_person_name'], 'alarm_person_name:6')

    def test_get_error_detail(self):
        """测试失败获取报警事件详情"""
        self.contact_url = self.contact_url + '/100'
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '基础报警事件不存在')

    def test_get_success_export(self):
        """测试成功导出基础报警事件列表"""
        self.contact_url = self.contact_url + '/exports'
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)

    def test_get_success_export_template(self):
        """测试成功导出基础报警事件列表模板"""
        data = OrderedDict()
        data['event_name'] = 1
        data['event_code'] = 1
        data['start_time'] = datetime.now()
        data['end_time'] = datetime.now()
        self.contact_url = self.contact_url + '/exports'
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_get_success_statistics(self):
        """测试成功获取报警事件统计信息"""
        self.contact_url = self.contact_url + '/statistics'
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)

    def test_get_success_days(self):
        """测试成功获取报警事件日期统计信息"""
        data = OrderedDict()
        data['start_date'] = datetime.today().date()
        data['end_date'] = datetime.today().date()
        self.contact_url = self.contact_url + '/days'

        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'][0]['count'], 8)

    def test_get_success_months(self):
        """测试成功获取报警事件月份统计信息"""
        data = OrderedDict()
        data['start_month'] = str(datetime.today().date())[0:7]
        data['end_month'] = str(datetime.today().date())[0:7]
        self.contact_url = self.contact_url + '/months'

        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'][0]['count'], 8)

    def test_get_success_hours(self):
        """测试成功获取报警事件小时统计信息"""
        self.contact_url = self.contact_url + '/hours'

        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_events_count']['total_count'], 8)

    def test_patch_success_device_dispose(self):
        """测试成功处置自动报警事件详情"""
        self.contact_url = self.contact_url + '/1/dispose'
        data = OrderedDict()
        data['dispose_opinion'] = '123'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['data'])
        self.assertEqual(response.data['data']['dispose_opinion'], '123')

    def test_patch_success_person_audit(self):
        """测试成功审核人工报警事件"""
        EventWorkSheet.objects.create(
            id=self.person_events[0].id,
            work_sheet_code='123',
            alarm_event=self.person_events[0],
            dispose_user=self.user
        )
        self.contact_url = self.contact_url + '/6/person'
        data = OrderedDict()
        data['audit_opinion'] = '123'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['data'])
        self.assertEqual(response.data['data']['audit_opinion'], '123')

    def test_patch_success_device_audit(self):
        """测试成功审核系统报警事件"""
        EventWorkSheet.objects.create(
            id=self.device_events[0].id,
            work_sheet_code='123',
            alarm_event=self.device_events[0],
            dispose_user=self.user
        )
        self.contact_url = self.contact_url + '/1/device'
        event = self.device_events[0]
        event.event_state = 'relieved'
        event.save()
        data = OrderedDict()
        data['audit_opinion'] = '123'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['data'])
        self.assertEqual(response.data['data']['audit_opinion'], '123')

    def test_create_success_person(self):
        """测试成功创建人工上报事件"""
        self.contact_url = self.contact_url + '/persons'
        data = OrderedDict()
        data['event_name'] = '123'
        data['alarm_person_name'] = '123'
        data['alarm_person_type'] = 1
        data['handled_opinion'] = '123'
        data['gis_basic_info'] = '123'
        data['gis_field'] = '123'
        data['alarm_time'] = datetime.now()
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['data'])
        self.assertEqual(response.data['data']['gis_field'], '123')

    def test_create_error_person(self):
        """测试失败创建人工上报事件"""
        self.contact_url = self.contact_url + '/persons'
        data = OrderedDict()
        data['event_name'] = '123'
        data['alarm_person_name'] = '123'
        data['alarm_person_type'] = 1
        # data['handled_opinion'] = '123'
        data['gis_basic_info'] = '123'
        data['gis_field'] = '123'
        data['alarm_time'] = datetime.now()
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], 'handled_opinion不能为null')
