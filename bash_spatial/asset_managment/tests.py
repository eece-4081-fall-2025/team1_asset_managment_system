from django.test import TestCase
from asset_managment.models import Asset, Attribute


class TaskTests(TestCase):
    def setUp(self):
        Asset.objects.create(name="Example1")

    def test_task_creation(self):
        example1 = Asset.objects.get(name="Example1")
        self.assertEqual(example1.name, "Example1")
