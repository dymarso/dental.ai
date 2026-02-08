from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, AppointmentReminder
from .serializers import AppointmentSerializer, AppointmentReminderSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments
    """
    queryset = Appointment.objects.select_related('patient')
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'status', 'consultation_type', 'date']
    search_fields = ['patient__first_name', 'patient__last_name', 'notes']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments"""
        today = timezone.now().date()
        appointments = self.queryset.filter(date=today)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def week(self, request):
        """Get this week's appointments"""
        today = timezone.now().date()
        week_end = today + timedelta(days=7)
        appointments = self.queryset.filter(date__gte=today, date__lte=week_end)
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def month(self, request):
        """Get this month's appointments"""
        today = timezone.now().date()
        appointments = self.queryset.filter(
            date__year=today.year,
            date__month=today.month
        )
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
