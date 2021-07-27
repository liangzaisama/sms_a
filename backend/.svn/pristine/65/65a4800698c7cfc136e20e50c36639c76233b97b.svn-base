"""设备资源管理模块单元测试"""
from collections import OrderedDict

from rest_framework.test import APIRequestFactory, APITestCase, APIClient

from .models import DeviceInfo, DeviceGroup, DeviceLabel, CameraDevice
from users.models import User, Department


class DeviceCountViewTestClass(APITestCase):
    """设备类型状态统计测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)
        self.contact_url = '/api/devices/statistics'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_count = 5
        self.devices = DeviceInfo.objects.bulk_create(list(self.create_devices()))

    def create_devices(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceInfo(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功获取设备类型状态统计"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'][0]['device_type'], 'cctv')
        self.assertEqual(response.data['data'][0]['count'], 5)

    def test_user_device_empty(self):
        """测试用户无设备权限"""
        self.user.is_superuser = False
        self.user.save()
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'][0]['device_type'], 'cctv')
        self.assertEqual(response.data['data'][0]['count'], 0)

    def test_user_device_single(self):
        """测试用户只有一个设备的权限"""
        self.user.is_superuser = False
        self.user.device_set.add(self.devices[0])
        self.user.save()
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'][0]['device_type'], 'cctv')
        self.assertEqual(response.data['data'][0]['count'], 1)


class DeviceTypePercentageCountViewTestClass(APITestCase):
    """设备类型百分比统计测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/devices/type/statistics'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_count = 5
        self.devices = DeviceInfo.objects.bulk_create(list(self.create_devices()))

    def create_devices(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceInfo(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功获取设备类型状态统计"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['category'][0]['device_type'], 'cctv')
        self.assertEqual(response.data['data']['category'][0]['count'], 5)
        self.assertEqual(response.data['data']['total']['total_count'], 5)

    def test_user_device_empty(self):
        """测试用户无设备权限"""
        self.user.is_superuser = False
        self.user.save()
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['category'][0]['device_type'], 'cctv')
        self.assertEqual(response.data['data']['category'][0]['count'], 5)
        self.assertEqual(response.data['data']['total']['total_count'], 5)

    def test_user_device_single(self):
        """测试用户只有一个设备的权限"""
        self.user.is_superuser = False
        self.user.device_set.add(self.devices[0])
        self.user.save()
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['category'][0]['device_type'], 'cctv')
        self.assertEqual(response.data['data']['category'][0]['count'], 5)
        self.assertEqual(response.data['data']['total']['total_count'], 5)


class DeviceInfoViewTestClass(APITestCase):
    """设备列表接口测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/devices'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_count = 5
        self.devices = DeviceInfo.objects.bulk_create(list(self.create_devices()))

    def create_devices(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceInfo(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success_status(self):
        """测试成功获取设备状态场景列表"""
        data = OrderedDict()
        data['scene'] = 'status'
        device = self.devices[0]
        device.device_state = DeviceInfo.DeviceState.TROUBLE_OPEN.value
        device.save()

        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 5)
        self.assertEqual(response.data['data']['objects'][0]['device_state'], 'normal')

    def test_get_success_info(self):
        """测试成功获取设备完整信息场景列表"""
        data = OrderedDict()
        data['scene'] = 'info'
        data['device_name'] = '1'

        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 1)
        self.assertEqual(response.data['data']['objects'][0]['ipv4'], '')

    def test_get_error_scene(self):
        """测试缺少场景值"""
        data = OrderedDict()
        data['device_name'] = '1'

        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '缺少参数scene')


class DeviceBasicsViewSetTestClass(APITestCase):
    """设备基础信息接口测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/devices'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_count = 5
        self.camera_device_count = 3
        self.devices = DeviceInfo.objects.bulk_create(list(self.create_devices()))
        self.create_camera_devices()
        self.user.department = self.create_department()
        self.user.save()

    def create_devices(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceInfo(
                id=index,
                device_type=DeviceInfo.DeviceType.MAINTENANCE.value,
                belong_system=DeviceInfo.BelongSystem.MAINTENANCE.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def create_camera_devices(self):
        count = self.camera_device_count
        for i in range(count):
            index = i + 6
            CameraDevice.objects.create(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def create_department(self):
        department = Department.objects.create(
            id=self.device_count,
            department_name=self.device_count

        )
        return department

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success_normal(self):
        """测试成功获取设备详情"""
        self.contact_url = self.contact_url + '/1'

        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['device_type'], 'enclosure')

    def test_get_success_camera(self):
        """测试成功获取摄像机设备详情"""
        self.contact_url = self.contact_url + '/6'

        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['device_type'], 'cctv')
        self.assertEqual(response.data['data']['camera_type'], '枪机')

    def test_get_error_permission(self):
        """测试无设备权限"""
        self.user.is_superuser = False
        self.user.save()
        self.contact_url = self.contact_url + '/1'

        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '设备不存在')

    def test_get_device_users(self):
        """测试获取同部门拥有设备权限的普通用户信息"""
        self.user.is_superuser = False
        department = self.user.department
        self.user.device_set.add(*self.devices)
        department.device_set.add(*self.devices)
        department.save()
        self.user.save()
        self.contact_url = self.contact_url + '/1/owners'

        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'][0]['username'], self.user.username)

    def test_success_update_details(self):
        """测试成功修改设备手动维护字段"""
        data = OrderedDict()
        data['group_ids'] = []
        data['label_ids'] = []
        data['gis_basic_info'] = '123'
        data['gis_field'] = '123'
        data['device_cad_code'] = '123'
        self.contact_url = self.contact_url + '/1/details'

        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['device_cad_code'], '123')

    def test_success_update_camera_details(self):
        """测试成功修改摄像机设备设备手动维护字段"""
        data = OrderedDict()
        data['group_ids'] = []
        data['label_ids'] = []
        data['gis_basic_info'] = '123'
        data['gis_field'] = '123'
        data['device_cad_code'] = '123'
        data['camera_type'] = '全景相机'
        self.contact_url = self.contact_url + '/6/details'

        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['device_cad_code'], '123')
        self.assertEqual(response.data['data']['camera_type'], '全景相机')

    def test_error_update_details(self):
        """测试失败修改设备手动维护字段，设备组参数错误"""
        data = OrderedDict()
        data['group_ids'] = [1, 2, 3]
        data['label_ids'] = []
        data['gis_basic_info'] = '123'
        data['gis_field'] = '123'
        data['device_cad_code'] = '123'
        self.contact_url = self.contact_url + '/1/details'

        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '参数group_ids错误')

    def test_error_update_camera_details(self):
        """测试失败修改摄像机设备手动维护字段，摄像机类型参数错误"""
        data = OrderedDict()
        data['group_ids'] = []
        data['label_ids'] = []
        data['gis_basic_info'] = '123'
        data['gis_field'] = '123'
        data['device_cad_code'] = '123'
        data['camera_type'] = '全景相机123'
        self.contact_url = self.contact_url + '/6/details'

        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], 'camera_type格式错误')

    def test_error_update_gis(self):
        """测试成功修改gis字段"""
        data = OrderedDict()
        data['gis_basic_info'] = '1234'
        data['gis_field'] = '123'
        self.contact_url = self.contact_url + '/1/gis'

        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['gis_basic_info'], '1234')

    def test_error_create(self):
        """测试失败创建设备"""
        data = OrderedDict()
        data['gis_basic_info'] = '1234'
        data['gis_field'] = '123'
        self.contact_url = self.contact_url

        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data['error_message'], '方法 “POST” 不被允许。')

    def test_error_update(self):
        """测试失败修改设备"""
        data = OrderedDict()
        data['gis_basic_info'] = '1234'
        data['gis_field'] = '123'
        self.contact_url = self.contact_url + '/1'

        response = self.client.put(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data['error_message'], '方法 “PUT” 不被允许。')

    def test_error_delete(self):
        """测试失败删除设备"""
        data = OrderedDict()
        data['gis_basic_info'] = '1234'
        data['gis_field'] = '123'
        self.contact_url = self.contact_url + '/1'

        response = self.client.delete(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data['error_message'], '方法 “DELETE” 不被允许。')


class DeviceGroupsViewSetTestClass(APITestCase):
    """设备组信息接口测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/groups'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_count = 5
        self.camera_device_count = 3
        self.devices = DeviceInfo.objects.bulk_create(list(self.create_devices()))
        self.groups = DeviceGroup.objects.bulk_create(list(self.create_device_groups()))
        self.create_camera_devices()
        self.user.department = self.create_department()
        self.user.save()

    def create_devices(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceInfo(
                id=index,
                device_type=DeviceInfo.DeviceType.MAINTENANCE.value,
                belong_system=DeviceInfo.BelongSystem.MAINTENANCE.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def create_device_groups(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceGroup(
                id=index,
                name=f'name:{index}',
                user=self.user
            )

    def create_camera_devices(self):
        count = self.camera_device_count
        for i in range(count):
            index = i + 6
            CameraDevice.objects.create(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def create_department(self):
        department = Department.objects.create(
            id=self.device_count,
            department_name=self.device_count

        )
        return department

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success_list(self):
        """测试成功获取设备组列表"""

        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 5)

    def test_get_success_retrieve(self):
        """测试成功获取设备组详情"""
        self.contact_url = self.contact_url + '/1'
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['device_group_name'], 'name:1')

    def test_success_create(self):
        """测试成功创建设备组"""
        data = OrderedDict()
        data['devices'] = [1, 2, 3]
        data['device_group_name'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['device_group_name'], '123')

    def test_error_create_lack_name(self):
        """测试失败创建设备组，缺少名称"""
        data = OrderedDict()
        data['devices'] = [1, 2, 3]
        # data['device_group_name'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '缺少参数分组名称')

    def test_error_create_lack_device(self):
        """测试失败创建设备组，缺少设备id列表"""
        data = OrderedDict()
        # data['devices'] = [1, 2, 3]
        data['device_group_name'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '缺少参数设备组设备')

    def test_error_create_devices(self):
        """测试失败创建设备组，设备id列表错误"""
        data = OrderedDict()
        data['devices'] = [1, 2, 9]
        data['device_group_name'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '参数devices错误')

    def test_success_detachments(self):
        """测试成功设备组移除设备"""
        group = self.groups[0]
        group.devices.add(*self.devices)
        group.save()
        data = OrderedDict()
        data['devices'] = [1, 2, 3]
        self.contact_url = self.contact_url + '/1/detachments'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(group.devices.all()), 2)

    def test_error_detachments_device_error(self):
        """测试失败设备组移除设备,deviceID错误"""
        group = self.groups[0]
        group.devices.add(*self.devices)
        group.save()
        data = OrderedDict()
        data['devices'] = [1, 2, 8]
        self.contact_url = self.contact_url + '/1/detachments'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], 'device_name:8不属于选择设备分组，请重新选择')

    def test_error_detachments_lack_devices(self):
        """测试失败设备组移除设备,缺少设备ID列表"""
        group = self.groups[0]
        group.devices.add(*self.devices)
        group.save()
        data = OrderedDict()
        data['devices'] = []
        self.contact_url = self.contact_url + '/1/detachments'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '参数devices不能为空')


class DeviceLabelsViewSetTestClass(APITestCase):
    """设备标签信息接口测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/labels'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_count = 5
        self.camera_device_count = 3
        self.devices = DeviceInfo.objects.bulk_create(list(self.create_devices()))
        self.labels = DeviceLabel.objects.bulk_create(list(self.create_device_labels()))
        self.create_camera_devices()
        self.user.department = self.create_department()
        self.user.save()

    def create_devices(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceInfo(
                id=index,
                device_type=DeviceInfo.DeviceType.MAINTENANCE.value,
                belong_system=DeviceInfo.BelongSystem.MAINTENANCE.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def create_device_labels(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceLabel(
                id=index,
                name=f'name:{index}',
                keywords=f'keywords:{index}',
                content=f'content:{index}',
                color=f'color:{index}',
                user=self.user
            )

    def create_camera_devices(self):
        count = self.camera_device_count
        for i in range(count):
            index = i + 6
            CameraDevice.objects.create(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',

            )

    def create_department(self):
        department = Department.objects.create(
            id=self.device_count,
            department_name=self.device_count

        )
        return department

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success_list(self):
        """测试成功获取标签列表"""

        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 5)

    def test_get_success_retrieve(self):
        """测试成功获取标签详情"""
        self.contact_url = self.contact_url + '/1'
        response = self.client.get(self.contact_url, data={}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['device_label_name'], 'name:1')

    def test_success_create(self):
        """测试成功创建设备标签"""
        data = OrderedDict()
        data['devices'] = [1, 2, 3]
        data['device_label_name'] = '123'
        data['content'] = '123'
        data['keywords'] = '123'
        data['color'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['device_label_name'], '123')

    def test_error_create_lack_name(self):
        """测试失败创建设标签，缺少名称"""
        data = OrderedDict()
        data['devices'] = [1, 2, 3]
        # data['device_group_name'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '缺少参数标签名称')

    def test_error_create_lack_device(self):
        """测试失败创建设标签，缺少设备id列表"""
        data = OrderedDict()
        # data['devices'] = [1, 2, 3]
        data['device_label_name'] = '123'
        data['content'] = '123'
        data['keywords'] = '123'
        data['color'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '缺少参数设备组设备')

    #
    def test_error_create_devices(self):
        """测试失败创建设备标签，设备id列表错误"""
        data = OrderedDict()
        data['devices'] = [1, 2, 9]
        data['device_label_name'] = '123'
        data['content'] = '123'
        data['keywords'] = '123'
        data['color'] = '123'
        response = self.client.post(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '参数devices错误')

    def test_success_detachments(self):
        """测试成功标签移除设备"""
        label = self.labels[0]
        label.devices.add(*self.devices)
        label.save()
        data = OrderedDict()
        data['devices'] = [1, 2, 3]
        self.contact_url = self.contact_url + '/1/detachments'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(label.devices.all()), 2)

    def test_error_detachments_device_error(self):
        """测试失败设备标签移除设备,设备id错误"""
        label = self.labels[0]
        label.devices.add(*self.devices)
        label.save()
        data = OrderedDict()
        data['devices'] = [1, 2, 8]
        self.contact_url = self.contact_url + '/1/detachments'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], 'device_name:8不属于选择设备标签，请重新选择')

    def test_error_detachments_lack_devices(self):
        """测试失败设备标签移除设备，缺少设备ID列表"""
        label = self.labels[0]
        label.devices.add(*self.devices)
        label.save()
        data = OrderedDict()
        data['devices'] = []
        self.contact_url = self.contact_url + '/1/detachments'
        response = self.client.patch(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '参数devices不能为空')


class DeviceGisInfoViewTestClass(APITestCase):
    """gis半径内摄像机设备信息接口测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/devices/gis'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.device_count = 5
        self.camera_device_count = 3
        self.devices = DeviceInfo.objects.bulk_create(list(self.create_devices()))
        self.create_camera_devices()
        self.user.department = self.create_department()
        self.user.save()

    def create_devices(self):
        count = self.device_count
        for i in range(count):
            index = i + 1
            yield DeviceInfo(
                id=index,
                device_type=DeviceInfo.DeviceType.MAINTENANCE.value,
                belong_system=DeviceInfo.BelongSystem.MAINTENANCE.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',
                gis_basic_info='5,5'
            )

    def create_camera_devices(self):
        count = self.camera_device_count
        for i in range(count):
            index = i + 6
            CameraDevice.objects.create(
                id=index,
                device_type=DeviceInfo.DeviceType.CAMERA.value,
                belong_system=DeviceInfo.BelongSystem.CAMERA.value,
                device_state=DeviceInfo.DeviceState.NORMAL.value,
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',
                gis_basic_info='5,5'

            )

    def create_department(self):
        department = Department.objects.create(
            id=self.device_count,
            department_name=self.device_count

        )
        return department

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功获取gis半径内设备"""
        data = OrderedDict()
        data['cover_radius'] = 10
        data['gis_basic_info'] = '1,1'
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 3)

    def test_get_success_empty(self):
        """测试gis半径内无设备"""
        data = OrderedDict()
        data['cover_radius'] = 3
        data['gis_basic_info'] = '1,1'
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['total_count'], 0)

    def test_get_error_lack_cover_radius(self):
        """测试缺少半径参数"""
        data = OrderedDict()
        # data['cover_radius'] = 3
        data['gis_basic_info'] = '1,1'
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], 'cover_radius不能为null')

    def test_get_error_cover_radius(self):
        """测试半径参数格式错误"""
        data = OrderedDict()
        data['cover_radius'] = 'qqq'
        data['gis_basic_info'] = '1,1'
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], '覆盖半径格式错误')

    def test_get_error_gis_basic_info(self):
        """测试gis参数格式错误"""
        data = OrderedDict()
        data['cover_radius'] = 10
        data['gis_basic_info'] = '1,q'
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error_message'], 'gis_basic_info格式错误')
