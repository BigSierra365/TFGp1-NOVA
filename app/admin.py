"""
ARCHIVO: admin.py
DESCRIPCIÓN: Configuración del panel de administración de Django. 
            Personaliza la gestión del catálogo, incluyendo previsualización de imágenes, 
            filtros dinámicos de series por categoría y gestión de bundles in-line.
RELACIONES: 
    - Define la interfaz de gestión para todos los modelos en models.py.
    - Utiliza scripts de JavaScript personalizados en static/admin/js/ para lógica dinámica en el panel.
FLUJO: Interfaz de Administración. Permite a los gestores de contenido (revisores) 
       modificar la base de datos de PostgreSQL sin usar SQL.
"""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ChoiceField
from django.utils.html import format_html
from .models import Product, ProductImage, ProductBundle, BundleItem

# Mapeo de series por categoría de Producto
SERIES_MAP = {
    'Camera drone': [
        ('DJI Mavic',   'DJI Mavic'),
        ('DJI Mini',    'DJI Mini'),
        ('DJI Flip',    'DJI Flip'),
        ('DJI Avata',   'DJI Avata'),
        ('DJI Inspire', 'DJI Inspire'),
    ],
    'Portable': [
        ('Osmo Action',        'Osmo Action'),
        ('Osmo Pocket',        'Osmo Pocket'),
        ('Osmo Mobile',        'Osmo Mobile'),
        ('DJI Mic',            'DJI Mic'),
        ('Cámaras Ronin',      'Cámaras Ronin'),
        ('Estabilizadores Ronin', 'Estabilizadores Ronin'),
    ],
    # Energy se rellena automáticamente → no necesita choices
}

POWER_SERIE = 'DJI Power'   # serie fija para categoría Energy

#Imagenes de producto(se añadirán desde ProductAdmin)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src=\"{}\" style=\"max-height: 100px;\"/>', obj.image.url)
        return "No image"
    
    image_preview.short_description = 'Vista previa'

class ProductForm(ModelForm):
    # Definir explícitamente como ChoiceField para garantizar que se renderice como select
    series = ChoiceField(choices=[], required=False)
    
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Verificar que el campo series existe en el formulario
        if 'series' not in self.fields:
            return
            
        category = self.initial.get(
            "category",
            self.instance.category if self.instance and hasattr(self.instance, 'category') else None
        )

        # Ajusta dinámicamente el desplegable de series
        series_field = self.fields["series"]
        series_field.required = False  # Siempre no requerido
        
        if category in SERIES_MAP:
            series_field.choices = [('', '---------')] + SERIES_MAP[category]
        else:
            # Accessory u Energy: sin elección
            series_field.choices = [('', '---------')]
            
        # Establecer el valor actual si existe
        if self.instance and self.instance.series:
            series_field.initial = self.instance.series

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        series   = cleaned.get("series")

        # Validaciones según categoría

        if category == "Energy":
            cleaned["series"] = POWER_SERIE  # Fuerza automáticamente
        elif category == "Accessory":
            cleaned["series"] = None         # Serie vacía en accesorios

        return cleaned

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    inlines = [ProductImageInline]
    list_display = ['name', 'category', 'series', 'price', 'stock', 'is_active', 'created_at','card_image_preview', 'display_images']
    
    class Media:
        js = ('admin/js/category_series.js',)
    
    def card_image_preview(self, obj):
        if obj.card_image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.card_image.url)
        return "No image"
    card_image_preview.short_description = 'Card Image'
    
    def display_images(self, obj):
        images = obj.images.all()[:3]
        return format_html(' '.join(
            f'<img src="{img.image.url}" style="max-height: 50px; margin-right: 5px;"/>' 
            for img in images if img.image
        ))
    display_images.short_description = 'Imágenes'

    fieldsets = [
        ('Información Básica', {
            'fields': ['name', 'slug', 'description','procuct_details','slogan', 'price', 'stock', 'category', 'series', 'card_image', 'carousel_image', 'is_active']
        }),
        ('Multimedia', {
            'fields': ['video'],
            'classes': ['collapse']
        }),
        ('Relaciones', {
            'fields': ['compatible_with'],
            'classes': ['collapse']
        }),
    ]
    filter_horizontal = ['compatible_with']


class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 1
    verbose_name = "Producto incluido"
    verbose_name_plural = "Productos incluidos"

@admin.register(ProductBundle)
class ProductBundleAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_product', 'price', 'is_active', 'display_included_products')
    list_filter = ('is_active', 'main_product')
    search_fields = ('name', 'description', 'main_product__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BundleItemInline]
    fieldsets = (
        ('Información del Bundle', {
            'fields': ('name', 'slug', 'description', 'price', 'is_active', 'image')
        }),
        ('Producto Principal', {
            'fields': ('main_product',)
        }),
    )
    class Media:
        js = ("js/admin/toggle_series.js",)
        
    def display_included_products(self, obj):
        items = obj.bundle_items.all()
        if not items:
            return "-"
        return ", ".join([f"{item.quantity}x {item.product.name}" for item in items])
    display_included_products.short_description = 'Productos Incluidos'

     

from .models import Product, ProductImage, ProductBundle, BundleItem, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'bio',)
    search_fields = ('user__username', 'bio')
