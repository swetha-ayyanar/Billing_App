from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Product, Bill, BillItem, DenominationMaster, BillDenomination, ReturnDenomination
from .tasks import send_invoice_email
from django.template.loader import render_to_string
from billing_app import templates

@transaction.atomic
def generate_bill(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Expected POST')


    data = json.loads(request.body.decode('utf-8'))
    customer_email = data.get('customer_email')
    amount_paid = float(data.get('amount_paid', 0))
    product_rows = data.get('products', [])
    given_denominations = data.get('denominations', {})


    items = []
    total = 0.0


    # validate and compute
    for row in product_rows:
        pid = row.get('product_id')
        qty = int(row.get('quantity', 0))
        try:
            product = Product.objects.select_for_update().get(product_id=pid)
        except Product.DoesNotExist:
            transaction.set_rollback(True)
            return JsonResponse({'error': f'Product {pid} not found'}, status=400)
        if product.available_stocks < qty:
            transaction.set_rollback(True)
            return JsonResponse({'error': f'Insufficient stock for {pid}'}, status=400)


        item_base = product.price_per_unit * qty
        item_tax = item_base * (product.tax_percentage / 100)
        item_total = int(item_base) + int(item_tax)
        items.append({'product': product, 'qty': qty, 'price': item_base, 'tax': item_tax, 'total': item_total})
        total += item_total


    balance = round(amount_paid - total, 2)
    if balance < 0:
        return JsonResponse({'error': 'Amount paid is less than bill total', 'total': total}, status=400)


    # Save Bill
    bill = Bill.objects.create(customer_email=customer_email, total_amount=total, amount_paid=amount_paid, balance_amount=balance)


    # Save items and deduct stock
    for it in items:
        BillItem.objects.create(bill=bill, product=it['product'], quantity=it['qty'], price=it['price'], tax=it['tax'], total=it['total'])
        p = it['product']
        p.available_stocks -= it['qty']
        p.save()

    # Save given denominations
    for val_str, cnt in given_denominations.items():
        try:
            val = int(val_str)
            c = int(cnt)
            if c > 0:
                BillDenomination.objects.create(bill=bill, denomination_value=val, count=c)
        except ValueError:
            continue


    # compute return denominations
    denominations = list(DenominationMaster.objects.order_by('-value').values_list('value', flat=True))
    change = int(round(balance)) # assume denominations are integer rupee values
    return_breakdown = []
    remaining = change
    for d in denominations:
        if remaining <= 0:
            break
        cnt = remaining // d
        if cnt > 0:
            ReturnDenomination.objects.create(bill=bill, denomination_value=d, count=cnt)
            return_breakdown.append({'denomination': d, 'count': cnt})
            remaining -= d * cnt


    # send invoice async
    # send_invoice_email(bill.id, customer_email)


    # prepare response (bill summary URL)
    invoice_html = render_to_string('billing_app/invoice.html', {'bill': bill})
    return JsonResponse({'bill_id': bill.id, 'invoice_html': invoice_html, 'return_breakdown': return_breakdown})


def billing_page(request):
    denominations = DenominationMaster.objects.order_by('-value')
    return render(request, 'billing_app/billing_page.html', {'denominations': denominations})




def invoice_view(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'billing_app/invoice.html', {'bill': bill})




def customer_history(request):
    email = request.GET.get('email')
    bills = []
    if email:
        bills = Bill.objects.filter(customer_email=email).order_by('-created_at')
    return render(request, 'billing_app/history.html', {'bills': bills})