from django.test import TestCase
from rest_framework.test import APIClient


class AuthRefreshTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_invalid_refresh_token_returns_bad_request(self):
        response = self.client.post("/api/auth/refresh", {"refresh": "bad-token"}, format="json")

        self.assertEqual(response.status_code, 400, getattr(response, "data", None))
        self.assertIn("refresh", response.data)
