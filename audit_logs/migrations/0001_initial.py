from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('module', models.CharField(max_length=100)),
                ('object_pk', models.CharField(max_length=255)),
                ('action', models.CharField(max_length=50)),
                ('field_name', models.CharField(max_length=100, blank=True)),
                ('old_value', models.TextField(blank=True)),
                ('new_value', models.TextField(blank=True)),
                ('channel', models.CharField(max_length=100, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
