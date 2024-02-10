from django.shortcuts import render , HttpResponse
from django.http import JsonResponse
from .models import *
import json
import datetime
# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer , complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0 , 'get_cart_total':0 , 'shipping':False}
        cartItems = order['get_cart_items']
    context = {'items':items , 'order':order}
    
    productlist = Product.objects.all()
    context = {"productlist":productlist , "cartItems" : cartItems}
    return render(request , "store/store.html" , context)
   

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer , complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print("CART:",cart)
        items = []
        order = {'get_cart_items':0 , 'get_cart_total':0 , 'shipping':False}
        cartItems = order['get_cart_items']
        for i in cart:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id = i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] = total
            order['get_cart_items'] = cartItems
    context = {'items':items , 'order':order , 'cartItems' : cartItems}
    return render(request , "store/cart.html" , context)

def checkout(request):
    cartItems = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer , complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0 , 'get_cart_total':0 , 'shipping':False}
    context = {'items':items , 'order':order , 'cartItems':cartItems}
    return render(request , "store/checkout.html" , context)

def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print("Action:" , action)
    print("ProductId:" , productId)
    
    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order , created = Order.objects.get_or_create(customer=customer , complete = False)
    orderItem , created = OrderItem.objects.get_or_create(order=order , product = product)
    
    if action=="add":
        orderItem.quantity = (orderItem.quantity + 1)
    elif action=="remove":
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()
    
    if orderItem.quantity<=0:
        orderItem.delete()
    return JsonResponse("Item was added" , safe=False)
    
def process_order(request):
    # print("Data",request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer , complete = False)
        total = data['form']['total']
        order.transaction_id = transaction_id
        
        if total == order.get_cart_total:
            order.complete = True
            # order.get_cart_total = 0
        order.save()
        
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order = order,
                address = data['shipping']['address'],
                state = data['shipping']['state'],
                city = data['shipping']['city'],
                zipcode = data['shipping']['zipcode']
            )
    return JsonResponse("Payment Done" , safe=False)