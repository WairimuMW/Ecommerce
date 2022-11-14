from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from .forms import *
from .filters import *
from .decorators import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from django.utils.regex_helper import Group
from django.contrib.auth.models import Group
import decimal
import json
import datetime

# generating a pdf
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


# Create your views here.
def home(request):
    context = {}
    return render(request, 'arts/home.html', context)

def about(request):
    artist = ArtistProfile.objects.all()
    
    context = {'artist':artist}
    return render(request, 'arts/about.html', context)

def contact(request):
    context = {}
    return render(request, 'arts/contact.html', context)

def register(request):
    context = {}
    return render(request, 'arts/register.html', context)

@unauthenticated_user
def user_login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            group = request.user.groups.all()[0].name
            if group == 'artist':
                return redirect('artist_dashboard')
            else:
                return redirect('customer_dashboard')
        else:
            messages.info(request, 'Your username and password did not match. Please try again.')
    
    return render(request, 'arts/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def art(request):
    if request.user.is_authenticated:
        customer = request.user.customerprofile
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'delivery':True}
        cartItems = order['get_cart_items']   
    
    art = Art.objects.all()
    myFilter = ArtFilter(request.GET, queryset=art)
    art = myFilter.qs
    context = {'art':art, 'cartItems':cartItems, 'myFilter':myFilter}
    return render(request, 'arts/art.html', context)

# ecommerce views

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customerprofile
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'delivery':True}
        
    context = {'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'arts/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customerprofile
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'delivery':True}
        
    context = {'items': items, 'order':order, 'cartItems':cartItems}
    return render(request, 'arts/checkout.html', context)

def receipt(request):
    transaction_id = datetime.datetime.now().timestamp()
    if request.user.is_authenticated:
        customer = request.user.customerprofile
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'delivery':True}
        
    buff = io.BytesIO()
    can = canvas.Canvas(buff, pagesize=letter, bottomup=0)
    textobj = can.beginText()
    textobj.setTextOrigin(inch, inch)
    textobj.setFont("Helvetica", 12)
    
    lines = [
        "Transaction ID: " + str(transaction_id),
        "_____________________________________________________________",
        " ",
    ]
    
    for items in items:
        lines.append("Art Piece: " + str(items.art.description))
        lines.append("Artist Name: " + str(items.art.artist.first_name) + " " + str(items.art.artist.last_name))
        lines.append("Artist Phone Number: " + str(items.art.artist.phonenumber))
        lines.append("Price: Ksh " + str(items.art.price))
        lines.append("Date Ordered: " + str(items.order.date_ordered))
        lines.append(" ")
    
    for line in lines:
        textobj.textLine(line)
    
    can.drawText(textobj)
    can.showPage()
    can.save()
    buff.seek(0)
    
    return FileResponse(buff, as_attachment=True, filename="receipt.pdf")


def update_item(request):
    data = json.loads(request.body)
    artId = data['artId']
    action = data['action']
    
    print('Action:', action)
    print('Art:', artId)
    
    customer = request.user.customerprofile
    art = Art.objects.get(id=artId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    orderItem, created = OrderItem.objects.get_or_create(order=order, art=art)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('Item was added to cart', safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customerprofile
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        
        if total == order.get_cart_total:
            order.complete = True
        
        order.save()
        
        if order.delivery == True:
            Delivery.objects.create(
                customer = customer,
                order = order,
                address = data['delivery']['address'],
                country = data['delivery']['country'],
                county = data['delivery']['county'],
                town = data['delivery']['town'],
            )
    
    else:
        print('User is not logged in')
    
    return JsonResponse('Payment Complete', safe=False)


# artist views

@unauthenticated_user
def artist_register(request):
    if request.method == 'POST':
        form = ArtistRegistrationForm (request.POST)
        
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.artistprofile.email = form.cleaned_data.get('email')
            user.artistprofile.phonenumber = form.cleaned_data.get('phonenumber')
            group = Group.objects.get(name = 'artist')
            user.groups.add(group)
            user.save()
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username = username, password = password)
            login(request, user)
            return redirect('artist_dashboard')
    else:
        form = ArtistRegistrationForm()
            
    context = {'form':form}
    return render(request, 'arts/artist/artist_register.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'artist'])
def createArt(request, pk):
    artist = ArtistProfile.objects.get(id=pk)
    form = CreateArtForm(initial={'artist':artist})
    if request.method=='POST':
        form = CreateArtForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('artist_dashboard')
    
    
    context = {'form':form}
    return render(request, 'arts/artist/art_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'artist'])
def updateArt(request, pk):
    art = Art.objects.get(id=pk)
    form = CreateArtForm(instance=art)
    
    if request.method=='POST':
        form = CreateArtForm(request.POST, request.FILES, instance=art)
        if form.is_valid():
            form.save()
            return redirect('artist_dashboard')
    
    context = {'form':form}
    return render(request, 'arts/artist/art_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'artist'])
def deleteArt(request, pk):
    art = Art.objects.get(id=pk)
    if request.method=="POST":
        art.delete()
        return redirect('artist_dashboard')
        
    context = {'art':art}
    return render(request, 'arts/artist/delete_art.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'artist'])
def artist_dashboard(request):
    artist = request.user.artistprofile
    art = Art.objects.filter(artist=artist)
    total_art = art.count()
    
    context = {'art':art, 'total_art':total_art, 'artist':artist}
    return render(request, 'arts/artist/artist_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'artist'])
def artist_account(request):
    artist = request.user.artistprofile
    
    context = {'artist':artist} 
    return render(request, 'arts/artist/artist_account.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'artist'])
def artist_settings(request):
    artist = request.user.artistprofile
    form = ArtistProfileForm(instance=artist)
    
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=artist)
        if form.is_valid:
            form.save()
    
    context = {'form':form}
    return render(request, 'arts/artist/artist_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'artist'])
def artist_report(request):
    buff = io.BytesIO()
    can = canvas.Canvas(buff, pagesize=letter, bottomup=0)
    textobj = can.beginText()
    textobj.setTextOrigin(inch, inch)
    textobj.setFont("Helvetica", 12)
    
    artist = request.user.artistprofile
    art = Art.objects.filter(artist=artist)
    
    lines = [
        "ART PIECES UPLOADED",
        "_____________________________________________________________",
        " ",
    ]
    
    for art in art:
        lines.append("Art Piece: " + str(art.description))
        lines.append("Price: Ksh." + str(art.price))
        lines.append("Material: " + str(art.material))
        lines.append("Art Type: " + str(art.art_type))
        lines.append("Status: " + str(art.status))
        lines.append(" ")
    
    for line in lines:
        textobj.textLine(line)
    
    can.drawText(textobj)
    can.showPage()
    can.save()
    buff.seek(0)
    
    return FileResponse(buff, as_attachment=True, filename="artist_report.pdf")

  
# customer views

@unauthenticated_user
def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm (request.POST)
        
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.customerprofile.email = form.cleaned_data.get('email')
            user.customerprofile.phonenumber = form.cleaned_data.get('phonenumber')
            group = Group.objects.get(name = 'customer')
            user.groups.add(group)
            user.save()
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username = username, password = password)
            login(request, user)
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
                
    context = {'form':form}
    return render(request, 'arts/customer/customer_register.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'customer'])   
def customer_dashboard(request):
    customer = request.user.customerprofile
    
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    
    context = {'items':items, 'order':order}
    return render(request, 'arts/customer/customer_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'customer'])
def customer_account(request):
    customer = request.user.customerprofile
    
    context = {'customer':customer} 
    return render(request, 'arts/customer/customer_account.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'customer'])
def customer_settings(request):
    customer = request.user.customerprofile
    form = CustomerProfileForm(instance=customer)
    
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
        if form.is_valid:
            form.save()
    
    context = {'form':form}
    return render(request, 'arts/customer/customer_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'customer'])
def customer_report(request):
    # Bytestream buffer
    buff = io.BytesIO()
    # Creating a canvas
    can = canvas.Canvas(buff, pagesize=letter, bottomup=0)
    # Creating a text object
    textobj = can.beginText()
    textobj.setTextOrigin(inch, inch)
    textobj.setFont("Helvetica", 12)
    
    customer = request.user.customerprofile
    order = Order.objects.filter(customer=customer)
    item = OrderItem.objects.filter(order=order)
    delivery = Delivery.objects.filter(customer=customer)
    
    lines = [
        "ORDERS",
        "_____________________________________________________________",
        " ",
    ]
    
    for delivery in delivery:
        lines.append("Order Number: " + str(delivery.order))
        lines.append("Customer Name: " + str(delivery.customer.first_name))
        lines.append("Address: " + str(delivery.address))
        lines.append("Date Of Order: " + str(delivery.order.date_ordered))
        lines.append("Delivery Status: " + str(delivery.status))
        lines.append("Payment: " + str(delivery.payment))
        lines.append(" ")
    
    for line in lines:
        textobj.textLine(line)
    
    can.drawText(textobj)
    can.showPage()
    can.save()
    buff.seek(0)
    
    return FileResponse(buff, as_attachment=True, filename="customer_report.pdf")



