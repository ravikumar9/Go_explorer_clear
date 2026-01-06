from django.shortcuts import render
from django.views.generic import TemplateView
from hotels.models import Hotel
from buses.models import Bus
from packages.models import Package
from core.models import City


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show full city list in the search dropdown so users can find any destination
        context['popular_cities'] = City.objects.all().order_by('name')
        context['featured_hotels'] = Hotel.objects.filter(is_featured=True)[:6]
        context['featured_packages'] = Package.objects.filter(is_active=True)[:4]
        return context


class AboutView(TemplateView):
    """About page view"""
    template_name = 'about.html'


class ContactView(TemplateView):
    """Contact page view"""
    template_name = 'contact.html'
