# Generated by Django 4.0.2 on 2022-03-04 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_orderitem_coupon_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='coupon_code',
        ),
        migrations.AddField(
            model_name='order',
            name='coupon_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.coupon'),
        ),
    ]