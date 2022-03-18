from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils.translation import gettext_lazy as _

import invoice.models
import invoice.commons


# Quote views
def quote_to_invoice(request, pk):
    """Custom views.
    This view was created to generate Invoice from quote information
    """
    if pk and request.user.is_authenticated:
        try:
            quote_instance = invoice.models.Quote.objects.get(pk=pk)
            invoice_instance = invoice.models.Invoice.objects.create(
                quote=quote_instance,
                discount=quote_instance.discount,
                customer=quote_instance.customer,
                company_name=quote_instance.company_name,
                company_vat=quote_instance.company_vat,
                contact_first_name=quote_instance.contact_first_name,
                contact_last_name=quote_instance.contact_last_name,
                contact_email=quote_instance.contact_email,
                contact_phone=quote_instance.contact_phone,
                address_street=quote_instance.address_street,
                address_street_number=quote_instance.address_street_number,
                address_bp=quote_instance.address_bp,
                address_zipcode=quote_instance.address_zipcode,
                address_city=quote_instance.address_city,
            )
            for quoteitem_instance in quote_instance.quoteitem_set.all():
                invoice.models.InvoiceItem.objects.create(
                    invoice=invoice_instance,
                    product=quoteitem_instance.product,
                    product_description=quoteitem_instance.product_description,
                    product_quantity=quoteitem_instance.product_quantity,
                    product_vat=quoteitem_instance.product_vat,
                    product_price=quoteitem_instance.product_price,
                )
            messages.add_message(request, messages.SUCCESS, _("La facture a bien été générée."))
            url = reverse('admin:invoice_invoice_change',  args=[invoice_instance.pk])
            return HttpResponseRedirect(url)
        except:
            pass
    messages.add_message(request, messages.ERROR, _("Impossible de générer la facture."))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def quote_preview_pdf(request, pk):
    """ This view returns a preview of our PDF file for a given quote
    """
    # we get the selected item to use as the "object" context to be able to have some mockup data
    quote_instance = invoice.models.Quote.objects.get(pk=pk)
    quote_pdf_name = "quote-%s.pdf" % str(quote_instance)
    default_storage.delete(quote_pdf_name)
    quote_pdf = invoice.commons.generate_pdf('pdf/quote.html', 'css/invoice.css', quote_instance)
    quote_instance.quote_pdf = ContentFile(quote_pdf, quote_pdf_name)
    quote_instance.save()

    # Find previous/next urls
    previous_url = None
    previous_instance = invoice.models.Quote.objects.filter(pk__lt=pk).last()
    if previous_instance:
        previous_url = reverse('quote_preview_pdf', args=[previous_instance.pk])
    next_url = None
    next_intance = invoice.models.Quote.objects.filter(pk__gt=pk).first()
    if next_intance:
        next_url = reverse('quote_preview_pdf', args=[next_intance.pk])

    # GET
    context = dict(
        paginator={
            'previous_url': previous_url,
            'next_url': next_url,
        },
        target_instance=quote_instance,
        detail_url=reverse('admin:invoice_quote_change', args=[quote_instance.pk]),
        iframe_url=quote_instance.quote_pdf.url if quote_instance.quote_pdf else '',
        opts=invoice.models.Quote._meta,
    )
    return render(request, 'invoice/preview_pdf.html', context)


# Invoice views
def invoice_preview_pdf(request, pk):
    """ This view returns a preview of our PDF file for a given invoice
    """
    # we get the selected item to use as the "object" context to be able to have some mockup data
    invoice_instance = invoice.models.Invoice.objects.get(pk=pk)
    invoice_pdf_name = "invoice-%s.pdf" % str(invoice_instance)
    default_storage.delete(invoice_pdf_name)
    invoice_pdf = invoice.commons.generate_pdf('pdf/invoice.html', 'css/invoice.css', invoice_instance)
    invoice_instance.invoice_pdf = ContentFile(invoice_pdf, invoice_pdf_name)
    invoice_instance.save()

    # Find previous/next urls
    previous_url = None
    previous_instance = invoice.models.Invoice.objects.filter(pk__lt=pk).last()
    if previous_instance:
        previous_url = reverse('invoice_preview_pdf', args=[previous_instance.pk])
    next_url = None
    next_instance = invoice.models.Invoice.objects.filter(pk__gt=pk).first()
    if next_instance:
        next_url = reverse('invoice_preview_pdf', args=[next_instance.pk])

    # GET
    context = dict(
        paginator={
            'previous_url': previous_url,
            'next_url': next_url,
        },
        target_instance=invoice_instance,
        detail_url=reverse('admin:invoice_invoice_change', args=[invoice_instance.pk]),
        iframe_url=invoice_instance.invoice_pdf.url if invoice_instance.invoice_pdf else '',
        opts=invoice.models.Invoice._meta,
    )
    return render(request, 'invoice/preview_pdf.html', context)