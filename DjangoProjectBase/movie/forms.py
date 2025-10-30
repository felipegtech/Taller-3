from django import forms

class PromptForm(forms.Form):
    prompt = forms.CharField(label='Describe tu película ideal', max_length=200)

