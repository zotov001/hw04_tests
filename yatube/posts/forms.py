from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        help_texts = {'group': 'Выберите группу', 'text': 'Введите ссообщение'}
        fields = ('text', 'group', 'image')
