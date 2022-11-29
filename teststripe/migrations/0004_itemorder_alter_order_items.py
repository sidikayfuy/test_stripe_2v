# Generated by Django 4.1.3 on 2022-11-28 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teststripe', '0003_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teststripe.item')),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='teststripe.itemorder'),
        ),
    ]