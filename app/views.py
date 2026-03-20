"""
ARCHIVO: views.py
DESCRIPCIÓN: Controlador principal de la aplicación. 
            Contiene la lógica de procesamiento para el catálogo, gestión de usuarios, 
            detalles de producto y operaciones del carrito de compras.
RELACIONES: 
    - Orquesta datos provenientes de models.py.
    - Utiliza forms.py para validación de entradas de usuario.
    - Renderiza las plantillas en /templates/.
    - Se apoya en cart.py para la lógica de persistencia de sesión del carrito.
FLUJO: V (View) del patrón MVT. Recibe peticiones HTTP, consulta la base de datos y retorna respuestas (HTML o JSON).
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, CreateView, TemplateView, UpdateView, DeleteView, ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.manager import BaseManager
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from .forms import RegisterForm, ProfileForm, UserProfileForm, CustomPasswordChangeForm
from .models import * 
from decimal import Decimal
from collections import OrderedDict
from django.views.decorators.http import require_POST
from .cart import Cart

# #############################################################################
# SECCIÓN: CLASES BASE Y NAVEGACIÓN
# #############################################################################

# Add type hint for Product.objects
ProductManager = BaseManager.from_queryset(Product.objects.none().__class__)  # type: ignore

class BaseView(View):
    # Add type hint for Product.objects
    objects: ProductManager = Product.objects  # type: ignore
    
    def get_context_data(self, **kwargs):
        """
        Base context for all views that need product categories in the navbar
        
        Args:
            **kwargs: Additional context data
        """
        context = kwargs  # Use any passed in kwargs
        # Get 4 products from each category for the dropdowns
        context['camera_drones'] = self.objects.filter(
            category='Camera drone',
            is_active=True
        ).prefetch_related('images')[:4]
        
        context['portable_products'] = self.objects.filter(
            category='Portable',
            is_active=True
        ).prefetch_related('images')[:4]
        
        return context

from collections import OrderedDict
from django.shortcuts import render
from .models import Product
from .views import BaseView

def home(request):
    base_view = BaseView()
    context = base_view.get_context_data()

    # Tu lógica existente
    qs = (Product.objects
            .filter(is_active=True)
            .exclude(category='Accessory')
            .select_related()
            .prefetch_related('images')
            .order_by('category', 'series', 'created_at'))
    first_per_group = OrderedDict()
    for p in qs:
        key = (p.category, p.series or '')
        if key not in first_per_group:
            first_per_group[key] = p
    slides = []
    for p in first_per_group.values():
        img_url = p.carousel_image.url if p.carousel_image else (p.images.first().image.url if p.images.exists() else '')
        slides.append({
            'name': p.name,
            'slogan': p.slogan,
            'slug': p.slug,
            'product_details': p.procuct_details,
            'image': img_url,
        })
    context['slides'] = slides

    context['products_no_accesory'] = Product.objects \
    .filter(is_active=True) \
    .exclude(category='Accessory') \
    .select_related() \
    .prefetch_related('images')

    return render(request, 'home.html', context)




###
# Vista de página de drones con cámara
###
def get_products_by_category(request, category, category_name, template_name):
    # Get all unique series for the category
    series = Product.objects.filter(
        category=category,
        is_active=True,
        series__isnull=False
    ).order_by('series').values_list('series', flat=True).distinct()
    
    # Get selected series from query params
    selected_series = request.GET.get('series')
    
    # Filter products
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).prefetch_related('images')
    
    # Apply series filter if selected
    if selected_series:
        products = products.filter(series=selected_series)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    # Get base context
    base_view = BaseView()
    context = base_view.get_context_data()
    
    # Add category specific context
    context.update({
        'products': products,
        'all_series': series,
        'selected_series': selected_series,
        'page_title': category_name,
        'current_category': category
    })
    
    return render(request, f'products/{template_name}', context)

#LISTADO DE DRONES
def camera_drones(request):
    return get_products_by_category(
        request, 
        category='Camera drone', 
        category_name='Drones con Cámara',
        template_name='camera_drones.html'
    )

#LISTADO DE DPRODUCTOS PORTATILES
def portable_products(request):
    return get_products_by_category(
        request,
        category='Portable',
        category_name='Productos Portátiles',
        template_name='portable_products.html'
    )

#LISTADO DE ENERGIA
def energy_products(request):
    return get_products_by_category(
        request,
        category='Energy',
        category_name='Sistemas de Energía',
        template_name='energy_products.html'
    )

###
#Vista dinámica de los detalles de un producto
###

def product_detail(request, slug):
    # Obtén el producto base
    product = get_object_or_404(
        Product.objects.prefetch_related('bundles_as_main__bundle_items', 'accessories'),
        slug=slug, is_active=True
    )

    # Valores por defecto para la vista
    selected_bundle = None
    accessory_quantities = {}
    bundle_price = 0
    accessories_price = 0
    total_price = float(product.price)  # fallback: precio base (aunque lo ignoras luego)

    if request.method == 'POST':
        # 1) Bundle seleccionado
        bundle_id = request.POST.get('bundle')
        if bundle_id:
            selected_bundle = get_object_or_404(ProductBundle, pk=bundle_id)
            bundle_price = float(selected_bundle.price)

        # 2) Cantidades de accesorios
        for acc in product.accessories.all():
            qty = int(request.POST.get(f'acc_{acc.id}', 0))
            if qty > 0:
                accessory_quantities[acc.id] = {
                    'name': acc.name,
                    'price': float(acc.price),
                    'qty': qty,
                }
                accessories_price += float(acc.price) * qty

        # 3) Total
        total_price = bundle_price + accessories_price

    context = {
        'product': product,
        'related_products': Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4],
        # Datos de selección
        'selected_bundle': selected_bundle,
        'accessory_quantities': accessory_quantities,
        # Precios
        'bundle_price': bundle_price,
        'accessories_price': accessories_price,
        'total_price': total_price,
    }
    return render(request, 'products/product_detail.html', context)

#detalles del producto actualizar precios
def product_price_update(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('bundles_as_main__bundle_items__product'),
        slug=slug, is_active=True
    )

    bundle_price = 0.0
    items_data   = []
    bundle_id = request.GET.get('bundle')
    if bundle_id:
        bundle = get_object_or_404(ProductBundle, pk=bundle_id)
        bundle_price = float(bundle.price)
        for bi in bundle.bundle_items.all():
            items_data.append({
                "name": bi.product.name,
                "qty": bi.quantity,
                # usar build_absolute_uri para URL completa:
                "image": request.build_absolute_uri(bi.product.card_image.url)
            })

    # calcula también accesorios si los envías por GET…
    accessories_price = 0.0
    for key, vals in request.GET.lists():
        if key.startswith('acc_'):
            qty = int(vals[-1]) if vals else 0
            if qty > 0:
                acc = product.accessories.get(pk=int(key.split('_')[1]))
                accessories_price += float(acc.price) * qty

    total = bundle_price + accessories_price

    return JsonResponse({
        "bundle_price": f"{bundle_price:.2f}",
        "total":        f"{total:.2f}",
        "items":        items_data,
    })

#Listado de Accesorios
def accessories_list(request):
    # Mapeo código → etiqueta para desplegar
    CATEGORIES = {
        'Camera drone': 'Drones con Cámara',
        'Portable': 'Productos Portátiles',
        'Energy': 'Sistemas de Energía'
    }
    
    # Extrae series por categoría
    categories_with_series = []
    for code, label in CATEGORIES.items():
        series = list(
            Product.objects
                   .filter(category=code, is_active=True, series__isnull=False)
                   .order_by('series')
                   .values_list('series', flat=True)
                   .distinct()
        )
        categories_with_series.append({
            'code': code,
            'label': label,
            'series': series
        })
    
    selected_category = request.GET.get('category')
    selected_series   = request.GET.get('series')
    
    # Empieza por todos los accesorios
    accessories = Product.objects.filter(
        category='Accessory',
        is_active=True
    ).prefetch_related('images', 'compatible_with')
    
    # Aplica filtro por categoría
    if selected_category:
        accessories = accessories.filter(
            compatible_with__category=selected_category
        )
    # Aplica filtro adicional por serie
    if selected_series:
        accessories = accessories.filter(
            compatible_with__series=selected_series
        )
    
    # Elimina duplicados
    accessories = accessories.distinct()
    
    # Contexto para el template
    base_view = BaseView()
    context = base_view.get_context_data()
    context.update({
        'categories_with_series': categories_with_series,
        'selected_category': selected_category,
        'selected_series': selected_series,
        'selected_category_label': CATEGORIES.get(selected_category, ''),
        'accessories': accessories,
        'page_title': 'Accesorios'
    })
    return render(request, 'products/accessories.html', context)

# Buscador de productos navbar
@require_GET
def product_search(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse([], safe=False)
    matches = Product.objects.filter(name__icontains=q, is_active=True).exclude(category='Accessory')[:10]
    data = [
        {'name': p.name, 'slug': p.slug}
        for p in matches
    ]
    return JsonResponse(data, safe=False)

################
#Gestión de usuarios
################
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registro exitoso. ¡Bienvenido!')
        return redirect('profile')
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

class EditProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get(self, request, *args, **kwargs):
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, *args, **kwargs):
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect(self.success_url)
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

class DeleteAccountView(LoginRequiredMixin, DeleteView):
    template_name = 'accounts/delete_account.html'
    success_url = reverse_lazy('register')

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tu cuenta ha sido eliminada.')
        logout(request)
        return super().delete(request, *args, **kwargs)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        messages.success(self.request, 'Contraseña cambiada con éxito.')
        return super().form_valid(form)

class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/email/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

###############
#carrito
###############

def shopping_cart_view(request):
    cart = Cart(request)
    return render(request, "cart/shopping_cart.html", {
        "items": cart.items(),
        "total": cart.total_price(),
        "cart_count": cart.count()
    })

@require_POST
def cart_remove_view(request):
    item_type = request.POST.get('type') # 'bundle' o 'accessory'
    item_id = request.POST.get('id')    # ID del item
    
    if not item_type or not item_id:
        return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
    cart = Cart(request)
    cart.remove(item_type, item_id)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.count(),
            'cart_total': f"{cart.total_price():.2f}"  
        })
    
    return redirect('shopping_cart')

@require_POST
def cart_update_quantity_view(request):
    item_type = request.POST.get('type') # 'bundle' o 'accessory'
    item_id = request.POST.get('id')     # ID del item
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    if not item_type or not item_id:
        return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
    cart = Cart(request)
    cart.update_quantity(item_type, item_id, quantity)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.count(),
            'cart_total': f"{cart.total_price():.2f}",
            'item_subtotal': f"{quantity * float(request.POST.get('price', 0)):.2f}"
        })
    
    return redirect('shopping_cart')

@require_POST
def cart_add_view(request, product_id):
    # Verificar si se añade un bundle
    bundle = None
    bundle_id = request.POST.get('bundle')
    if bundle_id:
        try:
            bundle = ProductBundle.objects.get(id=bundle_id, is_active=True)
        except ProductBundle.DoesNotExist:
            bundle = None

    # Verificar si se añaden accesorios
    accessory = None
    if not bundle:
        try:
            accessory = Product.objects.get(id=product_id, category='Accessory', is_active=True)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    
    # Obtener cantidad
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Añadir al carrito
    cart = Cart(request)
    
    if bundle:
        cart.add(bundle=bundle, quantity=quantity)
    elif accessory:
        cart.add(product=accessory, quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.count(),
            'cart_total': f"{cart.total_price():.2f}"
        })
        
    return redirect('shopping_cart')
