from django.db import models


class TamaraTransaction(models.Model):
    tamara_order_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    tamara_checkout_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    order_reference_id = models.CharField(max_length=255, null=True, blank=True)
    order_number = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=3, default=0)
    currency = models.CharField(max_length=3, default="SAR")
    status = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    payment_type = models.CharField(max_length=50, null=True, blank=True)
    request_payload = models.JSONField(null=True, blank=True)
    response_payload = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tamara_transactions"
        verbose_name = "Tamara Transaction"
        verbose_name_plural = "Tamara Transactions"
        ordering = ["-created_at"]

    def __str__(self):
        order = self.tamara_order_id or self.order_reference_id or "N/A"
        return f"{order} | {self.currency} {self.amount} | {self.status or 'unknown'}"
