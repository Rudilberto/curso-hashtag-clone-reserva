# Generated by Django 5.0.4 on 2024-05-16 02:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0007_alter_itenspedido_pedido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itenspedido',
            name='pedido',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='loja.pedido'),
        ),
    ]