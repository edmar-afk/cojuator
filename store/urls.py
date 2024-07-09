from django.urls import path
from . import views


urlpatterns = [
    path('userLogin', views.userLogin, name='userLogin'),
    path('logoutUser', views.logoutUser, name='logoutUser'),
        
    path('staff', views.staff, name='staff'),
    path('homepageMonthly', views.homepageMonthly, name='homepageMonthly'),
    path('homepage', views.homepage, name='homepage'),
    path('checkoutHistory', views.checkoutHistory, name='checkoutHistory'),
    path('checkout', views.checkout, name='checkout'),
    path('products', views.products, name='products'),
    path('category', views.category, name='category'),
    
    
    path('<int:staff_id>/editStaff/', views.editStaff, name='editStaff'),
    path('<int:staff_id>/removeStaff/', views.removeStaff, name='removeStaff'),
    path('<int:product_id>/removeProduct/', views.removeProduct, name='removeProduct'),
    path('<int:category_id>/removeCategory/', views.removeCategory, name='removeCategory'),
    path('<int:category_id>/editCategory/', views.editCategory, name='editCategory'),
    path('<int:product_id>/editProduct/', views.editProduct, name='editProduct'),
]