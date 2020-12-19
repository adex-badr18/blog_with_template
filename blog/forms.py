from django import forms
from .models import Comment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.layout = Layout(
    #         'query',
    #         Submit('submit', 'Submit Comment')
    #     )


class ContactForm(forms.Form):
    name = forms.CharField(max_length=15)
    email = forms.EmailField()
    comment = forms.CharField(widget=forms.Textarea())

