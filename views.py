#implementation of stripe
import stripe
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import View
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

#you can use a cbv or fbv,whichever you choose,i am using cbv here 
class stripe_view(UserPassesTestMixin,View):
    #login_url is the name of the path
    login_url = "account_login"
    
    def test_func(self):
        #this to make sure user is logged in,you can return True for all users
        return self.request.user.is_authenticated
    
    def get(self,request):
        #amount can be whatever you choose but always multiply by 100 cos stripe will divide by it
        amount = self.request.Get.get('amount')
        price = int(amount * 100)
        # domain_url = get_current_site(request)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_id=None
        try:
            product = stripe.Product.create(
                name='Deposit',
                description=f'Deposit of XX currency',
                images=[],
            
            )
            price = stripe.Price.create(
                product=product.id,
                unit_amount=price,
                #currency you want,make sure stripe supports it or use django money to convert it
                currency='usd',
            
            )
            checkout_session = stripe.checkout.Session.create(
                #success urls and cancel urls to do stuff when payment is done and when payment is cancelled
                success_url=request.build_absolute_uri(reverse('name_of_url')),
                cancel_url=request.build_absolute_uri(reverse('name_of_url')),
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'quantity': 1,
                        'price': price.id,
                    }
                ]
            )
            checkout_id = checkout_session["id"]
            
            
        except Exception as e:
            print(e)
            
        #context containing details
        context = {
            "client_id": settings.STRIPE_PUBLISHABLE_KEY,
            "checkout_id": checkout_id
        }
        return render(request,'templates/stripe/stripe.html',context)
    
    
def cancelled(request):
    
    #do something for canelled
    return HttpResponse("it is cancelled")

def success(request):
    #return a response when stripe is sucessful
    
    return HttpResponse("it is success")
    
#stripe webhook for completion
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to handle checkout session completed event.
    """
    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        print(event)
        if event["type"] == "checkout.session.completed":
            print("Payment successful")
            session = event["data"]["object"]
            customer_email = session["customer_details"]["email"]
            product_id = session["metadata"]["product_id"]
            print(session)
            #do stuff when payment is completed with it
            # product = get_object_or_404(Product, id=product_id)
        # Can handle other events here.
