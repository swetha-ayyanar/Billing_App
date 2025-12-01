from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import tempfile
from billing_app import templates

@shared_task
def send_invoice_email(bill_id, to_email):
    from .models import Bill
    bill = Bill.objects.get(id=bill_id)
    # render invoice template
    html = render_to_string('billing_app/invoice.html', {'bill': bill})


    # convert to PDF (optional) - using weasyprint if installed
    try:
        from weasyprint import HTML
        fp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        HTML(string=html).write_pdf(fp.name)
        email = EmailMessage(subject=f"Invoice #{bill.id}", body="Please find the invoice attached.", from_email=settings.DEFAULT_FROM_EMAIL, to=[to_email])
        email.attach_file(fp.name)
        email.send()
    except Exception as e:
        # fallback to sending HTML email without attachment
        print(e)
        email = EmailMessage(subject=f"Invoice #{bill.id}", body=html, from_email=settings.DEFAULT_FROM_EMAIL, to=[to_email])
        email.content_subtype = 'html'
        email.send()