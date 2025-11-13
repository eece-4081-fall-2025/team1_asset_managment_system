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
    
    def test_create_asset_form_displays(self):
        """Test that create form is accessible"""
        response = self.client.get(reverse('asset_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Asset')
    
    def test_create_asset_with_valid_data(self):
        """Test creating asset with unique ID (Epic 1, Story 3)"""
        asset_data = {
            'name': 'New Laptop',
            'category': 'Electronics',
            'status': 'operational',
        }
        
        initial_count = Asset.objects.count()
        response = self.client.post(reverse('asset_create'), asset_data)
        
        # Check that asset was created
        self.assertEqual(Asset.objects.count(), initial_count + 1)
        new_asset = Asset.objects.get(name='New Laptop')
        self.assertEqual(new_asset.category, 'Electronics')
        self.assertIsNotNone(new_asset.id)  # Has unique ID
    
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
    
    def test_update_asset_details(self):
        """Test editing asset information (Epic 1, Story 5)"""
        updated_data = {
            'name': 'Updated Asset Name',
            'category': 'Furniture',
            'status': 'out_for_repairs',
        }
        
        response = self.client.post(
            reverse('asset_update', kwargs={'pk': self.asset.pk}),
            updated_data
        )
        
        # Refresh asset from database
        self.asset.refresh_from_db()
        
        # Check that changes were saved
        self.assertEqual(self.asset.name, 'Updated Asset Name')
        self.assertEqual(self.asset.category, 'Furniture')
        self.assertEqual(self.asset.status, 'out_for_repairs')


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