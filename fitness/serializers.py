from rest_framework import serializers
from .models import FitnessClass, Booking
import pytz

class FitnessClassSerializer(serializers.ModelSerializer):
    scheduled_time = serializers.SerializerMethodField()

    class Meta:
        model = FitnessClass
        # We’ll expose id, name, instructor, total/available slots, and a converted time
        fields = [
            'id',
            'name',
            'instructor',
            'total_slots',
            'available_slots',
            'scheduled_time',
        ]
        read_only_fields = ['id', 'available_slots']

    def get_scheduled_time(self, obj):
        """
        Convert `start_time` (stored in UTC) to the client’s requested timezone (via ?tz=),
        or default back to IST if none provided / invalid.
        """
        request = self.context.get('request')
        tz_param = None
        if request:
            tz_param = request.query_params.get('tz')
        try:
            if tz_param:
                target_tz = pytz.timezone(tz_param)
            else:
                target_tz = pytz.timezone('Asia/Kolkata')
        except Exception:
            target_tz = pytz.timezone('Asia/Kolkata')
        # obj.start_time is UTC; convert to `target_tz`
        return obj.start_time.astimezone(target_tz).isoformat()


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'fitness_class', 'client_name', 'client_email', 'booked_at']
        read_only_fields = ['id', 'booked_at']

    def validate(self, data):
        """
        Ensure the requested class has slots available.
        """
        fitness_class = data.get('fitness_class')
        if fitness_class is None:
            raise serializers.ValidationError("fitness_class is required.")
        if fitness_class.available_slots <= 0:
            raise serializers.ValidationError("No slots available for this class.")
        return data

    def create(self, validated_data):
        """
        Decrement `available_slots` and create the booking.
        """
        fitness_class = validated_data['fitness_class']
        # Decrement a slot
        fitness_class.available_slots -= 1
        fitness_class.save(update_fields=['available_slots'])
        return super().create(validated_data)
