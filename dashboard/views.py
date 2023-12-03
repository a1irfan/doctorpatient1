import stripe
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from stripe.error import StripeError

from dpsystem import settings
from payments.models import SubscriptionProduct, StripeCustomer
from accounts.models import CustomUser,Doctor,Patient
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def doctor_dashboard(request):
    user_id = request.GET.get('user_id')
    user = CustomUser.objects.get(id=user_id)
    record = False
    status = "new"
    doctor_rec = Doctor.objects.get(user_id=user_id)
    if doctor_rec:
        record = True
        status = 'update'
        firstname = doctor_rec.first_name
        lastname = doctor_rec.last_name
        dob = doctor_rec.dob
        refid = doctor_rec.referral_id
        #image = doctor_rec.profile_image
        id = doctor_rec.id
        rec = Patient.objects.filter(doctor_referral_id = refid).count()

        if rec >= 1:
            pat_rec =  Patient.objects.filter(doctor_referral_id = refid)
    subs_rec = StripeCustomer.objects.get(doctor=user_id)
    customer = stripe.Customer.retrieve(subs_rec.stripeCustomerId)
    email = user.email
    username = user.username


    # Retrieve the last 6 payment intents associated with the customer
    payment_intents = stripe.PaymentIntent.list(
        customer=customer.id,
        limit=6,
    )

    transaction_data = [{
        'transaction_id': payment_intent.id,
        'invoice_id': payment_intent.invoice,
        'invoice_amount': payment_intent.amount_received,
        'invoice_status': payment_intent.status,
        'transaction_date': datetime.utcfromtimestamp(payment_intent.created).strftime('%Y-%m-%d %H:%M:%S'),
        # Add other fields as needed
    } for payment_intent in payment_intents.data]
    if record:
        context = {
            'transactions': transaction_data,
            'record': record,
            'firstname' : firstname,
            'lastname' : lastname,
            'dob' :dob,
            'refid' : refid,
            #'image' : image,
            'username': username,
            'email' : email,
            'id': id,
            'status': status,
            #'pat_rec' : pat_rec,
        }
    else:
        context = {
            'transactions': transaction_data,
            'record': record,
            'status' : status,
        }


    return render(request, 'doctor_dashboard.html', context=context)


def patient_dashboard(request):
    return render(request, 'patient_dashboard.html', context={})

def subscription_package(request):
    # Assuming SubscriptionProduct is your model for subscription packages
    user_id = request.GET.get('user_id')
    products = SubscriptionProduct.objects.all()

    # Create a list to store information about all packages
    packages = []

    # Loop through each product and store its information in the packages list
    for product in products:
        package_info = {
            'name': product.product_name,
            'desc': product.product_description,
            'id': product.price_id,
            'price': str(product.product_price)[:2],

        }
        packages.append(package_info)

    context = {
        'packages': packages,
        'user_id': user_id,
    }

    return render(request, 'subscription_package.html', context=context)

