from django import forms
from .models import Textbook, TextbookPhoto, Class, Collection, Library, TextbookRating

class TextbookForm(forms.ModelForm):
    class Meta:
        model = Textbook
        fields = ('associated_class', 'published_date', 'condition', 'title', 'author', 'genre', 'description', 'library')
        widgets = {
            'associated_class': forms.Select(attrs={'class': 'form-control'}),
            'published_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'library': forms.Select(attrs={'class': 'form-control'}),
        }

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ('department', 'number', 'name')
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ('textbooks', 'name', 'private', 'description')
        widgets = {
            'textbooks': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'private': forms.CheckboxInput(attrs={'class': 'form-check-input '}),
        }

class TextbookPhotoForm(forms.ModelForm):
    class Meta:
        model = TextbookPhoto
        fields = ('picture',)
        widgets = {
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class LibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = ['name', 'description', 'collections', 'tags', 'public']
        widgets = {
            'collections': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TextbookRatingForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=TextbookRating.RATING_CHOICES,
        widget=forms.RadioSelect,
        label="Rating",
        required=True,           
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows':4, 'placeholder':'Tell us what you thought…'}),
        label="Comment",
        required=False,
    )

    class Meta:
        model = TextbookRating
        fields = ['rating', 'comment']
        