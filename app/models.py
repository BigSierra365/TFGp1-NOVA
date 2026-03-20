"""
ARCHIVO: models.py
DESCRIPCIÓN: Definición del esquema de base de datos (PostgreSQL). 
            Contiene la lógica de negocio core: Productos, Packs (Bundles), Usuarios y Carrito persistente.
RELACIONES: 
    - Consumido por views.py para consultas (ORMs).
    - Administrado vía admin.py para gestión de catálogo.
    - Referenciado en cart.py para la persistencia del carrito.
FLUJO: M (Model) del patrón MVT. Define cómo se estructuran los datos antes de ser procesados por las Vistas.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import re
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# #############################################################################
# SECCIÓN: PRODUCTOS Y MULTIMEDIA
# Propósito: Almacenar el catálogo base, incluyendo drones, portátiles y accesorios.
# #############################################################################

################
#Productos
################
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    procuct_details = models.TextField(blank=True)
    slogan = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=[
        ('Camera drone', 'Drone con cámara'),
        ('Portable', 'Producto portátil'),
        ('Energy', 'Energía'),
        ('Accessory', 'Accesorio')
    ])
    card_image = models.ImageField(upload_to='images/product_images/',blank=True)
    carousel_image = models.ImageField(upload_to='images/product_images/',blank=True)
    series = models.CharField(max_length=50, blank=True, null=True)
    video = models.URLField(max_length=500, blank=True, null=True, help_text="Pega aquí la URL embebible de YouTube/Vimeo")
    @property
    def video_embed_url(self):
        """
        Devuelve la URL lista para el iframe (<iframe src="…">).
        """
        import re
        if not self.video:
            return ''
        m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]+)', self.video)
        if m:
            return f'https://www.youtube.com/embed/{m.group(1)}'
        if 'embed/' in self.video:
            return self.video
        return self.video
    compatible_with = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='accessories') # Campo para asignar con qué producto es compatible un producto de tipo accesorio
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} {self.slug} {self.description} {self.price} {self.category} {self.stock} {self.is_active} {self.created_at} {self.updated_at}"

    # Remove the clean method since validation is handled in admin.py

################
#Img de productos
################
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/product_images/')
    order = models.PositiveIntegerField(default=1, )
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Imagen de {self.product.name}"

################
#Packs de productos
################
class ProductBundle(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    # Producto principal (solo uno)
    main_product = models.ForeignKey(Product, related_name='bundles_as_main', on_delete=models.CASCADE)
    # Mantengamos el ManyToManyField original para compatibilidad con código existente
    included_products = models.ManyToManyField(Product, related_name='bundles_included')
    image = models.ImageField(upload_to='images/bundles/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bundle"
        verbose_name_plural = "Bundles"

    def __str__(self) -> str:
        return f"{self.name} (para {self.main_product.name})"

################
# Elementos de pack de productos
################
class BundleItem(models.Model):
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE, related_name='bundle_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bundle_items_as_product')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    
    class Meta:
        verbose_name = "Elemento del bundle"
        verbose_name_plural = "Elementos del bundle"
        unique_together = ('bundle', 'product')  # Evita duplicar productos en un mismo bundle
    
    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"

###
#usuarios
###
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Si quisieras un email separado: 
    # email = models.EmailField(unique=True, blank=True, null=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

# Crear/guardar perfil al crear usuario
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

##
#Carrito
###
class CartModel(models.Model):
    user = models.OneToOneField(
            settings.AUTH_USER_MODEL, 
            on_delete=models.CASCADE,
            null=True, blank=True
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}"
        else:
            return f"Carrito de sesión {self.session_key[:8] if self.session_key else ''}"
    
    def total_items(self):
        bundle_count = sum(item.quantity for item in self.bundle_items.all())
        accessory_count = sum(item.quantity for item in self.accessory_items.all())
        return bundle_count + accessory_count
    
    def total_price(self):
        bundle_total = sum(item.subtotal() for item in self.bundle_items.all())
        accessory_total = sum(item.subtotal() for item in self.accessory_items.all())
        return bundle_total + accessory_total

class CartBundleItem(models.Model):
    cart = models.ForeignKey(
            CartModel, 
            on_delete=models.CASCADE,
            related_name='bundle_items'
        )
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x Bundle: {self.bundle.name} en {self.cart}"
    
    def subtotal(self):
        return self.quantity * self.bundle.price

class CartAccessoryItem(models.Model):
    cart = models.ForeignKey(
            CartModel, 
            on_delete=models.CASCADE,
            related_name='accessory_items'
        )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} en {self.cart}"
    
    def subtotal(self):
        return self.quantity * self.product.price
