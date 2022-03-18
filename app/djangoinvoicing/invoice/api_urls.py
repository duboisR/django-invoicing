from django.urls import path

import invoice.api_views

urlpatterns = [
    # Customer views
    path('customer/infos/', invoice.api_views.customer_infos),

    # Product views
    path('product/infos/', invoice.api_views.product_infos),
]
