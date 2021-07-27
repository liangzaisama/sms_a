"""安保运行管理模块单元测试"""
from collections import OrderedDict
from datetime import datetime

from rest_framework.test import APIRequestFactory, APITestCase, APIClient

from .models import WatchAddressBook, EntranceAccessRecords
from .views import WatchAddressBookView
from users.models import User, UserDiary


class WatchAddressBookViewTestClass(APITestCase):
    """值班通讯录列表测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.view = WatchAddressBookView()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/contact'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.plan_group_count = 5
        self.plan_groups = WatchAddressBook.objects.bulk_create(list(self.create_watch_address_book()))

    def create_watch_address_book(self):
        count = self.plan_group_count
        for i in range(count):
            index = i + 1
            yield WatchAddressBook(
                id=index,
                department_name=f'department_name:{index}',
                staff_name=f'{index}',
                contact_mobile=f'contact_mobile:{index}',
                duty_date=datetime.today(),
            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功获取值班通讯录"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_duty_date_invalid(self):
        """测试参数格式错误"""
        data = OrderedDict()
        data['duty_date'] = 123
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.data['error_message'], '值班日期格式错误')

    def test_query_staff_name(self):
        """测试员工姓名查询"""
        data = OrderedDict()
        data['staff_name'] = 1
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.data['data']['objects'][0]['staff_name'], '1')


class WatchAddressBookViewDownloadTestClass(APITestCase):
    """值班通讯录下载测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.view = WatchAddressBookView()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/contact/exports'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.plan_group_count = 5
        self.plan_groups = WatchAddressBook.objects.bulk_create(list(self.create_watch_address_book()))

    def create_watch_address_book(self):
        count = self.plan_group_count
        for i in range(count):
            index = i + 1
            yield WatchAddressBook(
                id=index,
                department_name=f'department_name:{index}',
                staff_name=f'{index}',
                contact_mobile=f'contact_mobile:{index}',
                duty_date=datetime.today(),
            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功下载值班通讯录"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_duty_date_invalid(self):
        """测试参数格式错误"""
        data = OrderedDict()
        data['duty_date'] = 123
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.data['error_message'], '值班日期格式错误')

    def test_query_staff_name(self):
        """测试员工姓名查询"""
        data = OrderedDict()
        data['staff_name'] = 1
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_download_empty_excel(self):
        """测试下载空模板"""
        data = OrderedDict()
        data['duty_date'] = '2020-12-26'
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)


class WatchAddressBookTemplateDownloadViewTestClass(APITestCase):
    """值班通讯录模板下载测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.view = WatchAddressBookView()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/contact/exports/template'
        # self.accept = 'application/json；version=2.0'
        # 批量创建值班通讯录
        self.plan_group_count = 5
        self.plan_groups = WatchAddressBook.objects.bulk_create(list(self.create_watch_address_book()))

    def create_watch_address_book(self):
        count = self.plan_group_count
        for i in range(count):
            index = i + 1
            yield WatchAddressBook(
                id=index,
                department_name=f'department_name:{index}',
                staff_name=f'{index}',
                contact_mobile=f'contact_mobile:{index}',
                duty_date=datetime.today(),
            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功下载值班通讯录"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)


class AccessRecordsViewTestClass(APITestCase):
    """值班通讯录列表测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/access/records'
        # self.accept = 'application/json；version=2.0'
        # 批量创建通行记录
        self.access_record_count = 5
        self.access_records = EntranceAccessRecords.objects.bulk_create(list(self.create_access_record()))

    def create_access_record(self):
        count = self.access_record_count
        for i in range(count):
            index = i + 1
            yield EntranceAccessRecords(
                id=index,
                entrance_punch_code=f'entrance_punch_code:{index}',
                device_code=f'device_code:{index}',
                device_name=f'device_name:{index}',
                card_no=f'card_no:{index}',
                in_out=1,
                region_id=f'index',
                record_time=datetime.now(),
            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功获取门禁通行记录"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_duty_date_invalid(self):
        """测试参数格式错误"""
        data = OrderedDict()
        data['start_time'] = 123
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.data['error_message'], '开始时间格式错误')

    def test_success_query_data_filter(self):
        """测试条件查询成功"""
        data = OrderedDict()
        data['device_name'] = 1
        data['holder'] = 1
        data['start_time'] = datetime.now()
        data['end_time'] = datetime.now()
        data['holder'] = datetime.now()
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_query_device_name(self):
        """测试成功过滤设备名称查询"""
        data = OrderedDict()
        data['device_name'] = '1'
        response = self.client.get(self.contact_url, data=data, format='json')
        self.assertEqual(response.data['data']['objects'][0]['device_name'], 'device_name:1')


class UserDiaryViewTestClass(APITestCase):
    """用户日志创建、获取列表测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/users/diary'
        # self.accept = 'application/json；version=2.0'
        # 批量用户日志
        self.info_count = 5
        self.user_diary = UserDiary.objects.bulk_create(list(self.create_user_diary()))

    def create_user_diary(self):
        count = self.info_count
        for i in range(count):
            index = i + 1
            yield UserDiary(
                id=index,
                user=self.user,
                handover_user=self.user,
                job_content=f'job_content:{index}',
                handover_content=f'handover_content:{index}',
                job_time=datetime.now(),
            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功获取用户日志"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_duty_date_invalid(self):
        """测试参数格式错误"""
        data = OrderedDict()
        data['start_time'] = 123
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.data['error_message'], '开始时间格式错误')

    def test_success_query_data_filter(self):
        """测试条件查询成功"""
        data = OrderedDict()
        data['username'] = 1
        data['handover_username'] = 1
        # data['department_id'] = 1
        data['start_time'] = datetime.now()
        data['end_time'] = datetime.now()
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_query_device_name(self):
        """测试成功过滤工作内容查询"""
        data = OrderedDict()
        data['username'] = 'jacob'
        response = self.client.get(self.contact_url, data=data, format='json')
        self.assertEqual(len(response.data['data']['objects']), 5)

    def test_post_single_success(self):
        """测试成功单条创建用户日志"""
        data = OrderedDict()
        data['job_content'] = "工作内容"
        data['job_time'] = datetime.now()
        data['is_handover'] = 0

        response = self.client.post(self.contact_url, data=data, format='json')
        diary_count = UserDiary.objects.all().count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(diary_count, 6)

    def test_post_single_error(self):
        """测试失败单条创建用户日志"""
        data = OrderedDict()
        data['job_content'] = "工作内容"
        data['job_time'] = 123
        data['is_handover'] = 1

        response = self.client.post(self.contact_url, data=data, format='json')
        self.assertEqual(response.data['error_message'], '时间格式错误')

    def test_post_batch_success(self):
        """测试成功批量创建用户日志"""
        data = []
        single_data = OrderedDict()
        single_data['job_content'] = "工作内容"
        single_data['job_time'] = datetime.now()
        single_data['is_handover'] = 0
        data.append(single_data)
        data.append(single_data)
        response = self.client.post(self.contact_url, data=data, format='json')
        diary_count = UserDiary.objects.all().count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(diary_count, 7)

    def test_post_batch_param_error_job_time(self):
        """测试失败批量创建用户日志参数错误"""
        data = []
        single_data = OrderedDict()
        single_data['job_content'] = "工作内容"
        single_data['job_time'] = datetime.now()
        single_data['is_handover'] = 0
        data.append(single_data)
        single_data['job_time'] = 123
        data.append(single_data)
        response = self.client.post(self.contact_url, data=data, format='json')
        self.assertEqual(response.data['error_message'], '时间格式错误')

    def test_post_batch_param_error_is_handover(self):
        """测试失败批量创建用户日志参数错误"""
        data = []
        single_data = OrderedDict()
        single_data['job_content'] = "工作内容"
        single_data['job_time'] = datetime.now()
        data.append(single_data)
        data.append(single_data)
        response = self.client.post(self.contact_url, data=data, format='json')
        self.assertEqual(response.data['error_message'], 'is_handover不能为null')

    def test_post_batch_empty_data(self):
        """测试失败批量创建用户日志参数为空"""
        data = []

        response = self.client.post(self.contact_url, data=data, format='json')
        self.assertEqual(response.data['error_message'], '请求数据解析错误')


class UserDiaryViewDownloadTestClass(APITestCase):
    """用户日志下载测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/users/diary/exports'
        # self.accept = 'application/json；version=2.0'
        # 批量用户日志
        self.info_count = 5
        self.user_diary = UserDiary.objects.bulk_create(list(self.create_user_diary()))

    def create_user_diary(self):
        count = self.info_count
        for i in range(count):
            index = i + 1
            yield UserDiary(
                id=index,
                user=self.user,
                handover_user=self.user,
                job_content=f'job_content:{index}',
                handover_content=f'handover_content:{index}',
                job_time=datetime.now(),
            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_get_success(self):
        """测试成功下载用户日志"""
        response = self.client.get(self.contact_url, data={}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_duty_date_invalid(self):
        """测试参数格式错误"""
        data = OrderedDict()
        data['start_time'] = 123
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.data['error_message'], '开始时间格式错误')

    def test_success_query_data_filter(self):
        """测试条件查询成功"""
        data = OrderedDict()
        data['username'] = 1
        data['handover_username'] = 1
        # data['department_id'] = 1
        data['start_time'] = datetime.now()
        data['end_time'] = datetime.now()
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_query_device_name(self):
        """测试成功过滤工作内容查询"""
        data = OrderedDict()
        data['username'] = 'jacob'
        response = self.client.get(self.contact_url, data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_download_empty_excel(self):
        """测试下载空模板"""
        data = OrderedDict()
        data['start_time'] = datetime.now()
        response = self.client.get(self.contact_url, data=data, format='json')

        self.assertEqual(response.status_code, 200)


class UserDiaryDetailTestClass(APITestCase):
    """用户日志交接确认测试"""

    def setUp(self):
        """该方法会首先执行，相当于做测试前的准备工作"""
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        self.user_test = User.objects.create_user(username='test', email='jacob@…', password='top_secret')
        self.user.is_superuser = True
        self.user.save()
        # 通过force_authenticate函数来执行用户
        self.client.force_authenticate(self.user)

        self.contact_url = '/api/users/diary/1'
        # self.accept = 'application/json；version=2.0'
        # 批量用户日志
        self.info_count = 5
        self.user_diary = UserDiary.objects.bulk_create(list(self.create_user_diary()))

    def create_user_diary(self):
        count = self.info_count
        for i in range(count):
            index = i + 1
            yield UserDiary(
                id=index,
                user=self.user,
                handover_user=self.user,
                job_content=f'job_content:{index}',
                handover_content=f'handover_content:{index}',
                job_time=datetime.now(),
            )

    def tearDown(self):
        """该方法会在测试代码执行完后执行，相当于做测试后的扫尾工作"""
        pass

    def test_put_success(self):
        """测试成功确认交接用户日志"""
        index = 6
        UserDiary.objects.create(
            id=index,
            user=self.user,
            handover_user=self.user,
            job_content=f'job_content:{index}',
            handover_content=f'handover_content:{index}',
            job_time=datetime.now(),
            is_handover=1
        )
        response = self.client.put('/api/users/diary/6', data={}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_put_error_is_handover(self):
        """测试失败确认交接用户日志无需交接"""
        response = self.client.put(self.contact_url, data={}, format='json')

        self.assertEqual(response.data['error_message'], '当前日志未交接无需确认')
        self.assertEqual(response.status_code, 400)

    def test_put_error_user(self):
        """测试失败确认交接用户日志用户不符合"""
        index = 6
        UserDiary.objects.create(
            id=index,
            user=self.user,
            handover_user=self.user_test,
            job_content=f'job_content:{index}',
            handover_content=f'handover_content:{index}',
            job_time=datetime.now(),
            is_handover=1
        )
        response = self.client.put('/api/users/diary/6', data={}, format='json')

        self.assertEqual(response.data['error_message'], '当前用户与交接用户不符')
        self.assertEqual(response.status_code, 400)

    def test_put_error_is_confirm(self):
        """测试失败确认交接用户日志用户不符合"""
        index = 6
        UserDiary.objects.create(
            id=index,
            user=self.user,
            handover_user=self.user,
            job_content=f'job_content:{index}',
            handover_content=f'handover_content:{index}',
            job_time=datetime.now(),
            is_handover=1,
            is_confirm=1
        )
        response = self.client.put('/api/users/diary/6', data={}, format='json')

        self.assertEqual(response.data['error_message'], '当前日志已确认交接')
        self.assertEqual(response.status_code, 400)
