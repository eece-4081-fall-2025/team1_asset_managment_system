from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.urls import reverse_lazy
from .models import Asset, Attribute
from .forms import AssetForm, AssetAttributeFormSet


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "asset_managment/templates/asset_list.html"
    context_object_name = "assets"


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = "asset_managment/templates/asset_detail.html"
    context_object_name = "asset"


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "asset_managment/templates/asset_form.html"
    success_url = reverse_lazy("asset_list")

    def form_valid(self, form):
        self.object = form.save()

        formset = AssetAttributeFormSet(
            self.request.POST, self.request.FILES, instance=self.object
        )

        if formset.is_valid():
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class AssetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "asset_managment/templates/asset_form.html"
    success_url = reverse_lazy("asset_list")

    def form_valid(self, form):
        self.object = form.save()

        formset = AssetAttributeFormSet(
            self.request.POST, self.request.FILES, instance=self.object
        )

        if formset.is_valid():
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class AssetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Asset
    template_name = "asset_managment/templates/asset_confirm_delete.html"
    success_url = reverse_lazy("asset_list")


@LoginRequiredMixin
def assign_asset_view(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == "POST":
        asset.status = "assigned"
        asset.save()

        return redirect("asset_detail", pk=pk)

    return render(request, "inventory/assign_asset_form.html", {"asset": asset})
