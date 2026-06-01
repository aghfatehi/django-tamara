from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="TamaraTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tamara_order_id", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("tamara_checkout_id", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("order_reference_id", models.CharField(blank=True, max_length=255, null=True)),
                ("order_number", models.CharField(blank=True, max_length=255, null=True)),
                ("amount", models.DecimalField(decimal_places=3, default=0, max_digits=20)),
                ("currency", models.CharField(default="SAR", max_length=3)),
                ("status", models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ("payment_type", models.CharField(blank=True, max_length=50, null=True)),
                ("request_payload", models.JSONField(blank=True, null=True)),
                ("response_payload", models.JSONField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("object_id", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=models.SET_NULL, to="contenttypes.ContentType"
                    ),
                ),
            ],
            options={
                "db_table": "tamara_transactions",
                "ordering": ["-created_at"],
                "verbose_name": "Tamara Transaction",
                "verbose_name_plural": "Tamara Transactions",
            },
        ),
    ]
