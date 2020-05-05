from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Task, Skill, TaskRatings, TaskLike


class FavouriteFormPOST(forms.Form):
    pass


class AddLikeForm(forms.ModelForm):
    class Meta:
        model = TaskLike
        fields = ('task',)
        widgets = {
            'task': forms.HiddenInput(attrs={'id':'addLikeFormTaskID'}),
        }


class SetRatingForm(forms.ModelForm):
    class Meta:
        model = TaskRatings
        fields = ('task',)
        widgets = {
            'task': forms.HiddenInput(attrs={'id':'setRatingFormTaskID'}),
        }


class TaskUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Task
        fields = ('title', 'skill', 'extra_skill1', 'extra_skill2', 'extra_skill3')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'id': 'task_title', 'class': 'form-control', 'placeholder': _('Название задачи'), 'value': ''})
        self.fields['skill'].widget.attrs.update({'class': 'custom-select form-control'})
        self.fields['extra_skill1'].widget.attrs.update({'class': 'custom-select form-control mb-1'})
        self.fields['extra_skill2'].widget.attrs.update({'class': 'custom-select form-control mb-1'})
        self.fields['extra_skill3'].widget.attrs.update({'class': 'custom-select form-control mb-1'})
