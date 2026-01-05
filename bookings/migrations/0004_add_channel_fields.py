# Generated migration to add channel integration fields to Booking
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_booking_deleted_at_booking_deleted_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='external_booking_id',
            field=models.CharField(max_length=200, null=True, blank=True, db_index=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='channel_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='channel_reference',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='sync_status',
            field=models.CharField(choices=[('pending','Pending'), ('synced','Synced'), ('failed','Failed')], default='pending', max_length=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='last_synced_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='booking_source',
            field=models.CharField(choices=[('internal','Internal'), ('external','External')], default='internal', max_length=20),
        ),
    ]
