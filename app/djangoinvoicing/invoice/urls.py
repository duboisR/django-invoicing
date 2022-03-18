from django.urls import path, include

import invoice.views

quote_urlpatterns = [
    path('<int:pk>/generate-invoice/', invoice.views.quote_to_invoice, name="quote_to_invoice"),
    path('<int:pk>/preview-pdf/', invoice.views.quote_preview_pdf, name="quote_preview_pdf"),
]

invoice_urlpatterns = [
    path('<int:pk>/preview-pdf/', invoice.views.invoice_preview_pdf, name="invoice_preview_pdf"),
]

urlpatterns = [
    path('quote/', include(quote_urlpatterns)),
    path('invoice/', include(invoice_urlpatterns)),
]
