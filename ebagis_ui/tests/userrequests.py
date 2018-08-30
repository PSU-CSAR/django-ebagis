from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils import dateformat

from ebagis.models.aoi import AOI
from ebagis.models.upload import Upload
from ebagis.models.download import Download
from djcelery.models import TaskMeta
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model


class UploadTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='akeifer2')
        self.user.set_password('12345')
        self.user.save()

        self.client = Client()
        self.client.force_login(self.user)

        task = TaskMeta.objects.create(
            id=1,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a1",
            status="SUCCESS",
            date_done="2017-03-22T05:52:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f1",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="animas",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload complete, task failure
        task = TaskMeta.objects.create(
            id=2,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a2",
            status="FAILURE",
            date_done="2017-03-22T05:52:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f2",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="upload_complete_task_failed",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload complete, task success
        task = TaskMeta.objects.create(
            id=3,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a3",
            status="SUCCESS",
            date_done="2017-03-22T05:50:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f3",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="upload_complete_task_success",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload complete, task pending
        task = TaskMeta.objects.create(
            id=4,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a4",
            status="PENDING",
            date_done="2017-03-22T05:50:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f4",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="upload_complete_task_pending",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload complete, task started
        task = TaskMeta.objects.create(
            id=6,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a5",
            status="STARTED",
            date_done="2017-03-22T05:50:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f6",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="upload_complete_task_started",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=True,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        #upload complete, task retry
        task = TaskMeta.objects.create(
            id=5,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a6",
            status="RETRY",
            date_done="2017-03-22T05:50:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f5",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="upload_complete_task_retry",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload complete, task aborted
        task = TaskMeta.objects.create(
            id=7,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a7",
            status="ABORTED",
            date_done="2017-03-22T05:50:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f7",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="upload_complete_task_aborted",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload success, task rovoked
        task = TaskMeta.objects.create(
            id=8,
            result="http://localhost:8000/api/rest/aois/665355c0-a453-48aa-8c1b-5291220c6b91/",
            task_id="57ddf937-95f7-4008-9417-648a5b3cf4a8",
            status="REVOKED",
            date_done="2017-03-22T05:50:38.902000Z",
            traceback=None,
            hidden=False,
            meta="eJxrYKotZIzgYGBgSM7IzEkpSs2LLdYDADylBhk=",
        )

        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f8",
            user=self.user,
            task=task,
            status=Upload.COMPLETE,
            filename="upload_complete_task_revoked",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload uploading
        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a943f9",
            user=self.user,
            task=None,
            status=Upload.UPLOADING,
            filename="upload_uploading",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )

        # upload aborted
        Upload.objects.create(
            id="5c6829eb-3d77-434a-9e0c-c52d87a94310",
            user=self.user,
            task=None,
            status=Upload.ABORTED,
            filename="upload_aborted",
            offset=54977200,
            object_id="665355c0-a453-48aa-8c1b-5291220c6b91",
            is_update=False,
            parent_object_id=None,
            comment="",
            content_type=ContentType.objects.get_for_model(AOI),
            parent_object_content_type=None
        )
    def test_upload_is_aborted_false(self):
        """Uploads that are not aborted are correctly identified"""
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f1')
        self.assertEqual(upload.is_aborted(), False)

    def test_requests_page(self):
        response = self.client.get(reverse('account_requests'))
        with open('./testoutput.html', 'w') as f:
            f.write(response.content)
        self.assertEqual(response.status_code, 200)

    def test_request_upload_complete_task_failed(self):
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f2')
        time = dateformat.format(timezone.localtime(upload.created_at), 'F j, Y, P')

        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)
        self.assertEqual(upload.status, upload.COMPLETE)
        self.assertEqual(upload.task.status, "FAILURE")
        self.assertContains(response, row, html=True)

    def test_request_upload_complete_task_success(self):
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f3')
        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)
        self.assertEqual(upload.status, upload.COMPLETE)
        self.assertEqual(upload.task.status, "SUCCESS")
        self.assertContains(response, row, html=True)

    def test_request_upload_complete_task_pending(self):
        # Status = Processing
        # Actions = Cancel
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f4')

        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)
        self.assertEqual(upload.status, upload.COMPLETE)
        self.assertEqual(upload.task.status, "PENDING")
        self.assertContains(response, row, html=True)

    def test_request_upload_complete_task_retry(self):
        # Status = Processing
        # Actions = Cancel
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f5')

        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)
        self.assertEqual(upload.status, upload.COMPLETE)
        self.assertEqual(upload.task.status, "RETRY")
        self.assertContains(response, row, html=True)

    def test_request_upload_complete_task_started(self):
        # Status = Processing
        # Actions = Cancel
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f6')

        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)
        self.assertEqual(upload.status, upload.COMPLETE)
        self.assertEqual(upload.task.status, "STARTED")
        self.assertContains(response, row, html=True)

    def test_request_upload_complete_task_aborted(self):
        # Status = Cancelled
        # Actions = N/A
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f7')

        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)

        self.assertEqual(upload.status, upload.COMPLETE)
        self.assertEqual(upload.task.status, "ABORTED")
        self.assertContains(response, row, html=True)

    def test_request_upload_complete_task_revoked(self):
        # Status = Cancelled
        # Actions = N/A
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f8')

        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)
        self.assertEqual(upload.status, upload.COMPLETE)
        self.assertEqual(upload.task.status, 'REVOKED')
        self.assertContains(response, row, html=True)

    def test_request_upload_uploading(self):
        # Status = Incomplete
        # Actions = Cancel
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a943f9')
        response = self.client.get(reverse('account_requests'))
        row = self.create_row(upload)

        self.assertEqual(upload.status, upload.UPLOADING)
        self.assertEqual(upload.task, None)
        self.assertContains(response, row, html=True)

    def test_request_upload_aborted(self):
        # Status = Cancelled
        # Actions = N/A
        upload = Upload.objects.get(id='5c6829eb-3d77-434a-9e0c-c52d87a94310')

        response = self.client.get(reverse('account_requests'))

        row = self.create_row(upload)
        self.assertEqual(upload.status, upload.ABORTED)
        self.assertEqual(upload.task, None)
        self.assertContains(response, row, html=True)

#        context['processing_states'] = ['PENDING', 'RETRY', 'STARTED']
#        context['cancelled_states'] = ['ABORTED', 'REVOKED']

    @staticmethod
    def create_row(upload):
        time = dateformat.format(timezone.localtime(upload.created_at), 'F j, Y, P')

        if upload.status == upload.ABORTED:
            status = '<span class="badge badge-warning">Cancelled</span>'
            action = '<span class="badge badge-dark">N/A</span>'
        elif upload.status == upload.UPLOADING:
            status = '<span class="badge badge-info">Incomplete</span>'
            action = '<button class="btn btn-sm btn-warning"><i class="fa fa-ban" aria-hidden="true"></i> Cancel</button>'
        elif upload.status == upload.COMPLETE and (upload.task is None or upload.task.status == 'SUCCESS'):
            status = '<span class="badge badge-success">Completed</span>'
            action = '<button class="btn btn-sm btn-success"><i class="fa fa-eye" aria-hidden="true"></i> View Result</button>'
        elif upload.task.status in ['REVOKED', 'ABORTED']:
            status = '<span class="badge badge-warning">Cancelled</span>'
            action = '<span class="badge badge-dark">N/A</span>'
        elif upload.task.status in ['PENDING', 'RETRY', 'STARTED']:
            status = '<span class="badge badge-primary">Processing</span>'
            action = '<button class="btn btn-sm btn-warning"><i class="fa fa-ban" aria-hidden="true"></i> Cancel</button>'
        elif upload.task.status == 'FAILURE':
            status = '<span class="badge badge-danger">Failed</span>'
            action = '<button class="btn btn-sm btn-danger"><i class="fa fa-exclamation-triangle" aria-hidden="true"></i> View Error</button>'
        else:
            status = '<span">Missing a case</span>'
            action = '<span">Missing a case</span>'

        if upload.is_update:
            operation = '<span class="badge badge-info">Update</span>'
        else:
            operation = '<span class="badge badge-primary">Create</span>'

        return '''<tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>

                <td>{}</td>

                <td> {}</td>
                </tr>'''.format(status, upload.filename, time, operation, action)
