"""
ARCHIVO: cart.py
DESCRIPCIÓN: Lógica de abstracción del carrito de compras. 
            Maneja la transición entre carritos de sesión (anónimos) y carritos de base de datos (autenticados).
RELACIONES: 
    - Utilizado por views.py para gestionar el flujo de compra.
    - Interactúa directamente con CartModel y sus items en models.py.
FLUJO: Capa de Servicio / Ayudante. Actúa como puente entre la sesión del usuario (frontend/browser) 
       y la persistencia en la base de datos (backend).
"""
import uuid
from django.conf import settings
from .models import Product, ProductBundle, CartModel, CartBundleItem, CartAccessoryItem

# #############################################################################
# CLASE: Cart
# Propósito: Centralizar las operaciones de añadir, quitar y calcular totales.
# #############################################################################

class Cart:
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        self.session = request.session
        
        # Intentar obtener o crear el carrito para usuarios autenticados
        if self.user:
            self.cart_model, _ = CartModel.objects.get_or_create(user=self.user)
        else:
            # Carrito de sesión para usuarios anónimos
            session_key = self.session.session_key or self.session.create()
            try:
                self.cart_model = CartModel.objects.get(session_key=session_key)
            except CartModel.DoesNotExist:
                self.cart_model = CartModel.objects.create(
                    session_key=session_key
                )
    
    def add(self, product=None, quantity=1, bundle=None):
        """Añade un bundle o un accesorio al carrito"""
        if bundle:
            # Comprobar si ya existe este bundle en el carrito
            existing = self.cart_model.bundle_items.filter(bundle=bundle).first()
            if existing:
                existing.quantity += quantity
                existing.save()
            else:
                CartBundleItem.objects.create(
                    cart=self.cart_model,
                    bundle=bundle,
                    quantity=quantity
                )
        elif product and product.category == 'Accessory':
            # Comprobar si ya existe este accesorio en el carrito
            existing = self.cart_model.accessory_items.filter(product=product).first()
            if existing:
                existing.quantity += quantity
                existing.save()
            else:
                CartAccessoryItem.objects.create(
                    cart=self.cart_model,
                    product=product,
                    quantity=quantity
                )
    
    def update_quantity(self, item_type, item_id, quantity):
        """Actualiza la cantidad de un item del carrito"""
        if quantity < 1:
            return self.remove(item_type, item_id)
            
        if item_type == 'bundle':
            try:
                item = self.cart_model.bundle_items.get(id=item_id)
                item.quantity = quantity
                item.save()
            except CartBundleItem.DoesNotExist:
                pass
        elif item_type == 'accessory':
            try:
                item = self.cart_model.accessory_items.get(id=item_id)
                item.quantity = quantity
                item.save()
            except CartAccessoryItem.DoesNotExist:
                pass
    
    def remove(self, item_type, item_id):
        """Elimina un item del carrito"""
        if item_type == 'bundle':
            try:
                self.cart_model.bundle_items.filter(id=item_id).delete()
            except:
                pass
        elif item_type == 'accessory':
            try:
                self.cart_model.accessory_items.filter(id=item_id).delete()
            except:
                pass
    
    def clear(self):
        """Vacía el carrito"""
        self.cart_model.bundle_items.all().delete()
        self.cart_model.accessory_items.all().delete()
    
    def count(self):
        """Retorna el número total de items en el carrito"""
        return self.cart_model.total_items()
    
    def total_price(self):
        """Retorna el precio total del carrito"""
        return self.cart_model.total_price()
    
    def items(self):
        """Retorna todos los items del carrito"""
        items = []
        
        # Añadir bundles
        for bundle_item in self.cart_model.bundle_items.all():
            items.append({
                'id': bundle_item.id,
                'type': 'bundle',
                'bundle': bundle_item.bundle,
                'quantity': bundle_item.quantity,
                'price': bundle_item.bundle.price,
                'subtotal': bundle_item.subtotal()
            })
        
        # Añadir accesorios
        for acc_item in self.cart_model.accessory_items.all():
            items.append({
                'id': acc_item.id,
                'type': 'accessory',
                'product': acc_item.product,
                'quantity': acc_item.quantity,
                'price': acc_item.product.price,
                'subtotal': acc_item.subtotal()
            })
        
        return items