from django.test import SimpleTestCase
from django.conf import settings
import os


class MediaURLConfigurationTestCase(SimpleTestCase):
    """Test cases for media URL configuration (no database needed)

Note: Django's test runner sets DEBUG=False during tests, so media URLs
won't be served during testing. These tests verify the configuration.
"""

    def test_media_url_code_has_show_indexes(self):
        """Test that the URLs module configures show_indexes=True for media when DEBUG=True"""
        # Read the actual urls.py file to verify the configuration
        urls_file_path = os.path.join(
            os.path.dirname(__file__), 
            'urls.py'
        )

        with open(urls_file_path, 'r') as f:
            urls_content = f.read()

        # Verify that show_indexes is set to True in the code
        self.assertIn("'show_indexes': True", urls_content,
                      "show_indexes should be set to True in urls.py")

        # Verify it's within the DEBUG check
        self.assertIn("if settings.DEBUG:", urls_content,
                      "Media serving should be conditional on DEBUG")

        # Verify we're using django.views.static.serve
        self.assertIn("from django.views.static import serve", urls_content,
                      "Should import serve from django.views.static")

    def test_media_root_configuration(self):
        """Test that MEDIA_ROOT and MEDIA_URL are properly configured"""
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
        self.assertTrue(hasattr(settings, 'MEDIA_URL'))

        # In development, MEDIA_URL should be '/media/'
        # In production with GCS, it will be a GCS URL
        if settings.DEBUG:
            self.assertEqual(settings.MEDIA_URL, '/media/')
        else:
            # In production, MEDIA_URL could be a GCS URL or local fallback
            self.assertTrue(settings.MEDIA_URL.startswith(('http://', 'https://', '/media/')))

    def test_storage_backend_configuration(self):
        """Test that storage backend is correctly configured based on DEBUG setting"""
        if settings.DEBUG:
            # In development, should not use storages app
            self.assertNotIn('storages', settings.INSTALLED_APPS)
        else:
            # In production, storages should be in INSTALLED_APPS
            self.assertIn('storages', settings.INSTALLED_APPS)
            # And STORAGES setting should exist
            self.assertTrue(hasattr(settings, 'STORAGES'))
            