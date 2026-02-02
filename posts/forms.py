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
            }
        ),
        label='',
        max_length=1000,
    )

    attachments = forms.FileField(
        required=False,
        widget=MultipleFileInput(
            attrs={
                'class': 'form-control feed-attachments-input',
                'accept': 'image/*,text/plain,.txt,.md,.json,.log,.pdf,.doc,.docx',
            }
        ),
        label='Добавить вложения',
    )

    class Meta:
        model = Post
        fields = ['content']


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Оставьте комментарий...',
            }
        ),
        label='',
        max_length=500,
    )

    class Meta:
        model = Comment
        fields = ['content']