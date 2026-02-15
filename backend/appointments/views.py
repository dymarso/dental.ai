from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta, datetime, date
from .models import Appointment, AppointmentReminder
from .serializers import AppointmentSerializer, AppointmentReminderSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments
    """
    queryset = Appointment.objects.select_related('patient')
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'status', 'consultation_type', 'date', 'telemedicine_enabled', 'public_booking']
    search_fields = ['patient__first_name', 'patient__last_name', 'notes']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']
    
    def perform_create(self, serializer):
        """Set created_by when creating appointment"""
        created_by = None
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            created_by = self.request.user.username
        serializer.save(created_by=created_by)
    
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
    
    @action(detail=False, methods=['get'])
    def agenda(self, request):
        """Get agenda view (daily or weekly)"""
        view_type = request.query_params.get('view', 'daily')  # 'daily' or 'weekly'
        date_str = request.query_params.get('date', None)
        
        # Parse date or use today
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = timezone.now().date()
        
        if view_type == 'daily':
            # Daily agenda
            appointments = self.queryset.filter(date=target_date)
            return Response({
                'view': 'daily',
                'date': target_date,
                'appointments': AppointmentSerializer(appointments, many=True).data
            })
        
        elif view_type == 'weekly':
            # Weekly agenda - get the week containing target_date
            week_start = target_date - timedelta(days=target_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            appointments = self.queryset.filter(
                date__gte=week_start,
                date__lte=week_end
            )
            
            # Group by day
            days_data = {}
            for i in range(7):
                day = week_start + timedelta(days=i)
                day_appointments = [a for a in appointments if a.date == day]
                days_data[day.strftime('%Y-%m-%d')] = {
                    'date': day,
                    'day_name': day.strftime('%A'),
                    'appointments': AppointmentSerializer(day_appointments, many=True).data
                }
            
            return Response({
                'view': 'weekly',
                'week_start': week_start,
                'week_end': week_end,
                'days': days_data
            })
        
        else:
            return Response(
                {'error': 'Tipo de vista inválido. Use "daily" o "weekly"'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get', 'post'])
    def public_booking(self, request):
        """Public booking endpoint for patients to book appointments"""
        if request.method == 'GET':
            # Return available slots for booking
            date_str = request.query_params.get('date', None)
            
            if not date_str:
                return Response(
                    {'error': 'Parámetro "date" requerido (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get existing appointments for the day
            existing_appointments = self.queryset.filter(
                date=target_date,
                status__in=['pending', 'confirmed']
            )
            
            # Generate available slots (8 AM to 8 PM, 30-minute intervals)
            from datetime import time
            available_slots = []
            current_time = time(8, 0)
            end_time = time(20, 0)
            
            while current_time < end_time:
                # Calculate slot end time (30 minutes later)
                slot_end_hour = current_time.hour
                slot_end_minute = current_time.minute + 30
                if slot_end_minute >= 60:
                    slot_end_hour += 1
                    slot_end_minute -= 60
                slot_end = time(slot_end_hour, slot_end_minute)
                
                # Check if slot is available
                is_available = True
                for appt in existing_appointments:
                    if (current_time < appt.end_time and slot_end > appt.start_time):
                        is_available = False
                        break
                
                available_slots.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M'),
                    'available': is_available
                })
                
                # Move to next slot
                current_time = slot_end
            
            return Response({
                'date': target_date,
                'slots': available_slots
            })
        
        elif request.method == 'POST':
            # Create a public booking
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(public_booking=True, created_by='public')
            
            return Response(
                {
                    'message': 'Cita reservada exitosamente',
                    'appointment': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
