# Generated by Django 4.1.3 on 2022-11-29 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teststripe', '0005_discount_tax_promocode'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='promocode',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teststripe.promocode'),
        ),
    ]
