from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from booking_api import settings
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer


import logging

logger = logging.getLogger('fitness')

@api_view(['GET'])
def list_classes(request):
    logger.info("GET /classes/ - List requested.")
    now_utc = timezone.now()
    upcoming = FitnessClass.objects.filter(start_time__gte=now_utc).order_by('start_time')
    logger.info(f"{upcoming.count()} upcoming classes found.")
    serializer = FitnessClassSerializer(upcoming, many=True, context={'request': request})
    return Response(serializer.data)



@api_view(['POST'])
def book_class(request):
    """
    POST /book/
    - Validates if slots are available.
    - Creates booking, decrements slot count.
    - Sends confirmation email to client.
    """
    logger.info("Booking request received: %s", request.data)

    serializer = BookingSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Invalid booking data: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    booking = serializer.save()
    logger.info("Booking created successfully for class ID %s", booking.fitness_class.id)

    # Email content
    subject = f"Booking Confirmation for {booking.fitness_class.name}"
    message = (
        f"Hello {booking.client_name},\n\n"
        f"You have successfully booked a spot in the '{booking.fitness_class.name}' class.\n"
        f"Instructor: {booking.fitness_class.instructor}\n"
        f"Time: {booking.fitness_class.start_time.strftime('%Y-%m-%d %H:%M %Z')}\n\n"
        f"Thank you for booking with Fitness Studio!"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.client_email],
            fail_silently=False,
        )
        logger.info("Confirmation email sent to %s", booking.client_email)
    except Exception as e:
        logger.error("Failed to send email to %s: %s", booking.client_email, str(e))

    return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_bookings_by_email(request):
    email = request.query_params.get('email')
    if not email:
        logger.warning("GET /bookings/ - Missing email parameter.")
        return Response(
            {"error": "Email query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    bookings = Booking.objects.filter(client_email=email).order_by('-booked_at')
    logger.info(f"{bookings.count()} bookings found for email {email}")
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
