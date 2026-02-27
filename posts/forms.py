from django import forms
from .models import Post, Comment, Attachment


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control feed-content-input',
                'rows': 4,
                'placeholder': 'Расскажите что-нибудь интересное...',
                'maxlength': '1000',
            }
        ),
        label='',
        max_length=1000,
        required=True,
    )

    class Meta:
        model = Post
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content.strip():
            raise forms.ValidationError("Пост не может быть пустым.")
        return content

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Оставьте комментарий...',
                'maxlength': '500',
            }
        ),
        label='',
        max_length=500,
        required=True,
    )

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content.strip():
            raise forms.ValidationError("Комментарий не может быть пустым.")
        return content