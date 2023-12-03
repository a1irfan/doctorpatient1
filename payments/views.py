# views.py
import jwt
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from stripe.error import StripeError

from .models import SubscriptionProduct, StripeCustomer
from dpsystem import settings
import stripe
from rest_framework.decorators import api_view
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def CreateSubscriptionProductView(request):
        product_name = request.data.get('product_name')
        product_description = request.data.get('product_description')
        product_price = request.data.get('product_price')  # Price in cents
        currency = request.data.get('currency')  # Change this to your desired currency code
        interval = request.data.get('period')  # Change this to 'year' for yearly subscriptions

        try:
            product = stripe.Product.create(
                name=product_name,
                description=product_description,
                type='service',
            )
            print("========PRODUCT========")
            print(product)
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(product_price),
                currency=currency,
                recurring={
                    'interval': interval,
                },

            )
            print("========PRICE========")
            print(price)

            subscription_product = SubscriptionProduct.objects.create(
                product_name=product_name,
                product_description=product_description,
                product_price=int(product_price),
                product_id=product.id,
                price_id=price.id,
            )

            return JsonResponse({'success': True, 'product_id': subscription_product.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def CreateCustomerSubscription(request):
    print("Yes inside here")
    try:

            price_id = request.GET.get('price_id')
            doctor_id = request.GET.get('user_id')
            print(price_id)
            print(doctor_id)
            print("YES TYES YES")
            user_data = CustomUser.objects.get(id=doctor_id)
            print(user_data)
            email = user_data.email
            username = user_data.username

            customer = stripe.Customer.create(
                email=email,
                name=username,
            )
            print("Customer Created Successfully")
            print(customer)

            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{
                    'price': price_id,
                }],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )

            StripeCustomer.objects.create(
                doctor=int(doctor_id),
                stripeCustomerId=customer.id,
                stripeSubscriptionId=subscription.id,
            )

            stripe_config = {'clientsecret': subscription.latest_invoice.payment_intent.client_secret}
            return JsonResponse(stripe_config, safe=False)

    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

def checkout_session(request):
        user_id = request.GET.get('user_id')
        price_id = request.GET.get('price_id')
        product = SubscriptionProduct.objects.get(price_id=price_id)
        user = CustomUser.objects.get(id=user_id)
        print(settings.STRIPE_PUBLIC_KEY)

        # You can add additional logic here based on the price_id

        context = {
            'price_id': price_id,
            'username': user.username,
            'email': user.email,
            'pro_name': product.product_name,
            'pro_price': str(product.product_price)[:2],
            'user_id': user.id,
            'pkey': settings.STRIPE_PUBLIC_KEY,
            # Add any other context variables you need for the checkout page
        }

        return render(request, 'checkout.html', context=context)


