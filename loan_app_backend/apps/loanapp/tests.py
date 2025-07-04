from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from loan_app_backend.apps.loanapp.models import LoanApplication, FraudFlag, Users
import uuid


class LoanApplicationTest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(
            username=f'user_{uuid.uuid4().hex[:8]}',
            email='testuser@example.com',
            password='pass1234'
        )
        self.client.login(email='testuser@example.com', password='pass1234')
        self.url = reverse('loan-application')

    def test_successful_loan_application(self):
        payload = {
            "amount_requested": 200000,
            "purpose": "Business expansion"
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(LoanApplication.objects.count(), 1)
        self.assertEqual(FraudFlag.objects.count(), 0)

    def test_flagged_due_to_multiple_loans(self):
        # Create 3 existing loans within the past 24 hours
        for _ in range(3):
            LoanApplication.objects.create(user=self.user, amount_requested=100000, purpose="Test", created_at=timezone.now())

        payload = {
            "amount_requested": 500000,
            "purpose": "Another business"
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 201)
        flagged_loan = LoanApplication.objects.latest('created_at')
        self.assertEqual(flagged_loan.status, 'flagged')
        self.assertTrue(FraudFlag.objects.filter(loan_application=flagged_loan).exists())

    def test_flagged_due_to_high_amount(self):
        payload = {
            "amount_requested": 6000000,  # > 5 million
            "purpose": "Expensive equipment"
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 201)
        loan = LoanApplication.objects.latest('created_at')
        self.assertEqual(loan.status, 'flagged')
        self.assertTrue(FraudFlag.objects.filter(loan_application=loan, reason__icontains="Amount exceeds NGN 5,000,000").exists())

    def test_flagged_due_to_shared_email_domain(self):
        # Create 11 users with the same domain
        for i in range(11):
            Users.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="test1234"
            )

        self.user.email = "special@example.com"
        self.user.save()

        payload = {
            "amount_requested": 100000,
            "purpose": "Normal test"
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 201)
        loan = LoanApplication.objects.latest('created_at')
        self.assertEqual(loan.status, 'flagged')
        self.assertTrue(FraudFlag.objects.filter(loan_application=loan, reason__icontains="Email domain").exists())
