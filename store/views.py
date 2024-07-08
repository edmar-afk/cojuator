from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth import authenticate, login
from django.db.models import Q
from .models import Products, Category, SoldItems
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Max
today = timezone.now().date()
from dateutil.relativedelta import relativedelta
# Create your views here.


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
    
    # Current day (last 24 hours)
    # Current day (last 24 hours)
    current_date_start = timezone.now() - timedelta(days=1)
    current_date_end = timezone.now()
    current_history = SoldItems.objects.filter(sold_date__gte=current_date_start, sold_date__lt=current_date_end).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Previous day (24 to 48 hours ago)
    day_two_start = timezone.now() - timedelta(days=2)
    day_two_end = timezone.now() - timedelta(days=1)
    day_two_history = SoldItems.objects.filter(sold_date__gte=day_two_start, sold_date__lt=day_two_end).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Day before previous day (48 to 72 hours ago)
    day_three_start = timezone.now() - timedelta(days=3)
    day_three_end = timezone.now() - timedelta(days=2)
    day_three_history = SoldItems.objects.filter(sold_date__gte=day_three_start, sold_date__lt=day_three_end).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Day 4 (72 to 96 hours ago)
    day_four_start = timezone.now() - timedelta(days=4)
    day_four_end = timezone.now() - timedelta(days=3)
    day_four_history = SoldItems.objects.filter(sold_date__gte=day_four_start, sold_date__lt=day_four_end).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Day 5 (96 to 120 hours ago)
    day_five_start = timezone.now() - timedelta(days=5)
    day_five_end = timezone.now() - timedelta(days=4)
    day_five_history = SoldItems.objects.filter(sold_date__gte=day_five_start, sold_date__lt=day_five_end).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Day 6 (120 to 144 hours ago)
    day_six_start = timezone.now() - timedelta(days=6)
    day_six_end = timezone.now() - timedelta(days=5)
    day_six_history = SoldItems.objects.filter(sold_date__gte=day_six_start, sold_date__lt=day_six_end).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Day 7 (144 to 168 hours ago)
    day_seven_start = timezone.now() - timedelta(days=7)
    day_seven_end = timezone.now() - timedelta(days=6)
    day_seven_history = SoldItems.objects.filter(sold_date__gte=day_seven_start, sold_date__lt=day_seven_end).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
   
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
        
        
        'current_history': current_history,
        'day_two_history': day_two_history,
        'day_three_history': day_three_history,
        'day_four_history': day_four_history,
        'day_five_history': day_five_history,
        'day_six_history': day_six_history,
        'day_seven_history': day_seven_history,
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