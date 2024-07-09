from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from .models import Products, Category, SoldItems
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Max
today = timezone.now().date()
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.



def userLogin(request):
    if request.method == 'POST':
        phone_num = request.POST.get('phone_num')
        password = request.POST.get('password')

        info = authenticate(username=phone_num, password=password)
        if info is not None:
            auth_login(request, info)
            if info.is_staff or info.is_superuser:
                return redirect('homepage')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('userLogin')
    return render(request, 'login.html')


def logoutUser(request):
    auth.logout(request)
    messages.success(request, "Logged out Successfully!")
    return redirect('userLogin')

def staff(request):
    staffs = User.objects.all().order_by('-id')
    
    
    if request.method == 'POST':
         
        fullname = request.POST['staff_name']
        mobile_num = request.POST['mobile_num']
        gender = request.POST['gender']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            if User.objects.filter(username=mobile_num).exists():
                messages.error(request, 'Phone number already taken.')
                return redirect(request.META.get('HTTP_REFERER'))

            else:
                seniors = User.objects.create_user(
                    first_name=fullname, username=mobile_num, last_name=gender, password=password1, is_staff=True, is_superuser=False )
                seniors.save()
                
                messages.success(request, 'Staff Account created')
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Password does not match.')
            return redirect(request.META.get('HTTP_REFERER'))    
    
    
    
    context = {
        'staffs':staffs
    }
    
    return render(request, 'saleslady.html', context)

def checkoutHistory(request):
    checkoutHistory = SoldItems.objects.all().order_by('-id')
    
    context = {
        'checkoutHistory': checkoutHistory,
    }
    return render(request, 'checkoutHistory.html', context)


def checkout(request):
    products = Products.objects.all().order_by('-id')
    
    if request.method == 'POST':
        product_id = request.POST['product']
        quantity = int(request.POST['quantity'])  # Convert quantity to integer
        total_amount = float(request.POST['totalAmount'])  # Convert totalAmount to float

        # Retrieve the product using the product name
        product = get_object_or_404(Products, id=product_id)
        
        # Check if there is enough stock
        if product.quantity >= quantity:
            # Deduct the quantity from the product's stock
            product.quantity -= quantity
            product.save()

            # Record the sale
            new_sold = SoldItems.objects.create(
                product_name=product,  # ForeignKey should be a model instance
                quantity=quantity, 
                price=total_amount,  # Use DecimalField for price
                sold_date=timezone.now()
            )
            new_sold.save()
            
            messages.success(request, 'Checkout successfully completed.')
        else:
            messages.error(request, 'Insufficient stock for the product.')
    
    context = {
        'products': products,
    }
    
    return render(request, 'checkout.html', context)












def homepage(request):
    products = Products.objects.all().order_by('-id')
    
    # -----REPORT ------

    current = timezone.now()

    # Calculate the dates for the last 7 days
    yesterday = current - timedelta(days=1)
    two_days_ago = current - timedelta(days=2)
    three_days_ago = current - timedelta(days=3)
    four_days_ago = current - timedelta(days=4)
    five_days_ago = current - timedelta(days=5)
    six_days_ago = current - timedelta(days=6)
    seven_days_ago = current - timedelta(days=7)

    # Fetch the total sold items for each date
    current_history = SoldItems.objects.filter(sold_date__date=current.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    yesterday_history = SoldItems.objects.filter(sold_date__date=yesterday.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    two_days_ago_history = SoldItems.objects.filter(sold_date__date=two_days_ago.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    three_days_ago_history = SoldItems.objects.filter(sold_date__date=three_days_ago.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    four_days_ago_history = SoldItems.objects.filter(sold_date__date=four_days_ago.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    five_days_ago_history = SoldItems.objects.filter(sold_date__date=five_days_ago.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    six_days_ago_history = SoldItems.objects.filter(sold_date__date=six_days_ago.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    seven_days_ago_history = SoldItems.objects.filter(sold_date__date=seven_days_ago.date()).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # ----- REPORT -----
    
    
    
    # Get today's date
    today = timezone.now().date()

    # Filter and sum the quantity for items sold today
    total_quantity_sold_today = SoldItems.objects.filter(sold_date__date=today).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Calculate total price of items sold today
    sold_items_today = SoldItems.objects.filter(sold_date__date=today)
    total_price_sold_today = sold_items_today.aggregate(Sum('price'))['price__sum'] or 0

    # Calculate total price and quantity of all products
    total_price = SoldItems.objects.aggregate(
    total=Sum(F('price') * F('quantity'))
    )['total'] or 0.0
    total_quantity = Products.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Calculate total price of items sold today
    total_price_sold_today = SoldItems.objects.filter(sold_date__date=today).aggregate(Sum('price'))['price__sum'] or 0

    # Calculate the highest total price for any day and the corresponding date
    
    highest_total_price_data = (
        SoldItems.objects
        .values('sold_date__date')
        .annotate(total_price=Sum('price'))
        .order_by('-total_price')
    )
    
    if highest_total_price_data:
        most_recent = highest_total_price_data[0]
        highest_total_price = most_recent['total_price']
        highest_total_price_date = most_recent['sold_date__date']
    else:
        highest_total_price = 0
        highest_total_price_date = 'N/A'

    context = {
        'products': products,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'total_quantity_sold_today': total_quantity_sold_today,
        'total_price_sold_today': total_price_sold_today,
        'highest_total_price': highest_total_price,
        'highest_total_price_date': highest_total_price_date,
        
        
        'current_history': current_history,
        'yesterday_history': yesterday_history,
        'two_days_ago_history': two_days_ago_history,
        'three_days_ago_history': three_days_ago_history,
        'four_days_ago_history': four_days_ago_history,
        'five_days_ago_history': five_days_ago_history,
        'six_days_ago_history': six_days_ago_history,
        'seven_days_ago_history': seven_days_ago_history,
        
        'current': current,
        'yesterday': yesterday,
        'two_days_ago': two_days_ago,
        'three_days_ago': three_days_ago,
        'four_days_ago': four_days_ago,
        'five_days_ago': five_days_ago,
        'six_days_ago': six_days_ago,
        
    }

    return render(request, 'index.html', context)








def homepageMonthly(request):
    products = Products.objects.all().order_by('-id')
    
    # -----REPORT ------
    now = timezone.now()
        # January
    jan_history = SoldItems.objects.filter(
        sold_date__month=1,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # February
    feb_history = SoldItems.objects.filter(
        sold_date__month=2,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # March
    mar_history = SoldItems.objects.filter(
        sold_date__month=3,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # April
    apr_history = SoldItems.objects.filter(
        sold_date__month=4,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # May
    may_history = SoldItems.objects.filter(
        sold_date__month=5,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # June
    jun_history = SoldItems.objects.filter(
        sold_date__month=6,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # July
    jul_history = SoldItems.objects.filter(
        sold_date__month=7,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # August
    aug_history = SoldItems.objects.filter(
        sold_date__month=8,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # September
    sept_history = SoldItems.objects.filter(
        sold_date__month=9,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # October
    oct_history = SoldItems.objects.filter(
        sold_date__month=10,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # November
    nov_history = SoldItems.objects.filter(
        sold_date__month=11,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # December
    dec_history = SoldItems.objects.filter(
        sold_date__month=12,
        sold_date__year=now.year
    ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
   
    # ----- REPORT -----
    
    
    
    # Get today's date
    today = timezone.now().date()

    # Filter and sum the quantity for items sold today
    total_quantity_sold_today = SoldItems.objects.filter(sold_date__date=today).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Calculate total price of items sold today
    sold_items_today = SoldItems.objects.filter(sold_date__date=today)
    total_price_sold_today = sold_items_today.aggregate(Sum('price'))['price__sum'] or 0

    # Calculate total price and quantity of all products
    total_price = Products.objects.aggregate(total=Sum('price'))['total'] or 0.0
    total_quantity = Products.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Calculate total price of items sold today
    total_price_sold_today = SoldItems.objects.filter(sold_date__date=today).aggregate(Sum('price'))['price__sum'] or 0

    # Calculate the highest total price for any day and the corresponding date
    highest_total_price_data = (
        SoldItems.objects
        .values('sold_date__date')
        .annotate(total_price=Sum('price'))
        .order_by('-total_price')
    )
    
    if highest_total_price_data:
        most_recent = highest_total_price_data[0]
        highest_total_price = most_recent['total_price']
        highest_total_price_date = most_recent['sold_date__date']
    else:
        highest_total_price = 0
        highest_total_price_date = 'N/A'

    context = {
        'products': products,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'total_quantity_sold_today': total_quantity_sold_today,
        'total_price_sold_today': total_price_sold_today,
        'highest_total_price': highest_total_price,
        'highest_total_price_date': highest_total_price_date,
        
        
        'jan_history':jan_history,
        'feb_history':feb_history,
        'mar_history':mar_history,
        'apr_history':apr_history,
        'may_history':may_history,
        'jun_history':jun_history,
        'jul_history':jul_history,
        'aug_history':aug_history,
        'sept_history':sept_history,
        'oct_history':oct_history,
        'nov_history':nov_history,
        'jan_history':jan_history,
    }

    return render(request, 'indexMonthly.html', context)











def products(request):
    categories = Category.objects.all().order_by('-id')
    products = Products.objects.all().order_by('-id')
    
    if request.method == 'POST':
        product_name = request.POST['product_name']
        category_name = request.POST['category']
        price = request.POST['price']
        quantity = request.POST['quantity']
        
        # Convert price to Decimal
        price = Decimal(price)
        
        # Look up the Category instance based on the category name
        category = Category.objects.get(type=category_name)
        
        # Check if the product already exists
        existing_product = Products.objects.filter(name=product_name).first()
        
        if existing_product:
            # Product exists, update the quantity
            existing_product.quantity += int(quantity)
            existing_product.save()
            messages.success(request, 'The Product is already exists. It will automatically add to the quantity of the existing product instead.')
        else:
            # Product does not exist, create a new one
            new_product = Products.objects.create(
                name=product_name,
                category=category,
                price=price,
                quantity=quantity
            )
            new_product.save()
            messages.success(request, 'Product Added!')
        
    context = {
        'categories': categories,
        'products': products,
    }
    
    return render(request, 'products.html', context)



def category(request):
    categories = Category.objects.all().order_by('-id')
    
    if request.method == 'POST':
        type = request.POST['type']
      
        
        # Check if the type already exists
        if Category.objects.filter(type=type).exists():
            messages.error(request, 'Category type already exists!')
            return redirect('category')  # Replace 'category' with the name of your URL pattern for this view
        
        # If the type does not exist, create the new category
        new_category = Category.objects.create(type=type)
        new_category.save()
        messages.success(request, 'Category type added!')
        
    context = {
        'categories': categories,
    }
    
    return render(request, 'category.html', context)


def removeCategory(request, category_id):
    Category.objects.filter(id=category_id).delete()
    messages.success(request, 'Category Deleted!')
    
    return redirect(request.META.get('HTTP_REFERER'))


def removeStaff(request, staff_id):
    User.objects.filter(id=staff_id).delete()
    messages.success(request, 'Staff Deleted!')
    
    return redirect(request.META.get('HTTP_REFERER'))


def editStaff(request, staff_id):
    try:
        staff = User.objects.get(pk=staff_id)
    except ObjectDoesNotExist:
        messages.error(request, 'Staff member not found.')
        return redirect('some_view')  # Redirect to a relevant view or page

    if request.method == 'POST':
        fullname = request.POST.get('staff_name')
        mobile_num = request.POST.get('mobile_num')
        gender = request.POST.get('gender')
        password = request.POST.get('password')

        # Check if the new username (mobile_num) already exists, and it is not the current staff member's username
        if User.objects.filter(username=mobile_num).exclude(pk=staff_id).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'edit_staff.html', {'staff': staff})  # Render the edit form with error message

        # Update staff details
        staff.first_name = fullname
        staff.username = mobile_num
        staff.last_name = gender
        staff.set_password(password)  # Use set_password() to hash the password
        staff.save()

        messages.success(request, 'Staff Edited!')
        return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'edit_staff.html', {'staff': staff})




def removeProduct(request, product_id):
    Products.objects.filter(id=product_id).delete()
    messages.success(request, 'Product Deleted!')
    
    return redirect(request.META.get('HTTP_REFERER'))



def editCategory(request, category_id):
    edit_category = Category.objects.get(pk=category_id)
    
    if request.method == 'POST':
        type = request.POST['type']
      
        edit_category.type = type
       
        edit_category.save()
        messages.success(request, 'Category Edited!')
    
    return redirect(request.META.get('HTTP_REFERER'))
        
def editProduct(request, product_id):
    edit_product = get_object_or_404(Products, pk=product_id)
    
    if request.method == 'POST':
        product_name = request.POST['product_name']
        category_name = request.POST['category']
        price = request.POST['price']
        quantity = request.POST['quantity']
        
        # Fetch the Category instance based on the category_name
        try:
            category_instance = Category.objects.get(type=category_name)
        except Category.DoesNotExist:
            messages.error(request, 'Category does not exist!')
            return redirect(request.META.get('HTTP_REFERER'))

        edit_product.name = product_name
        edit_product.category = category_instance
        edit_product.price = price
        edit_product.quantity = quantity
        edit_product.save()
        messages.success(request, 'Product Edited!')
    
    return redirect(request.META.get('HTTP_REFERER'))