from django.shortcuts import render
from .views import BaseView

def about_us(request):
    """
    Vista para la página 'Conócenos'
    """
    base_view = BaseView()
    context = base_view.get_context_data()
    return render(request, 'about_us.html', context)


def privacy_policy(request):
    """
    Vista para la página 'Políticas de Privacidad'
    """
    base_view = BaseView()
    context = base_view.get_context_data()
    return render(request, 'privacy_policy.html', context)
