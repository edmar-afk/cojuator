from django.urls import path
from . import views


urlpatterns = [
    
    path('homepageMonthly', views.homepageMonthly, name='homepageMonthly'),
    path('homepage', views.homepage, name='homepage'),
    path('checkoutHistory', views.checkoutHistory, name='checkoutHistory'),
    path('checkout', views.checkout, name='checkout'),
    path('products', views.products, name='products'),
    path('category', views.category, name='category'),
    
    path('<int:product_id>/removeProduct/', views.removeProduct, name='removeProduct'),
    path('<int:category_id>/removeCategory/', views.removeCategory, name='removeCategory'),
    path('<int:category_id>/editCategory/', views.editCategory, name='editCategory'),
    path('<int:product_id>/editProduct/', views.editProduct, name='editProduct'),
]