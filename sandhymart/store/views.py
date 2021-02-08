from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect

import json
import datetime

from .models import *

from .form import productForm, createUserForm, customerSettingsForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user, allowed_users

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import OrderSerializer
# Create your views here.


@api_view(['GET'])
def getItems(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data)


def store(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)


def searching(request):
    product_name = request.GET.get('keyword')
    products = Product.objects.filter(name__icontains=product_name)
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)


@allowed_users(allowed_roles=['admin', 'customer'])
def addItem(request):
    if request.user.is_authenticated:
        if request.POST:
            productId = request.POST.get('productId')
            customer = request.user.customer
            product = Product.objects.get(id=productId)
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)

            orderItem, created = OrderItem.objects.get_or_create(
                order=order, product=product)

            orderItem.quantity += 1

            orderItem.save()
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
            return redirect('addItem')

        else:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items

    else:
        print("user not logged in")

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)


@allowed_users(allowed_roles=['admin', 'customer'])
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    if action == 'delete':
        orderItem.delete()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item Was Added', safe=False)


@allowed_users(allowed_roles=['admin', 'customer'])
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/checkout.html', context)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    customer = request.user.customer
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    order.transaction_id = transaction_id
    order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zipcode=request.POST.get('zipcode'),
        )

    return redirect('store')


@allowed_users(allowed_roles=['admin'])
def productList(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'seller/productList.html', context)


@allowed_users(allowed_roles=['admin'])
def addProduct(request):
    if request.POST:
        form = productForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productList')
    else:
        form = productForm()
        context = {
            'form': form,
        }
        return render(request, 'seller/addProduct.html', context)


@allowed_users(allowed_roles=['admin'])
def updateProduct(request, id_product):
    product = Product.objects.get(id=id_product)
    if request.POST:
        if request.FILES:
            remove = get_object_or_404(Product, id=id_product)
            if remove.image and remove.image != 'placeholder.png':
                remove.image.delete()

        form = productForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('productList')
    else:
        form = productForm(instance=product)
        context = {
            'form': form,
        }
        return render(request, 'seller/addProduct.html', context)


@allowed_users(allowed_roles=['admin'])
def productDelete(request):
    id_product = request.POST.get('id_product')
    print(id_product)
    remove = get_object_or_404(Product, id=id_product)
    if remove.image and remove.image != 'placeholder.png':
        remove.image.delete()

    product = Product.objects.filter(id=id_product)
    product.delete()

    return redirect('productList')


@unauthenticated_user
def registerPage(request):
    form = createUserForm()

    if request.POST:
        form = createUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request, 'Account Was Created for ' + username)
            return redirect('loginPage')
    context = {
        'form': form,
    }
    return render(request, 'store/registerPage.html', context)


@unauthenticated_user
def loginPage(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            group = request.user.groups.all()[0].name
            if group == 'customer':
                return redirect('store')
            elif group == 'admin':
                return redirect('productList')
        else:
            messages.info(request, 'Username or Password is Incorrect')
            return render(request, 'store/loginPage.html')
    return render(request, 'store/loginPage.html')


def logoutPage(request):
    logout(request)
    return redirect('loginPage')


@allowed_users(allowed_roles=['admin', 'customer'])
def accountSettings(request):
    customer = request.user.customer
    form = customerSettingsForm(instance=customer)
    if request.POST:
        if request.FILES:
            remove = get_object_or_404(Customer, id=customer.id)
            if remove.profil_pic and remove.profil_pic != 'profile/default.jpg':
                remove.profil_pic.delete()

        form = customerSettingsForm(
            request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {
        'form': form,
    }
    return render(request, 'store/accountSettings.html', context)


def orderList(request):
    orders = Order.objects.filter(complete=True).order_by('-date_ordered')
    context = {
        'orders': orders,
    }
    return render(request, 'seller/orderList.html', context)


def detailOrder(request, order_id):
    order = Order.objects.get(id=order_id)
    orderitems = OrderItem.objects.filter(order=order)
    total = order.get_cart_total
    context = {
        'orderItems': orderitems,
        'total': total,
    }
    return render(request, 'seller/detailOrder.html', context)
