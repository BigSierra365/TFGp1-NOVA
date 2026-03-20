from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from . import payment
from . import info_views

# Configuración del router
router = DefaultRouter()
# router.register(r'tu-modelo', TuVistaViewSet)

#app_name = 'accounts'

urlpatterns = [
    # Página de inicio
    path('', views.home, name='home'),
    
    # Lista de productos por categoría
    path('productos/drones-camara/', views.camera_drones, name='camera_drones'),
    path('productos/portatiles/', views.portable_products, name='portable_products'),
    path('productos/energia/', views.energy_products, name='energy_products'),
    path('productos/accesorios/', views.accessories_list, name='accessories'),
    
    # Detalle del producto
    path('productos/<slug:slug>/', views.product_detail, name='product_detail'),
    path('productos/<slug:slug>/update-prices/', views.product_price_update, name='product_price_update'),
    
    #Busqueda de productos
    #path('productos/search/', views.product_search, name='product_search'),
    path('ajax/product-search/', views.product_search, name='product_search'),

    #Gestión de usuarios
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/delete/', views.DeleteAccountView.as_view(), name='delete_account'),

    # Password change
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Password reset
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    #carrito
    path("cart/", views.shopping_cart_view, name="shopping_cart"),
    path("cart/update/", views.cart_update_quantity_view, name="cart_update"), 
    path("cart/remove/", views.cart_remove_view, name="cart_remove"),
    path('cart/add/<int:product_id>/', views.cart_add_view, name='cart_add_view'),
    
    # Pasarela de pago Stripe
    path('payment/process/', payment.payment_process, name='payment_process'),
    path('payment/success/', payment.payment_success, name='payment_success'),
    path('payment/cancel/', payment.payment_cancel, name='payment_cancel'),

    # Páginas informativas
    path('conocenos/', info_views.about_us, name='about_us'),
    path('politicas-privacidad/', info_views.privacy_policy, name='privacy_policy'),

] + router.urls
