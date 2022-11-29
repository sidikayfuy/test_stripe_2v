import array
import json

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import Item, Order, ItemOrder, Tax, Promocode
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import ItemSerializer, OrderSerializer
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


def index(request):
    items = Item.objects.all()
    request.session.set_expiry(100)
    return render(request, 'teststripe/index.html', {'items': items})


def create_intent(request):
    amount = 0
    currency = []
    cart = request.POST.getlist('order[]')
    order = Order.objects.create()
    for i in cart:
        item_order = ItemOrder.objects.create(item=Item.objects.get(id=int(str(i).split(',')[0])),
                                              count=int(str(i).split(',')[1]))
        order.items.add(item_order)
    try:
        order.promocode = Promocode.objects.get(code=request.POST.get('promocode'))
    except:
        order.promocode = None
    for i in cart:
        item = Item.objects.get(id=int(str(i).split(',')[0]))
        count = int(str(i).split(',')[1])
        amount += (item.price * 100 if item.currency.type.name == 'decimal' else item.price)*count
        if item.currency.name not in currency:
            currency.append(item.currency.name)
    if order.promocode != None:
        amount=round(amount*(100-order.promocode.coupon.discount)/100)
    if len(currency) == 1:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency[0],
            payment_method_types=["card"],
        )
        public_key = settings.STRIPE_PUBLISHABLE_KEY
        return JsonResponse({'clientSecret': intent['client_secret'], 'public_key': public_key})
    else:
        return HttpResponse('multycurrency', status=500)

def item(request, id):
    item = Item.objects.get(id=int(id))
    return render(request, 'teststripe/item.html', {'item': item})


def add_to_cart(request):
    id = request.GET.get('item')
    count = request.GET.get('count')
    item = Item.objects.get(id=int(id))
    if 'cart' in request.session.keys():
        cart = request.session['cart']
        ids = [i[0] for i in cart]
        if item.id in ids:
            for i in cart:
                if i[0] == item.id:
                    i[1] += int(count)
        else:
            cart.append([item.id, int(count)])
        request.session['cart'] = cart
    else:
        request.session['cart'] = []
        request.session['cart'].append([item.id, int(count)])
    return HttpResponse(status=200)


def cart(request):
    items = []
    amount = 0
    if 'cart' in request.session.keys():
        for i in request.session['cart']:
            items.append([Item.objects.get(id=i[0]), i[1], Item.objects.get(id=i[0]).price*i[1]])
            amount+=Item.objects.get(id=i[0]).price*i[1]

    return render(request, 'teststripe/cart.html', {'items': items, 'amount': amount})


def make_session(domain, order):
    session = stripe.checkout.Session.create(
        success_url=f"{domain}",
        cancel_url=f"{domain}",
        line_items=[
            {
                'price_data': {
                    'currency': i.item.currency.name,
                    'product_data': {
                        'name': i.item.name,
                    },
                    'unit_amount': i.item.price * 100 if i.item.currency.type.name == 'decimal' else i.item.price,
                },
                "quantity": i.count,
                "tax_rates": [tax['id'] for tax in stripe.TaxRate.list()['data'] if tax['description'] == i.item.currency.name.lower() and tax['active'] == True],
            }
            for i in order.items.all()],
        mode="payment",
        discounts=[{'coupon': Promocode.objects.get(code=order.promocode.code).coupon.id}] if order.promocode != None else None,
    )
    return session


def buy(request, id):
    item = Item.objects.get(id=id)
    domain = request.build_absolute_uri().replace(request.get_full_path(), '')
    quantity = request.POST['count']
    order = Order.objects.create()
    item_order = ItemOrder.objects.create(item=item, count=quantity)
    order.items.add(item_order)
    session = make_session(domain, order)
    public_key = settings.STRIPE_PUBLISHABLE_KEY
    return JsonResponse({'session': session.id, 'public_key': public_key})


def buyorder(request):
    cart = request.POST.getlist('order[]')
    order = Order.objects.create()
    for i in cart:
        item_order = ItemOrder.objects.create(item=Item.objects.get(id=int(str(i).split(',')[0])), count=int(str(i).split(',')[1]))
        order.items.add(item_order)
    try:
        order.promocode = Promocode.objects.get(code=request.POST.get('promocode'))
    except:
        order.promocode = None
    domain = request.build_absolute_uri().replace(request.get_full_path(), '')
    try:
        session = make_session(domain, order)
        public_key = settings.STRIPE_PUBLISHABLE_KEY
        return JsonResponse({'session': session.id, 'public_key': public_key})
    except Exception as e:
        print(e.args[0])
        return HttpResponse(e.args[0], status=500)



def checkpromo(request):
    code = request.POST['code']
    try:
        percent = Promocode.objects.get(code=code)
        return HttpResponse(percent.coupon.discount, status=200)
    except Exception as e:
        return HttpResponse('bad', status=200)


def checkcart(request):
    currency = []
    cart = request.POST.getlist('order[]')
    for i in cart:
        item = Item.objects.get(id=int(str(i).split(',')[0]))
        if item.currency.name not in currency:
            currency.append(item.currency.name)
    if len(currency) == 1:
        return HttpResponse(currency[0], status=200)
    else:
        return HttpResponse('multicurrency', status=500)