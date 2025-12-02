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
from django.contrib.auth.models import Group

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
        user = self.request.user
        queryset = Asset.objects.all().order_by('-created_at')
        if not user.is_superuser and not user.is_staff:
            queryset.filter(assigned_to=user)
        
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
        user = self.request.user
        # Get unique categories for filter dropdown
        context['categories'] = Asset.objects.values_list('category', flat=True).distinct()
        
        # Get the queryset (already filtered by security in get_queryset if you did that)
        assets_temp = context['assets']
        assets = []
        for a in assets_temp:
            if a.has_access(user):
                assets.append(a)


         
        context['assets'] = assets
        return context

class AssetDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Epic 1, Stories 5, 8, 9: View asset details with attributes
    """
    model = Asset
    template_name = "asset_managment/asset_detail.html"
    context_object_name = "asset"
    def test_func(self):
        asset = self.get_object() 
        return asset.has_access(self.request.user)
    
    def test_func(self):
        asset = self.get_object() 
        return asset.has_access(self.request.user)
    

class AssetCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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
    
    def test_func(self):
        user = self.request.user

        if user.is_superuser:
            return True
        try:
            manager_group = Group.objects.get(name='manager')
            if manager_group in user.groups.all():
                return True
        except Group.DoesNotExist:
            pass 
        return False


class AssetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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
    
    def test_func(self):
        asset = self.get_object() 
        return asset.has_access(self.request.user)


class AssetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Epic 1, Story 7: Delete outdated or retired assets
    """
    model = Asset
    template_name = "asset_managment/asset_confirm_delete.html"
    success_url = reverse_lazy("asset_list")

    def test_func(self):
        asset = self.get_object() 
        return asset.has_access(self.request.user)


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

@login_required
def asset_duplicate_view(request, pk):
    """
    Epic 1, Story 6: Duplicate asset to simplify creating similar assets
    """
    # Get the original asset
    original_asset = get_object_or_404(Asset, pk=pk)
    
    if request.method == 'GET':
        # Create a form pre-filled with the original asset's data
        form = AssetForm(initial={
            'name': f"{original_asset.name} (Copy)",
            'category': original_asset.category,
            'status': original_asset.status,
            'depreciation': original_asset.depreciation,
            # Don't copy assigned_to - new asset should be unassigned
        })
        
        # Create empty formset for attributes
        formset = AssetAttributeFormSet()
        
        context = {
            'form': form,
            'formset': formset,
            'is_duplicate': True,
            'original_asset': original_asset,
        }
        return render(request, 'asset_managment/asset_form.html', context)
    
    elif request.method == 'POST':
        form = AssetForm(request.POST)
        formset = AssetAttributeFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Create the new asset
            new_asset = form.save()
            
            # Copy attributes from original asset
            for attr in original_asset.attributes_set.all():
                Attribute.objects.create(
                    asset=new_asset,
                    name=attr.name,
                    value=attr.value
                )
            
            # Also save any new attributes from formset
            formset.instance = new_asset
            formset.save()
            
            return redirect('asset_detail', pk=new_asset.pk)
        else:
            context = {
                'form': form,
                'formset': formset,
                'is_duplicate': True,
                'original_asset': original_asset,
            }
            return render(request, 'asset_managment/asset_form.html', context)