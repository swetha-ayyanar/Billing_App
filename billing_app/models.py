from django.db import models


class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    available_stocks = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)



class Bill(models.Model):
    customer_email = models.EmailField()
    total_amount = models.FloatField()
    amount_paid = models.FloatField()
    balance_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Bill #{self.id} - {self.customer_email} - {self.created_at.date()}"


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    price = models.FloatField() # price without tax for the qty
    tax = models.FloatField()
    total = models.FloatField() # price + tax for qty


class DenominationMaster(models.Model):
    value = models.IntegerField(unique=True)


    def __str__(self):
        return str(self.value)


class BillDenomination(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='given_denominations')
    denomination_value = models.IntegerField()
    count = models.IntegerField()


class ReturnDenomination(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='return_denominations')
    denomination_value = models.IntegerField()
    count = models.IntegerField()