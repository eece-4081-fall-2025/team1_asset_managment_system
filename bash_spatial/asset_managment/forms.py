from django import forms
from django.forms.models import inlineformset_factory
from .models import Asset, Attribute


class AssetForm(forms.ModelForm):

    class Meta:
        model = Asset
        fields = [
            "name",
            "category",
            "status",
            "depreciation",
            "assigned_to",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Asset Name"}),
            "category": forms.TextInput(attrs={"placeholder": "Type"}),
            "depreciation": forms.DateInput(attrs={"placeholder": "10/10/2010"}),
        }


class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ["name", "value"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Serial Number, Purchase Date, etc."}
            ),
            "value": forms.TextInput(
                attrs={"placeholder": "The specific value of the attribute"}
            ),
        }


AssetAttributeFormSet = inlineformset_factory(
    parent_model=Asset,
    model=Attribute,
    form=AttributeForm,
    extra=1,
    can_delete=True,
)
