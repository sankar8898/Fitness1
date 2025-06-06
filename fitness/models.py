from django.db import models
import pytz
from django.utils import timezone

class FitnessClass(models.Model):
    CLASS_CHOICES = [
        ('Yoga', 'Yoga'),
        ('Zumba', 'Zumba'),
        ('HIIT', 'HIIT'),
    ]

    name = models.CharField(max_length=20, choices=CLASS_CHOICES)
    instructor = models.CharField(max_length=100)
    # Store naive datetimes as if they are IST; we'll convert to UTC on save
    start_time = models.DateTimeField()
    total_slots = models.PositiveIntegerField(default=0)
    available_slots = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        """
        If `start_time` is naive, treat it as IST and convert to UTC before saving.
        """
        if self.start_time.tzinfo is None:
            ist = pytz.timezone('Asia/Kolkata')
            self.start_time = ist.localize(self.start_time).astimezone(pytz.UTC)
        super().save(*args, **kwargs)

    def __str__(self):
        # Represent in UTC here; serializer will convert for clients
        return f"{self.name} at {self.start_time.isoformat()} with {self.instructor}"


class Booking(models.Model):
    fitness_class = models.ForeignKey(
        FitnessClass, on_delete=models.CASCADE, related_name='bookings'
    )
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} booked {self.fitness_class.name}"
