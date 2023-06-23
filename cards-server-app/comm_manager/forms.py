from django import forms


class PushMessageForm(forms.Form):
    message_type = forms.ChoiceField(
        widget=forms.RadioSelect, choices=[("text", "text"), ("flex", "flex")]
    )
    contents = forms.CharField(widget=forms.Textarea(attrs={"rows": "5"}))
    alt_text = forms.CharField(max_length=100)
    # Add more fields as needed
