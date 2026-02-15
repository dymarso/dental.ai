from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.http import HttpResponse
from .models import Agreement
from .serializers import (
    AgreementSerializer,
    AgreementListSerializer,
    SignAgreementSerializer
)


class AgreementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing agreements
    """
    queryset = Agreement.objects.select_related('patient', 'created_by')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'agreement_type', 'status', 'created_by']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['created_at', 'signed_at', 'expires_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgreementListSerializer
        return AgreementSerializer
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Sign an agreement with digital signature"""
        agreement = self.get_object()
        
        if agreement.status == 'signed':
            return Response(
                {'error': 'El acuerdo ya está firmado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SignAgreementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Update agreement
        agreement.signature_data = serializer.validated_data['signature_data']
        agreement.signed_by_name = serializer.validated_data['signed_by_name']
        agreement.signed_at = timezone.now()
        agreement.ip_address = ip
        agreement.status = 'signed'
        agreement.save()
        
        # Generate PDF (optional - can be done asynchronously)
        # self.generate_pdf(agreement)
        
        agreement_serializer = self.get_serializer(agreement)
        return Response(agreement_serializer.data)
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline an agreement"""
        agreement = self.get_object()
        
        if agreement.status == 'signed':
            return Response(
                {'error': 'No se puede rechazar un acuerdo ya firmado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        agreement.status = 'declined'
        agreement.save()
        
        serializer = self.get_serializer(agreement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Download agreement as PDF"""
        agreement = self.get_object()
        
        if not agreement.pdf_file:
            # Generate PDF if it doesn't exist
            pdf_content = self.generate_pdf(agreement)
            return HttpResponse(pdf_content, content_type='application/pdf')
        
        # Return existing PDF file
        return HttpResponse(
            agreement.pdf_file.read(),
            content_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{agreement.title}.pdf"'}
        )
    
    def generate_pdf(self, agreement):
        """
        Generate PDF from agreement
        This is a placeholder - implement with reportlab or weasyprint
        """
        from io import BytesIO
        
        # TODO: Implement PDF generation with reportlab or weasyprint
        # For now, return a simple text representation
        buffer = BytesIO()
        content = f"""
        {agreement.title}
        
        Paciente: {agreement.patient.full_name}
        Tipo: {agreement.get_agreement_type_display()}
        
        {agreement.content}
        
        Firmado por: {agreement.signed_by_name or 'No firmado'}
        Fecha de firma: {agreement.signed_at or 'No firmado'}
        """
        
        buffer.write(content.encode('utf-8'))
        buffer.seek(0)
        
        # Save PDF to model
        from django.core.files.base import ContentFile
        agreement.pdf_file.save(
            f"{agreement.patient.id}_{agreement.id}.pdf",
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        return buffer.getvalue()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending agreements"""
        pending = self.queryset.filter(status='pending')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def signed(self, request):
        """Get all signed agreements"""
        signed = self.queryset.filter(status='signed')
        serializer = self.get_serializer(signed, many=True)
        return Response(serializer.data)
