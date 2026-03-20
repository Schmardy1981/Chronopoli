import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CoursePricingTier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course_key", models.CharField(help_text="OpenEdX course key", max_length=255, unique=True)),
                ("layer", models.CharField(choices=[("L1", "Entry"), ("L2", "Professional"), ("L3", "Advanced Practitioner"), ("L4", "Live Cohort")], default="L1", max_length=5)),
                ("price_usd", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("stripe_price_id", models.CharField(blank=True, max_length=100)),
                ("is_free", models.BooleanField(default=True)),
                ("district_code", models.CharField(blank=True, max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Course Pricing Tier", "verbose_name_plural": "Course Pricing Tiers", "ordering": ["layer", "course_key"]},
        ),
        migrations.CreateModel(
            name="TeamSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("organization_name", models.CharField(max_length=200)),
                ("contact_email", models.EmailField(max_length=254)),
                ("partner_slug", models.CharField(blank=True, max_length=100)),
                ("stripe_customer_id", models.CharField(max_length=100, unique=True)),
                ("stripe_subscription_id", models.CharField(max_length=100, unique=True)),
                ("seats", models.IntegerField(default=10)),
                ("seats_used", models.IntegerField(default=0)),
                ("price_per_seat_usd", models.DecimalField(decimal_places=2, default=125, max_digits=8)),
                ("status", models.CharField(choices=[("active", "Active"), ("past_due", "Past Due"), ("canceled", "Canceled"), ("trialing", "Trialing"), ("unpaid", "Unpaid")], default="active", max_length=20)),
                ("current_period_start", models.DateTimeField(blank=True, null=True)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Team Subscription", "verbose_name_plural": "Team Subscriptions", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PartnerPayout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("partner_slug", models.CharField(max_length=100)),
                ("stripe_transfer_id", models.CharField(blank=True, max_length=100, unique=True)),
                ("stripe_connect_account_id", models.CharField(max_length=100)),
                ("course_key", models.CharField(max_length=255)),
                ("buyer_email", models.EmailField(max_length=254)),
                ("total_amount_usd", models.DecimalField(decimal_places=2, max_digits=10)),
                ("partner_share_usd", models.DecimalField(decimal_places=2, max_digits=10)),
                ("platform_share_usd", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "Partner Payout", "verbose_name_plural": "Partner Payouts", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="StripeWebhookEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_event_id", models.CharField(max_length=100, unique=True)),
                ("event_type", models.CharField(max_length=100)),
                ("processed", models.BooleanField(default=False)),
                ("payload", models.JSONField(default=dict)),
                ("error_message", models.TextField(blank=True)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "Stripe Webhook Event", "verbose_name_plural": "Stripe Webhook Events", "ordering": ["-received_at"]},
        ),
        migrations.CreateModel(
            name="Purchase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course_key", models.CharField(max_length=255)),
                ("stripe_checkout_session_id", models.CharField(blank=True, max_length=200)),
                ("stripe_payment_intent_id", models.CharField(blank=True, max_length=200)),
                ("amount_usd", models.DecimalField(decimal_places=2, max_digits=8)),
                ("status", models.CharField(choices=[("pending", "Pending Payment"), ("completed", "Completed"), ("refunded", "Refunded"), ("failed", "Failed")], default="pending", max_length=20)),
                ("enrolled", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chronopoli_purchases", to=settings.AUTH_USER_MODEL)),
                ("pricing_tier", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="chronopoli_ecommerce.coursepricingtier")),
            ],
            options={"verbose_name": "Course Purchase", "verbose_name_plural": "Course Purchases", "ordering": ["-created_at"], "unique_together": {("user", "course_key")}},
        ),
    ]
