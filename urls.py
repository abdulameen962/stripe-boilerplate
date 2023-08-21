from django.urls import path

from . import views

urlpatterns = [
    # add four paths,one for the stripe view,another for cancelled,sucess and webhook
    path("",views.stripe_view.as_view(),name="stripe_view"),
    path("cancelled/",views.cancelled,name="cancelled"),
    path("success/",views.sucess,name="success"),
    
    path("webhook/stripe/",views.StripeWebhookView.as_view())
]
