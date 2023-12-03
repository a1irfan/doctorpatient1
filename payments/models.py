from django.db import models
from accounts.models import CustomUser


class SubscriptionProduct(models.Model):
    product_name = models.CharField(max_length=255)
    product_description = models.TextField()
    product_price = models.IntegerField()  # Price in cents
    product_id = models.CharField(max_length=255)  # Stripe product ID
    price_id = models.CharField(max_length=255)  # Stripe price ID

    def __str__(self):
        return self.product_name

class StripeCustomer(models.Model):
    doctor = models.IntegerField(null=False, max_length=5)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255)

    class Meta:
        db_table = 'stripe_customer'
    def __str__(self):
        return self.stripeCustomerId