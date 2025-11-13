from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Asset, Attribute
from .forms import AssetForm, AssetAttributeFormSet


class CustomLoginView(LoginView):
    """
    Epic 4, Story 23: Login feature to track activity
    """
    template_name = 'asset_managment/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('asset_list')


class AssetListView(LoginRequiredMixin, ListView):
    """
    Epic 1, Stories 2-4: Asset list with search and filtering
    """
    model = Asset
    template_name = "asset_managment/asset_list.html"
    context_object_name = "assets"
    
    def get_queryset(self):
        queryset = Asset.objects.all().order_by('-created_at')
        
        # Search functionality (Epic 1, Story 4)
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(id__icontains=search_query) |
                Q(category__icontains=search_query)
            )
        
        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unique categories for filter dropdown
        context['categories'] = Asset.objects.values_list('category', flat=True).distinct()
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    """
    Epic 1, Stories 5, 8, 9: View asset details with attributes
    """
    model = Asset
    template_name = "asset_managment/asset_detail.html"
    context_object_name = "asset"


class AssetCreateView(LoginRequiredMixin, CreateView):
    """
    Epic 1, Story 3: Add new asset with unique ID
    Epic 1, Story 10: Add attributes to assets
    """
    model = Asset
    form_class = AssetForm
    template_name = "asset_managment/asset_form.html"
    success_url = reverse_lazy("asset_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = AssetAttributeFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = AssetAttributeFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    """
    Epic 1, Story 5: Edit asset details
    Epic 1, Story 6: Duplicate functionality through editing
    """
    model = Asset
    form_class = AssetForm
    template_name = "asset_managment/asset_form.html"
    
    def get_success_url(self):
        return reverse_lazy('asset_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = AssetAttributeFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['formset'] = AssetAttributeFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    """
    Epic 1, Story 7: Delete outdated or retired assets
    """
    model = Asset
    template_name = "asset_managment/asset_confirm_delete.html"
    success_url = reverse_lazy("asset_list")


@login_required
def assign_asset_view(request, pk):
    """
    Epic 4, Story 22: Assign assets to individuals
    """
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        if user_id:
            from django.contrib.auth.models import User
            user = get_object_or_404(User, pk=user_id)
            asset.assigned_to = user
            asset.status = "checked_out"
            asset.save()
            return redirect("asset_detail", pk=pk)

    return render(request, "asset_managment/assign_asset_form.html", {"asset": asset})