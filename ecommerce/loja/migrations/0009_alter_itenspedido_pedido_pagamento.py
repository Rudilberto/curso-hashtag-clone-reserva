# Generated by Django 5.0.4 on 2024-05-22 23:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0008_alter_itenspedido_pedido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itenspedido',
            name='pedido',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.pedido'),
        ),
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_pagamento', models.CharField(blank=True, max_length=400, null=True)),
                ('pedido', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='loja.pedido')),
            ],
        ),
    ]
