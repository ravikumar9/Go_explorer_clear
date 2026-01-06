from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Payment, Invoice


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'payment_method', 'status', 'transaction_date', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['booking__booking_id', 'transaction_id', 'gateway_payment_id']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['export_as_csv']
    
    fieldsets = (
        ('Booking & Amount', {
            'fields': ('booking', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status', 'transaction_id', 'transaction_date')
        }),
        ('Gateway Details', {
            'fields': ('gateway_payment_id', 'gateway_order_id', 'gateway_signature', 'gateway_response')
        }),
        ('Refund', {
            'fields': ('refund_id', 'refund_amount', 'refund_date')
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make financial/editable fields readonly for non-superusers."""
        ro = list(self.readonly_fields)
        if not request.user.is_superuser:
            # prevent editing payment amounts and gateway details by regular staff
            ro += ['amount', 'currency', 'payment_method', 'status', 'transaction_id', 'gateway_payment_id', 'gateway_order_id', 'gateway_signature', 'gateway_response', 'refund_id', 'refund_amount']
        return ro

    def export_as_csv(self, request, queryset):
        """Export selected payments to CSV"""
        field_names = ['booking_id', 'amount', 'currency', 'payment_method', 'status', 'transaction_id', 'transaction_date', 'gateway_payment_id', 'refund_id']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=payments_export.csv'

        writer = csv.writer(response)
        writer.writerow(field_names)
        for p in queryset.select_related('booking'):
            writer.writerow([
                str(p.booking.booking_id) if p.booking else '',
                f"{p.amount}",
                p.currency,
                p.payment_method,
                p.status,
                p.transaction_id,
                p.transaction_date.strftime('%Y-%m-%d %H:%M') if p.transaction_date else '',
                p.gateway_payment_id,
                p.refund_id,
            ])

        return response
    export_as_csv.short_description = "Export selected payments to CSV"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'booking', 'billing_name', 'total_amount', 'invoice_date']
    list_filter = ['invoice_date']
    search_fields = ['invoice_number', 'booking__booking_id', 'billing_name', 'billing_email']
    readonly_fields = ['invoice_number', 'invoice_date']
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('invoice_number', 'invoice_date', 'booking')
        }),
        ('Billing Information', {
            'fields': ('billing_name', 'billing_email', 'billing_phone', 'billing_address')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Tax Details', {
            'fields': ('cgst', 'sgst', 'igst')
        }),
        ('PDF', {
            'fields': ('pdf_file',)
        }),
    )
