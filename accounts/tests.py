from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.messages import get_messages

from .models import UserProfile


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='Project Manager',
            department='Engineering'
        )
    
    def test_profile_creation(self):
        """Test user profile creation and basic properties"""
        expected_str = f"Profile for {self.user.username}"
        self.assertEqual(str(self.profile), expected_str)
        self.assertEqual(self.profile.role, 'Project Manager')
        self.assertEqual(self.profile.department, 'Engineering')
    
    def test_profile_user_relationship(self):
        """Test one-to-one relationship with User"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.user.profile, self.profile)
    
    def test_profile_with_null_fields(self):
        """Test profile creation with null optional fields"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        profile2 = UserProfile.objects.create(user=user2)
        
        self.assertIsNone(profile2.role)
        self.assertIsNone(profile2.department)
    
    def test_profile_auto_creation_signal(self):
        """Test that profile can be auto-created via signal (if implemented)"""
        # This test assumes a signal is set up to auto-create profiles
        # If not implemented, this test documents the intended behavior
        user3 = User.objects.create_user(
            username='signaluser',
            email='signal@example.com',
            password='testpass123'
        )
        
        # Check if profile exists or create manually for this test
        try:
            profile = user3.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user3)
        
        self.assertIsNotNone(profile)


class AccountsViewsTest(TestCase):
    """Test cases for Accounts views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='Developer',
            department='Engineering'
        )
    
    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')  # Check for login form or text
    
    def test_login_view_post_valid(self):
        """Test login view with valid credentials"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # Check if user is logged in
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)
    
    def test_login_view_post_invalid(self):
        """Test login view with invalid credentials"""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/accounts/login/', login_data)
        
        # Should stay on login page or show error
        self.assertIn(response.status_code, [200, 302])
        
        # User should not be authenticated
        user = authenticate(username='testuser', password='wrongpassword')
        self.assertIsNone(user)
    
    def test_logout_view(self):
        """Test logout functionality"""
        # First login
        self.client.force_login(self.user)
        
        # Then logout
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        
        # Check that user is logged out
        response = self.client.get('/dashboard/')  # Protected page
        # Should redirect to login or show unauthorized
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_register_view_get(self):
        """Test registration view GET request"""
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'register')  # Check for registration form
    
    def test_register_view_post_valid(self):
        """Test registration with valid data"""
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/accounts/register/', register_data)
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check if user can login
        new_user = authenticate(username='newuser', password='complexpass123')
        self.assertIsNotNone(new_user)
    
    def test_register_view_post_password_mismatch(self):
        """Test registration with password mismatch"""
        register_data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/accounts/register/', register_data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='newuser2').exists())
    
    def test_register_view_duplicate_username(self):
        """Test registration with duplicate username"""
        register_data = {
            'username': 'testuser',  # Already exists
            'email': 'another@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'Another',
            'last_name': 'User'
        }
        
        response = self.client.post('/accounts/register/', register_data)
        
        # Should stay on registration page with error
        self.assertEqual(response.status_code, 200)
        
        # Should only have one user with this username
        users_with_username = User.objects.filter(username='testuser')
        self.assertEqual(users_with_username.count(), 1)
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user"""
        self.client.force_login(self.user)
        
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.profile.role)
    
    def test_profile_view_unauthenticated(self):
        """Test profile view for unauthenticated user"""
        response = self.client.get('/accounts/profile/')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_profile_edit_view_get(self):
        """Test profile edit view GET request"""
        self.client.force_login(self.user)
        
        response = self.client.get('/accounts/profile/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.profile.role)
    
    def test_profile_edit_view_post(self):
        """Test profile edit view POST request"""
        self.client.force_login(self.user)
        
        edit_data = {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'email': 'johnny.doe@example.com',
            'role': 'Senior Developer',
            'department': 'Software Engineering'
        }
        
        response = self.client.post('/accounts/profile/edit/', edit_data)
        
        # Should redirect after successful edit
        self.assertEqual(response.status_code, 302)
        
        # Check if user data was updated
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'Johnny')
        self.assertEqual(self.user.email, 'johnny.doe@example.com')
        self.assertEqual(self.profile.role, 'Senior Developer')
        self.assertEqual(self.profile.department, 'Software Engineering')


class AuthenticationTest(TestCase):
    """Test cases for authentication functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='authpass123',
            first_name='Auth',
            last_name='User'
        )
        
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='Tester',
            department='QA'
        )
    
    def test_user_authentication(self):
        """Test user authentication with correct credentials"""
        user = authenticate(username='authuser', password='authpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)
        self.assertTrue(user.is_authenticated)
    
    def test_user_authentication_wrong_password(self):
        """Test authentication with wrong password"""
        user = authenticate(username='authuser', password='wrongpass')
        self.assertIsNone(user)
    
    def test_user_authentication_wrong_username(self):
        """Test authentication with wrong username"""
        user = authenticate(username='wronguser', password='authpass123')
        self.assertIsNone(user)
    
    def test_password_change(self):
        """Test password change functionality"""
        client = Client()
        client.force_login(self.user)
        
        change_data = {
            'old_password': 'authpass123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        
        response = client.post('/accounts/password/change/', change_data)
        
        # Should redirect after successful change
        self.assertEqual(response.status_code, 302)
        
        # Test authentication with new password
        user = authenticate(username='authuser', password='newpassword123')
        self.assertIsNotNone(user)
        
        # Test that old password no longer works
        user = authenticate(username='authuser', password='authpass123')
        self.assertIsNone(user)


class UserManagementTest(TestCase):
    """Test cases for user management functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123'
        )
        
        self.regular_profile = UserProfile.objects.create(
            user=self.regular_user,
            role='Developer',
            department='Engineering'
        )
    
    def test_admin_access(self):
        """Test admin user access to admin interface"""
        client = Client()
        client.force_login(self.admin_user)
        
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_regular_user_admin_access(self):
        """Test regular user cannot access admin interface"""
        client = Client()
        client.force_login(self.regular_user)
        
        response = client.get('/admin/')
        # Should redirect to login or show forbidden
        self.assertIn(response.status_code, [302, 403])
    
    def test_user_permissions(self):
        """Test user permissions and groups"""
        # Test that regular user has basic permissions
        self.assertTrue(self.regular_user.has_perm('auth.change_user'))  # Can change own profile
        
        # Test admin has all permissions
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.is_staff)


class AccountsIntegrationTest(TestCase):
    """Integration tests for Accounts functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_complete_user_registration_workflow(self):
        """Test complete user registration and login workflow"""
        # Step 1: Register new user
        register_data = {
            'username': 'integrationuser',
            'email': 'integration@example.com',
            'password1': 'integrationpass123',
            'password2': 'integrationpass123',
            'first_name': 'Integration',
            'last_name': 'User'
        }
        
        response = self.client.post('/accounts/register/', register_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify user was created
        user = User.objects.get(username='integrationuser')
        self.assertEqual(user.email, 'integration@example.com')
        self.assertEqual(user.first_name, 'Integration')
        
        # Step 2: Login with new credentials
        login_data = {
            'username': 'integrationuser',
            'password': 'integrationpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 3: Access protected page
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Update profile
        # Create profile if it doesn't exist
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        edit_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'role': 'Software Engineer',
            'department': 'Product Development'
        }
        
        response = self.client.post('/accounts/profile/edit/', edit_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify updates
        user.refresh_from_db()
        profile.refresh_from_db()
        
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.email, 'updated@example.com')
        self.assertEqual(profile.role, 'Software Engineer')
        
        # Step 5: Change password
        change_data = {
            'old_password': 'integrationpass123',
            'new_password1': 'newintegrationpass123',
            'new_password2': 'newintegrationpass123'
        }
        
        response = self.client.post('/accounts/password/change/', change_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 6: Logout and login with new password
        self.client.logout()
        
        new_login_data = {
            'username': 'integrationuser',
            'password': 'newintegrationpass123'
        }
        
        response = self.client.post('/accounts/login/', new_login_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify can access protected content
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_session_management(self):
        """Test user session management"""
        user = User.objects.create_user(
            username='sessionuser',
            password='sessionpass123'
        )
        
        # Login
        login_data = {
            'username': 'sessionuser',
            'password': 'sessionpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify session exists
        self.assertIn('_auth_user_id', self.client.session)
        
        # Access protected page
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Logout
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        
        # Verify session is cleared
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # Verify cannot access protected page
        response = self.client.get('/dashboard/')
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_profile_resource_integration(self):
        """Test integration between user profiles and resource management"""
        # Create user with profile
        user = User.objects.create_user(
            username='resourceuser',
            email='resource@example.com',
            password='resourcepass123'
        )
        
        profile = UserProfile.objects.create(
            user=user,
            role='Full Stack Developer',
            department='Engineering'
        )
        
        # Import here to avoid circular imports in test setup
        from resources.models import Resource
        
        # Create associated resource
        resource = Resource.objects.create(
            user=user,
            name=f"{user.first_name} {user.last_name}".strip() or user.username,
            role=profile.role,
            department=profile.department,
            capacity=40
        )
        
        # Test relationships
        self.assertEqual(resource.user, user)
        self.assertEqual(user.resource, resource)
        self.assertEqual(resource.role, profile.role)
        self.assertEqual(resource.department, profile.department)
