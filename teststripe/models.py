from django.db import models
import stripe


class TypeCurrency(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=3)
    type = models.ForeignKey(TypeCurrency, default=None, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    price = models.IntegerField()
    currency = models.ForeignKey(Currency, default=None, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class ItemOrder(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField()


class Discount(models.Model):
    code = models.CharField(max_length=100)
    discount = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        stripe.Coupon.create(duration="once", id=self.id, percent_off=self.discount)

    def __str__(self):
        return self.code


class Promocode(models.Model):
    code = models.CharField(max_length=100)
    coupon = models.ForeignKey(Discount, on_delete=models.CASCADE, default=None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        stripe.PromotionCode.create(coupon=self.coupon.id, code=self.code)

    def __str__(self):
        return self.code

class Tax(models.Model):
    name = models.CharField(max_length=100)
    inclusive = models.BooleanField(default=False)
    percentage = models.FloatField()
    country = models.CharField(max_length=3)
    desc = models.CharField(max_length=100)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        stripe.TaxRate.create(display_name=self.name, inclusive=self.inclusive, percentage=self.percentage, country=self.country, description=self.desc)

    def __str__(self):
        return self.desc


class Order(models.Model):
    items = models.ManyToManyField(ItemOrder)
    promocode = models.ForeignKey(Promocode, null=True, on_delete=models.SET_NULL)