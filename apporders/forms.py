from django import forms
from django.contrib.auth.models import User

from django.utils.translation import gettext_lazy as _

from apptasks.models import Task
from .models import Order, OrderInCheck, OrderFavourites, OrderLike

class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('user', 'task',)
        widgets = {
            'user': forms.HiddenInput(),
            'task': forms.HiddenInput(),
        }

    def clean_task(self):
        task = self.cleaned_data['task']
        if not task or not Task.objects.filter(id=task.id).exists():
            raise forms.ValidationError(_('Задача удалена пользователем'))
        return task

class OrderUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ('code_url', 'build_url',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code_url'].widget.attrs.update({'id': 'code_url', 'class': 'form-control mt-2', 'placeholder': _('Ссылка на исходники')})
        self.fields['build_url'].widget.attrs.update({'id': 'build_url', 'class': 'form-control mt-2', 'placeholder': _('Ссылка на публикацию решения'), 'required': True})

class OrderStatusUpdateForm(forms.Form):
    pass
    # class Meta:
    #     model = Order
    #     fields = ('status',)
    #     widgets = {
    #         'status': forms.HiddenInput(),
    #     }
    
class OrderInCheckCreationForm(forms.Form):
    pass

# class OrderInCheckCreationForm(forms.ModelForm):
#     class Meta:
#         model = OrderInCheck
#         fields = ('user', 'order',)
#         widgets = {
#             'user': forms.HiddenInput(),
#             'order': forms.HiddenInput(),
#         }

#     def clean_user(self):
#         user = self.cleaned_data['user']
#         if not user or not User.objects.filter(id=user.id).exists():
#             raise forms.ValidationError('Пользователь удалился с сайта')
#         return user

#     def clean_order(self):
#         order = self.cleaned_data['order']
#         if not order or not Order.objects.filter(id=order.id).exists():
#             raise forms.ValidationError('Решение удалено пользователем')
#         return order

class OrderInCheckUpdateForm(forms.ModelForm):
    
    check_confirm = forms.BooleanField(label='check_confirm', widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}))
    class Meta:
        model = OrderInCheck
        fields = ('user', 'order', 'comment',)
        widgets = {
            'user': forms.HiddenInput(),
            'order': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'placeholder': _('Общий комментарий к работе ...'), 'rows': '3', 'class': 'form-control'}),
        }

class FavouriteUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderFavourites
        fields = ('order',)
        widgets = {
            'order': forms.HiddenInput(attrs={'id':'favouriteUpdateFormOrderID'}),
        }

class LikeUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderLike
        fields = ('order',)
        widgets = {
            'order': forms.HiddenInput(attrs={'id':'likeUpdateFormOrderID'}),
        }

# class TaskDetailOrderCreateFormPOST(forms.Form):
#     pass


# class TaskDetailOrderUpdateFormPOST(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ('status',)
#         widgets = {
#             'status': forms.HiddenInput(),
#         }

# class TaskDetailUserSolutionPOST(forms.Form):
#     pass

# class OrderInCheckUpdateFormPOST(forms.Form):
#     pass