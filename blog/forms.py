from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    firstname = forms.CharField(max_length=15)
    lastname = forms.CharField(max_length=15)
    email = forms.EmailField()
    to = forms.EmailField()
    comment = forms.CharField(required=False, widget=forms.Textarea())


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'comment')


class SearchForm(forms.Form):
    query = forms.CharField()


class ContactForm(forms.Form):
    name = forms.CharField(max_length=15)
    email = forms.EmailField()
    comment = forms.CharField(widget=forms.Textarea())

