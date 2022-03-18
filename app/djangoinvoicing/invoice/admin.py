from django import forms
from django.contrib import admin, messages
from django.shortcuts import reverse
from django.utils.translation import ngettext
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

import invoice.filters
import invoice.models


# Customer
class CustomerAddressInline(admin.StackedInline):
    model = invoice.models.CustomerAddress
    extra = 0
    min_num = 1
    classes = ['collapse']

    fields = (
        ('address_street', 'address_street_number', 'address_bp', ),
        ('address_zipcode', 'address_city', ),
    )


@admin.register(invoice.models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    model = invoice.models.Customer
    list_display = ('__str__', 'contact_email', 'contact_phone', 'get_invoice_link', )
    search_fields = ('company_name', 'company_vat', 'contact_first_name', 'contact_last_name', 'contact_email', 'contact_phone', )
    list_filter = (invoice.filters.CustomerTypeFilter, )

    fieldsets = (
        (_("Société"), {'fields': (
            ('company_name', 'company_vat', ),
        )}),
        (_("Contact"), {'fields': (
            ('contact_first_name', 'contact_last_name', ),
            'contact_email', 'contact_phone',
        )}),
    )
    inlines = [CustomerAddressInline, ]

    def get_invoice_link(self, obj):
        url = reverse('admin:invoice_invoice_changelist')
        return mark_safe("<a href='%s?customer__id__exact=%s'>Factures</a>" % (url, str(obj.pk)))
    get_invoice_link.short_description = _("Factures")


# Product
@admin.register(invoice.models.Product)
class ProductAdmin(admin.ModelAdmin):
    model = invoice.models.Product
    list_display = ('__str__', 'vat', 'price', )
    search_fields = ('description', 'vat', )
    readonly_fields = ('vat', )


# Quote
class QuoteItemInline(admin.TabularInline):
    model = invoice.models.QuoteItem
    verbose_name = _("Produit")
    verbose_name_plural = _("Produits")
    extra = 0
    readonly_fields = ('product_vat', )
    autocomplete_fields = ['product', ]


@admin.register(invoice.models.Quote)
class QuoteAdmin(admin.ModelAdmin):
    model = invoice.models.Quote

    list_display = ('quote_number', 'quote_date', 'get_customer', 'get_address', 'get_total', )
    search_fields = ('quote_number', )
    list_filter = ('customer', )
    date_hierarchy = 'quote_date'
    actions = ['set_done', 'set_wainting']

    autocomplete_fields = ['customer', ]
    fieldsets = (
        (_("Client"), {'fields': (
            ('customer', ),
        )}),
        (_("Société"), {'fields': (
            ('company_name', 'company_vat', ),
        )}),
        (_("Contact"), {'fields': (
            ('contact_first_name', 'contact_last_name', ),
            'contact_email', 'contact_phone', 
        )}),
        (_("Adresse"), {'fields': (
            ('address_street', 'address_street_number', 'address_bp', ),
            ('address_zipcode', 'address_city', ),
        )}),
        (_("Devis"), {'fields': (
            'quote_number', 'quote_date', 'discount', 'quote_pdf', ),
        }),
    )
    inlines = [QuoteItemInline, ]


# Invoice
class InvoiceAdminForm(forms.ModelForm):
    ref_number_warning = forms.BooleanField(
        label=_("Vous êtes sur le point de modifier la numérotation de ce devis. Afin d’éviter toutes erreurs, veuillez valider votre choix"),
        initial=True, required=True)

    class Meta:
        model = invoice.models.Invoice
        fields = '__all__'


class InvoiceItemInline(admin.TabularInline):
    model = invoice.models.InvoiceItem
    verbose_name = _("Produit")
    verbose_name_plural = _("Produits")
    extra = 0
    readonly_fields = ('product_vat', )
    autocomplete_fields = ['product', ]


@admin.register(invoice.models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    model = invoice.models.Invoice

    list_display = ('invoice_number', 'invoice_date', 'get_customer', 'get_address', 'get_total', 'get_deadline_date', 'invoice_status', )
    search_fields = ('invoice_number', )
    list_filter = ('customer', 'invoice_status', )
    date_hierarchy = 'invoice_date'
    actions = ['set_done', 'set_wainting']

    form = InvoiceAdminForm
    autocomplete_fields = ['customer', ]
    fieldsets = (
        (_("Client"), {'fields': (
            ('customer', ),
        )}),
        (_("Société"), {'fields': (
            ('company_name', 'company_vat', ),
        )}),
        (_("Contact"), {'fields': (
            ('contact_first_name', 'contact_last_name', ),
            'contact_email', 'contact_phone', 
        )}),
        (_("Adresse"), {'fields': (
            ('address_street', 'address_street_number', 'address_bp', ),
            ('address_zipcode', 'address_city', ),
        )}),
        (_("Facturation"), {'fields': (
            ('invoice_number', 'invoice_status', ),
            'ref_number_warning',  # cf. InvoiceAdminForm
            'invoice_date', 'terms_payment', 'discount', ),
        }),
    )
    inlines = [InvoiceItemInline, ]

    @admin.action(description="Marquer les factures sélectionnées comme 'Payées'")
    def set_done(self, request, queryset):
        updated = queryset.update(invoice_status='done')
        self.message_user(request, ngettext(
            "%d facture a bien été passée à 'Payée'.",
            "%d factures ont bien été passées à 'Payée'.",
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Marquer les factures sélectionnées comme 'En cours'")
    def set_wainting(self, request, queryset):
        updated = queryset.update(invoice_status='waiting')
        self.message_user(request, ngettext(
            "%d facture a bien été passée à 'En cours'.",
            "%d factures ont bien été passées à 'En cours'.",
            updated,
        ) % updated, messages.SUCCESS)
