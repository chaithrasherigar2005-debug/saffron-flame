
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, MenuItem, Cart
from decimal import Decimal
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import UserProfile,Order,OrderItem, Cart, OTP, Reservation
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import random
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
import re

def home(request):
    return render(request, 'index.html')

def reservation(request):

    if request.method == 'POST':

        Reservation.objects.create(

            user=request.user,

            seat_number=request.POST['seat_number'],

            reservation_date=request.POST['reservation_date'],

            reservation_time=request.POST['reservation_time'],

            guests=request.POST['guests']
        )

        messages.success(
             request,
                "🎉 Table reserved successfully!"
        )

        return redirect('/')

    return render(
        request,
        'reservation.html'
    )

def seat_selection(request):

    occupied_seats = Reservation.objects.filter(
        status='Occupied'
    ).values_list(
        'seat_number',
        flat=True
    )

    return render(
        request,
        'seat_selection.html',
        {
            'occupied_seats': list(occupied_seats)
        }
    )
def menu(request):
    categories = Category.objects.prefetch_related('items').all()
    return render(request, 'menu.html', {
        'categories': categories
    })

def add_to_cart(request, item_id):

    if not request.user.is_authenticated:
        return redirect('/login/')

    item = MenuItem.objects.get(id=item_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        item=item
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('/cart/')

def cart(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    cart_items = Cart.objects.filter(
        user=request.user
    )

    total = sum(
        item.total_price()
        for item in cart_items
    )

    return render(
        request,
        'cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )
def delete_cart(request, cart_id):

    cart_item = get_object_or_404(Cart, id=cart_id)

    cart_item.delete()

    return redirect('/cart/')
   
def increase_quantity(request, cart_id):

    cart_item = Cart.objects.get(id=cart_id)
    cart_item.quantity += 1
    cart_item.save()

    return redirect('/cart/')   

def decrease_quantity(request, cart_id):

    cart_item = Cart.objects.get(id=cart_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('/cart/')

def receipt(request):

    cart_items = Cart.objects.filter(
        user=request.user
    )
    subtotal = Decimal('0')

    for item in cart_items:
        subtotal += item.item.price * item.quantity

    gst = subtotal * Decimal('0.05')
    service_tax = subtotal * Decimal('0.02')

    reservation_fee = Decimal('0')

    if request.user.userprofile.dining_option == "Dine In":
        reservation_fee = Decimal('200')

    total = (
        subtotal +
        gst +
        service_tax +
        reservation_fee
    )
    return render(request, 'receipt.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'gst': gst,
        'service_tax': service_tax,
        'reservation_fee': reservation_fee,
        'total': total,
        'dining_option': request.user.userprofile.dining_option
    })
   
def user_login(request):

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        try:

            user_obj = User.objects.get(
                email=email
            )

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

        except User.DoesNotExist:

            user = None

        if user is not None:

            login(request, user)

            return redirect('/')

        else:

            return render(
                request,
                'login.html',
                {
                    'error':
                    'Wrong Password!! Please enter the correct password.'
                }
            )

    return render(
        request,
        'login.html'
    )


def register(request):

    if request.method == 'POST':

        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']


        if not re.match(r'^[A-Za-z][A-Za-z0-9 ]*$', full_name):

             return render(
                request,
                'register.html',
                {
                    'error':
                    'Username must start with a letter and can contain letters, numbers, and spaces only. Special characters are not allowed.'
                }
            )
        if (
            len(password) < 8
        or not any(char.isupper() for char in password)
        or not any(char.islower() for char in password)
        or not any(char.isdigit() for char in password)
        or not any(
            char in "!@#$%^&*()_+-=[]{}|;:,.<>?"
            for char in password
        )
    ):

            return render(
                request,
                'register.html',
                {
                    'error':
                     '''
    Password must contain:
    • At least 8 characters
    • One uppercase letter (A-Z)
    • One lowercase letter (a-z)
    • One number (0-9)
    • One special character (!@#$%^&*)
            '''
        }
    )

        if len(mobile) != 10 or not mobile.isdigit():

            return render(
                 request,
                'register.html',
                {
                     'error':
                    'Mobile number must contain exactly 10 digits'
                }
            )
        

        # CHECK IF USERNAME ALREADY EXISTS
        if User.objects.filter(email=email).exists():

            return render(request, 'register.html', {
                'error': 'Username already exists'
            })

        # CREATE USER
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.first_name = full_name
        user.save()
        UserProfile.objects.create(
            user=user,
            phone=mobile,
        )
         # SUCCESS MESSAGE
        messages.success(
            request,
            "Account created successfully. Please login."
        )

        logout(request)

        return redirect('/login/')

       

    return render(request, 'register.html')


def profile(request):

    return render(request, 'profile.html')

def user_logout(request):

    logout(request)

    return redirect('/')

def delivery(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':

        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        city = request.POST.get('city')
        state = request.POST.get('state')

        profile.address = (
                f"{address}, "
                f"{city}, "
                f"{state} - "
                f"{pincode}"
        )
        profile.dining_option = "Online Delivery"
        profile.save()

        return redirect('/menu/')

    return render(request, 'delivery.html')

def forgot_password(request):

    if request.method == 'POST':

        email = request.POST['email']

        try:

            User.objects.get(
                email=email
            )

            print("OTP REQUEST RECEIVED")

            otp = str(
                random.randint(
                    100000,
                    999999
                )
            )

            OTP.objects.filter(
                email=email
            ).delete()

            OTP.objects.create(
                email=email,
                otp=otp
            )

            send_mail(
                'Password Reset OTP',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

            request.session['reset_email'] = email

            return redirect('/verify-otp/')
            

        except User.DoesNotExist:

            return render(
                request,
                'forgot_password.html',
                {
                    'error':
                    'No account found with this email'
                }
            )

    return render(
        request,
        'forgot_password.html'
    )


def dining_option(request):

    return render(request, 'dining_option.html')

def dine_in(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    profile.dining_option = "Dine In"
    profile.save()

    return redirect('/menu/')


def contact(request):
    return render(request, 'contact.html')

from decimal import Decimal

def payment(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    cart_items = Cart.objects.filter(
    user=request.user
    )

    subtotal = Decimal('0')

    for item in cart_items:
        subtotal += item.item.price * item.quantity

    gst = subtotal * Decimal('0.05')
    service_tax = subtotal * Decimal('0.02')

    total = subtotal + gst + service_tax

    if request.method == 'POST':

        profile = request.user.userprofile

        cart_items = Cart.objects.filter(
            user=request.user
        )

        total = sum(
            item.item.price * item.quantity
            for item in cart_items
        )

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_status="Paid Online"
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                item_name=item.item.name,
                quantity=item.quantity,
                price=item.item.price
            )

        profile.payment_status = "Paid"

        profile.save()
        cart_items.delete() 
        return render(request, 'payment_success.html')

    return render(
        request,
        'payment.html',
        {
            'total': total
        }
    )

def pay_restaurant(request):

    cart_items = Cart.objects.filter(
    user=request.user
    )

    subtotal = 0

    for item in cart_items:
        subtotal += item.item.price * item.quantity

    gst = subtotal * Decimal('0.05')
    service_tax = subtotal * Decimal('0.02')

    reservation_fee = Decimal('0')

    if request.user.userprofile.dining_option == "Dine In":
         reservation_fee = Decimal('200')

    total = (
        subtotal +
        gst +
        service_tax +
        reservation_fee
    )

    if request.method == 'POST':

        profile = request.user.userprofile

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_status="Pay At Restaurant"
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                item_name=item.item.name,
                quantity=item.quantity,
                price=item.item.price
            )

        profile.payment_status = "Pay At Restaurant"

        profile.save()

        cart_items.delete()

        return render(
            request,
            'restaurant_success.html'
        )
    return render(
        request,
        'pay_restaurant.html',
        {'total': total}
    )

def cash_on_delivery(request):

    cart_items = Cart.objects.filter(
        user=request.user
    )

    subtotal = Decimal('0')

    for item in cart_items:
        subtotal += item.item.price * item.quantity

    gst = subtotal * Decimal('0.05')
    service_tax = subtotal * Decimal('0.02')

    total = subtotal + gst + service_tax

    if request.method == 'POST':

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_status="Cash On Delivery"
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                item_name=item.item.name,
                quantity=item.quantity,
                price=item.item.price
            )


        cart_items.delete()

        return redirect('/my-orders/')

    return render(
        request,
        'cash_on_delivery.html',
        {
            'total': total
        }
    )
    
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'my_orders.html',
        {'orders': orders}
    )

def cancel_order(request, order_id):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    order.status = "Cancelled"

    order.save()

    return redirect('/my-orders/')


def verify_otp(request):

    if request.method == 'GET':

        return render(
            request,
            'verify_otp.html',
            {
                'email': request.session.get('reset_email')
            }
        )

    email = request.POST['email']

    entered_otp = request.POST['otp']

    # STEP 1 : VERIFY OTP

    if 'new_password' not in request.POST:

        try:

            otp_obj = OTP.objects.filter(
                email=email
            ).latest('created_at')

            if otp_obj.otp != entered_otp:

                return render(
                    request,
                    'verify_otp.html',
                    {
                        'email': email,
                        'error': 'Invalid OTP'
                    }
                )

            return render(
                request,
                'verify_otp.html',
                {
                    'email': email,
                    'otp': entered_otp,
                    'otp_verified': True
                }
            )

        except Exception as e:

            return HttpResponse(str(e))

    # STEP 2 : CHANGE PASSWORD

    new_password = request.POST.get(
        'new_password'
    )

    confirm_password = request.POST.get(
        'confirm_password'
    )
    if new_password != confirm_password:

        return render(
            request,
            'verify_otp.html',
            {
                'email': email,
                'otp_verified': True,
                'error': 'Passwords do not match'
            }
        )

    try:

        user = User.objects.get(
            email=email
        )

        user.set_password(
            new_password
        )

        user.save()

        messages.success(
            request,
            "Password changed successfully. Please login."
        )

        return redirect('/login/')

    except Exception as e:

        return HttpResponse(str(e))