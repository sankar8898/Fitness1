from datetime import timedelta

from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import FitnessClass, Booking
import pytz
from django.utils import timezone

class BookingAPITestCase(TestCase):
    from datetime import timedelta
    fixtures = ['initial_classes']

    def setUp(self):
        ist = pytz.timezone('Asia/Kolkata')

        # Dynamic future datetime: 1 day from now
        future_utc = timezone.now() + timedelta(days=1)
        dt_ist = future_utc.astimezone(ist).replace(tzinfo=None)
        dt_ist = ist.localize(dt_ist)

        # FitnessClass 1
        self.cls1 = FitnessClass.objects.create(
            name='Yoga',
            instructor='Alice',
            start_time=dt_ist,
            total_slots=5,
            available_slots=5
        )

        # FitnessClass 2 - 2 hours later, no slots
        dt_ist2 = dt_ist + timedelta(hours=2)

        self.cls2 = FitnessClass.objects.create(
            name='Zumba',
            instructor='Bob',
            start_time=dt_ist2,
            total_slots=2,
            available_slots=0
        )

    def test_list_classes_default_tz(self):
        url = reverse('list_classes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 5)
        # Since no ?tz= provided, scheduled_time ends with +05:30
        self.assertTrue(data[0]['scheduled_time'].endswith('+05:30'))

    def test_list_classes_with_tz(self):
        url = reverse('list_classes') + '?tz=America/New_York'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should contain 2 classes (converted to EDT)
        self.assertTrue('T' in data[0]['scheduled_time'])

    def test_successful_booking(self):
        url = reverse('book_class')
        payload = {
            'fitness_class': self.cls1.id,
            'client_name': 'Tester',
            'client_email': 'test@example.com'
        }
        response = self.client.post(url, data=payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # available_slots should decrement
        self.cls1.refresh_from_db()
        self.assertEqual(self.cls1.available_slots, 4)

    def test_overbooking(self):
        url = reverse('book_class')
        payload = {
            'fitness_class': self.cls2.id,
            'client_name': 'Over',
            'client_email': 'over@example.com'
        }
        response = self.client.post(url, data=payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No slots available', response.json().get('non_field_errors', [''])[0])

    def test_list_bookings_by_email(self):
        # Create a booking first
        Booking.objects.create(
            fitness_class=self.cls1,
            client_name='User',
            client_email='user@example.com'
        )
        url = reverse('list_bookings_by_email') + '?email=user@example.com'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)

    def test_list_bookings_missing_email(self):
        url = reverse('list_bookings_by_email')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email query parameter is required.', response.json().get('error'))
