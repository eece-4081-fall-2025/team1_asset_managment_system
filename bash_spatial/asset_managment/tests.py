from django.test import TestCase
from asset_managment.models import Asset


class AssetTests(TestCase):
    def setUp(self):
        Asset.objects.create(name="Example1")

    # unit test added by Braxton
    def test_asset_creation(self):
        example1 = Asset.objects.get(name="Example1")
        self.assertEqual(example1.name, "Example1")
