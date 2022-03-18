from io import BytesIO
from multiprocessing import context
from weasyprint import HTML, CSS

from django.conf import settings
from django.template.loader import get_template


def generate_pdf(template_path, css_path, instance):
    html_template = get_template(template_path).render({'object': instance})
    stylesheets = [CSS('./' + settings.STATIC_URL + css_path)]
    pdf_file = HTML(string=html_template).write_pdf(None, stylesheets=stylesheets)
    return pdf_file