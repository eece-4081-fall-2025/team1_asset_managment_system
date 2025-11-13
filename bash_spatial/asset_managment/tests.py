from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from asset_managment.models import Asset, Attribute
import uuid

# ========== BRAXTON'S BACKEND UNIT TESTS ==========

class AssetTests(TestCase):
    def setUp(self):
        Asset.objects.create(name="Example1")

    # unit test added by Braxton
    def test_asset_creation(self):
        example1 = Asset.objects.get(name="Example1")
        self.assertEqual(example1.name, "Example1")

# ========== SARA'S FRONTEND UNIT TESTS ==========

class LoginViewTests(TestCase):
    """
    Unit tests for login functionality (Epic 4, Story 23)
    Written by: Sara
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_page_loads(self):
        """Test that login page is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Asset Management')
    
    def test_login_with_valid_credentials(self):
        """Test successful login redirects to asset list"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('asset_list'))
    
    def test_login_with_invalid_credentials(self):
        """Test that invalid login shows error"""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
        # Should show login form again


class AssetListViewTests(TestCase):
    """
    Unit tests for asset list display and filtering (Epic 1, Stories 2-4)
    Written by: Sara
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test assets
        Asset.objects.create(
            name='Dell Laptop',
            category='Electronics',
            status='operational'
        )
        Asset.objects.create(
            name='Office Chair',
            category='Furniture',
            status='operational'
        )
        Asset.objects.create(
            name='Adobe License',
            category='Software',
            status='depricated'
        )
    
    def test_asset_list_requires_login(self):
        """Test that asset list requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('asset_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_asset_list_displays_all_assets(self):
        """Test that asset list shows all assets (Epic 1, Story 2)"""
        response = self.client.get(reverse('asset_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 3)
        self.assertContains(response, 'Dell Laptop')
        self.assertContains(response, 'Office Chair')
        self.assertContains(response, 'Adobe License')
    
    def test_asset_search_by_name(self):
        """Test search functionality by name (Epic 1, Story 4)"""
        response = self.client.get(reverse('asset_list'), {'search': 'Laptop'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 1)
        self.assertContains(response, 'Dell Laptop')
        self.assertNotContains(response, 'Office Chair')
    
    def test_asset_filter_by_category(self):
        """Test filtering by category (Epic 1, Story 4)"""
        response = self.client.get(reverse('asset_list'), {'category': 'Electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 1)
        self.assertContains(response, 'Dell Laptop')
    
    def test_asset_filter_by_status(self):
        """Test filtering by status"""
        response = self.client.get(reverse('asset_list'), {'status': 'depricated'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 1)
        self.assertContains(response, 'Adobe License')
    
    def test_empty_search_results(self):
        """Test that empty search shows appropriate message"""
        response = self.client.get(reverse('asset_list'), {'search': 'NonexistentAsset'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 0)


class AssetDetailViewTests(TestCase):
    """
    Unit tests for asset detail page (Epic 1, Stories 5, 8, 9)
    Written by: Sara
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.asset = Asset.objects.create(
            name='Test Laptop',
            category='Electronics',
            status='operational'
        )
        
        # Add attributes
        Attribute.objects.create(
            asset=self.asset,
            name='Serial Number',
            value='SN12345'
        )
        Attribute.objects.create(
            asset=self.asset,
            name='Purchase Date',
            value='2024-01-15'
        )
    
    def test_asset_detail_displays_basic_info(self):
        """Test that detail page shows asset information (Epic 1, Story 8)"""
        response = self.client.get(reverse('asset_detail', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Laptop')
        self.assertContains(response, 'Electronics')
        self.assertContains(response, 'Operational')
    
    def test_asset_detail_displays_attributes(self):
        """Test that detail page shows custom attributes (Epic 1, Story 9)"""
        response = self.client.get(reverse('asset_detail', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Serial Number')
        self.assertContains(response, 'SN12345')
        self.assertContains(response, 'Purchase Date')
        self.assertContains(response, '2024-01-15')
    
    def test_asset_detail_shows_edit_button(self):
        """Test that edit button is visible"""
        response = self.client.get(reverse('asset_detail', kwargs={'pk': self.asset.pk}))
        self.assertContains(response, 'Edit Asset')


class AssetCreateViewTests(TestCase):
    """
    Unit tests for asset creation (Epic 1, Story 3)
    Written by: Sara
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    

    def test_create_asset_requires_name(self):
        """Test that asset name is required"""
        asset_data = {
            'category': 'Electronics',
            'status': 'operational',
        }
        
        response = self.client.post(reverse('asset_create'), asset_data)
        # Should stay on form page with error
        self.assertEqual(response.status_code, 200)


class AssetUpdateViewTests(TestCase):
    """
    Unit tests for editing assets (Epic 1, Story 5)
    Written by: Sara
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.asset = Asset.objects.create(
            name='Test Asset',
            category='Electronics',
            status='operational'
        )
    
    def test_update_asset_form_displays(self):
        """Test that edit form shows existing data"""
        response = self.client.get(reverse('asset_update', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Asset')
        self.assertContains(response, 'Edit Asset')
    
class AssetDeleteViewTests(TestCase):
    """
    Unit tests for deleting assets (Epic 1, Story 7)
    Written by: Sara
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.asset = Asset.objects.create(
            name='Asset to Delete',
            category='Electronics',
            status='depricated'
        )
    
    def test_delete_confirmation_page_displays(self):
        """Test that delete confirmation page shows"""
        response = self.client.get(reverse('asset_delete', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Asset')
        self.assertContains(response, 'Asset to Delete')
    
    def test_delete_asset_removes_from_database(self):
        """Test deleting outdated assets (Epic 1, Story 7)"""
        asset_id = self.asset.pk
        initial_count = Asset.objects.count()
        
        response = self.client.post(reverse('asset_delete', kwargs={'pk': asset_id}))
        
        # Check that asset was deleted
        self.assertEqual(Asset.objects.count(), initial_count - 1)
        self.assertFalse(Asset.objects.filter(pk=asset_id).exists())
        
        # Should redirect to asset list
        self.assertEqual(response.status_code, 302)


class AssetCategoryTests(TestCase):
    """
    Unit tests for categorization (Epic 1, Story 4)
    Written by: Sara
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create assets in different categories
        Asset.objects.create(name='Laptop', category='Electronics', status='operational')
        Asset.objects.create(name='Desk', category='Furniture', status='operational')
        Asset.objects.create(name='Software', category='Software', status='operational')
    
    def test_assets_can_be_categorized(self):
        """Test that assets support categories (Epic 1, Story 4)"""
        laptop = Asset.objects.get(name='Laptop')
        self.assertEqual(laptop.category, 'Electronics')
        
        desk = Asset.objects.get(name='Desk')
        self.assertEqual(desk.category, 'Furniture')
    
    def test_category_list_appears_in_filter(self):
        """Test that categories appear in filter dropdown"""
        response = self.client.get(reverse('asset_list'))
        self.assertEqual(response.status_code, 200)
        
        categories = response.context['categories']
        self.assertIn('Electronics', categories)
        self.assertIn('Furniture', categories)
        self.assertIn('Software', categories)

class AttributeModelTests(TestCase):
    """
    Tests for the Attribute model to ensure correct linking and behavior.
    """

    def setUp(self):
        self.asset = Asset.objects.create(
            name="Test Asset",
            category="Electronics",
            status="operational"
        )
        self.attribute = Attribute.objects.create(
            asset=self.asset,
            name="Serial Number",
            value="SN9999"
        )

    def test_attribute_creation(self):
        """Attribute should be created successfully and linked to an asset"""
        self.assertEqual(self.attribute.name, "Serial Number")
        self.assertEqual(self.attribute.value, "SN9999")
        self.assertEqual(self.attribute.asset, self.asset)

    def test_attribute_str_representation(self):
        """Test __str__ returns readable format"""
        self.assertTrue(str(self.attribute))

from django.urls import resolve
from asset_managment import views

class URLResolutionTests(TestCase):
    """
    Test that named URLs resolve to the correct views.
    """

    def test_asset_list_resolves(self):
        url = reverse('asset_list')
        self.assertEqual(resolve(url).func.view_class, views.AssetListView)

    def test_asset_create_resolves(self):
        url = reverse('asset_create')
        self.assertEqual(resolve(url).func.view_class, views.AssetCreateView)

    def test_asset_detail_resolves(self):
        asset = Asset.objects.create(name="Test")
        url = reverse('asset_detail', kwargs={'pk': asset.pk})
        self.assertEqual(resolve(url).func.view_class, views.AssetDetailView)

    def test_asset_update_resolves(self):
        asset = Asset.objects.create(name="Test")
        url = reverse('asset_update', kwargs={'pk': asset.pk})
        self.assertEqual(resolve(url).func.view_class, views.AssetUpdateView)

    def test_asset_delete_resolves(self):
        asset = Asset.objects.create(name="Test")
        url = reverse('asset_delete', kwargs={'pk': asset.pk})
        self.assertEqual(resolve(url).func.view_class, views.AssetDeleteView)

class AssetNotFoundTests(TestCase):
    """
    Ensure views return 404 for missing assets.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='u', password='p')
        self.client.login(username='u', password='p')

    def test_detail_404(self):
        response = self.client.get(reverse('asset_detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_update_404(self):
        response = self.client.get(reverse('asset_update', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_delete_404(self):
        response = self.client.get(reverse('asset_delete', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)

class LoginRequiredTests(TestCase):
    """
    Test that CRUD endpoints require authentication.
    """

    def setUp(self):
        self.asset = Asset.objects.create(name="Chair")

    def test_detail_requires_login(self):
        response = self.client.get(reverse('asset_detail', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 302)

    def test_create_requires_login(self):
        response = self.client.get(reverse('asset_create'))
        self.assertEqual(response.status_code, 302)

    def test_update_requires_login(self):
        response = self.client.get(reverse('asset_update', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 302)

    def test_delete_requires_login(self):
        response = self.client.get(reverse('asset_delete', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 302)
        
class AssetUpdatePOSTTests(TestCase):
    """
    Verify that submitting the edit form updates the asset.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='pass')
        self.client.login(username='test', password='pass')

        self.asset = Asset.objects.create(
            name="Old Name",
            category="Electronics",
            status="operational"
        )

    def test_update_asset_post(self):
        """POSTing valid data should modify the asset"""
        response = self.client.post(
            reverse('asset_update', kwargs={'pk': self.asset.pk}),
            {
                'name': 'Updated Name',
                'category': 'Electronics',
                'status': 'operational'
            }
        )
        self.assertEqual(response.status_code, 302)

        # Refresh from DB
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.name, "Updated Name")

class AssetDetailNoAttributeTests(TestCase):
    """
    Ensure detail page handles assets with no attributes.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='u', password='p')
        self.client.login(username='u', password='p')
        self.asset = Asset.objects.create(
            name="NoAttr Asset",
            category="Electronics",
            status="operational"
        )

    def test_detail_page_shows_no_attributes_message(self):
        response = self.client.get(reverse('asset_detail', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Attributes")  # adjust based on template wording

class AttributeCRUDTests(TestCase):
    """
    Basic tests for creating and deleting attributes from the UI.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="u", password="p")
        self.client.login(username="u", password="p")
        self.asset = Asset.objects.create(
            name="Laptop",
            category="Electronics",
            status="operational"
        )

    def test_add_attribute(self):
        """Test that an attribute can be added through POST."""
        response = self.client.post(
            reverse('attribute_create', kwargs={'pk': self.asset.pk}),
            {
                'name': 'Color',
                'value': 'Black'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Attribute.objects.filter(name='Color', asset=self.asset).exists())

    def test_delete_attribute(self):
        """Test that attribute delete removes the attribute."""
        attribute = Attribute.objects.create(
            asset=self.asset,
            name='Serial',
            value='1000'
        )

        response = self.client.post(
            reverse('attribute_delete', kwargs={'pk': attribute.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Attribute.objects.filter(pk=attribute.pk).exists())


