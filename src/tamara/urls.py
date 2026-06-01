from django.urls import path

from tamara.views import (
    AuthoriseView,
    CallbackView,
    CancelView,
    FailureView,
    PaymentTypesView,
    PayView,
    WebhookView,
)

app_name = "tamara"

urlpatterns = [
    path("payment/types", PaymentTypesView.as_view(), name="payment_types"),
    path("pay", PayView.as_view(), name="pay"),
    path("callback", CallbackView.as_view(), name="callback"),
    path("cancel", CancelView.as_view(), name="cancel"),
    path("failure", FailureView.as_view(), name="failure"),
    path("webhook", WebhookView.as_view(), name="webhook"),
    path("authorise", AuthoriseView.as_view(), name="authorise"),
]
