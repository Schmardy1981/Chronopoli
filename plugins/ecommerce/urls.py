from django.urls import path
from . import views

app_name = "chronopoli_ecommerce"

urlpatterns = [
    # Checkout flow
    path("checkout/<str:course_key>/", views.checkout_start, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout-success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout-cancel"),

    # Stripe webhook (no CSRF — Stripe signs the payload)
    path("webhook/stripe/", views.stripe_webhook, name="stripe-webhook"),

    # Subscription management
    path("subscriptions/", views.subscription_list, name="subscriptions"),

    # API
    path("api/pricing/<str:course_key>/", views.api_course_pricing, name="api-pricing"),
]
