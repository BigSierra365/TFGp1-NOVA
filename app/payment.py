"""
ARCHIVO: payment.py
DESCRIPCIÓN: Módulo de integración con la pasarela de pagos Stripe. 
            Gestiona la creación de sesiones de checkout y los retornos (éxito/cancelación).
RELACIONES: 
    - Invocado por las rutas definidas en urls.py.
    - Consume el estado actual del carrito a través de cart.py.
    - Utiliza las API Keys configuradas en settings.py.
FLUJO: Módulo de Integración Externa. Transforma los datos del carrito local en un formato 
       que la API de Stripe pueda procesar para la transacción.
"""
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .cart import Cart

# Configurar la API key de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_process(request):
    cart = Cart(request)
    
    # Si el carrito está vacío, redirige a la página del carrito
    if cart.count() == 0:
        return redirect('shopping_cart')
    
    # Crear un objeto checkout session de Stripe
    success_url = request.build_absolute_uri(reverse('payment_success'))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
    
    # Preparar los items para Stripe
    line_items = []
    for item in cart.items():
        # Si el item es un bundle, usa su información
        if item.get('type') == 'bundle':
            # Preparar datos del producto para el bundle
            product_data = {
                'name': item['bundle'].name
            }
            
            # Agregar descripción solo si no está vacía
            if hasattr(item['bundle'], 'description') and item['bundle'].description:
                product_data['description'] = item['bundle'].description[:255]
            
            # Agregar imágenes si existen
            if hasattr(item['bundle'], 'thumbnail') and item['bundle'].thumbnail:
                product_data['images'] = [request.build_absolute_uri(item['bundle'].thumbnail.url)]
            
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': product_data,
                    'unit_amount': int(float(item['price']) * 100),  # Stripe requiere céntimos
                },
                'quantity': item['quantity'],
            })
        # Si es un accesorio
        elif item.get('type') == 'accessory':
            # Preparar datos del producto para el accesorio
            product_data = {
                'name': item['product'].name
            }
            
            # Agregar descripción solo si no está vacía
            if hasattr(item['product'], 'description') and item['product'].description:
                product_data['description'] = item['product'].description[:255]
            
            # Agregar imágenes si existen
            if hasattr(item['product'], 'card_image') and item['product'].card_image:
                product_data['images'] = [request.build_absolute_uri(item['product'].card_image.url)]
            
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': product_data,
                    'unit_amount': int(float(item['price']) * 100),  # Stripe requiere céntimos
                },
                'quantity': item['quantity'],
            })
    
    # Crear la sesión de Stripe
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            # Añadir más opciones de personalización
            billing_address_collection='auto',
            locale='es',
            # Configurar una URL directa para el cliente
        )
        
        # Redireccionar directamente a la página de pago de Stripe en lugar de mostrar una página intermedia
        return redirect(session.url)
    
    except Exception as e:
        return render(request, 'payment/error.html', {'error': str(e)})

def payment_success(request):
    cart = Cart(request)
    # Limpiar el carrito después de un pago exitoso
    cart.clear()
    return render(request, 'payment/success.html')

def payment_cancel(request):
    return render(request, 'payment/cancel.html')
