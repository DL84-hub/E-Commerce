from django.db import migrations, models
import django.utils.timezone
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='email_verification_token',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='email_verification_token_created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ] 