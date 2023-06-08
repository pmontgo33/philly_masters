from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Team, Tournament


class TeamForm(forms.ModelForm):
    golfer_1 = forms.ModelChoiceField(queryset=None)
    golfer_2 = forms.ModelChoiceField(queryset=None)
    golfer_3 = forms.ModelChoiceField(queryset=None)
    golfer_4 = forms.ModelChoiceField(queryset=None)
    golfer_5 = forms.ModelChoiceField(queryset=None)

    class Meta:
        model = Team
        fields = ("tournament", "name", "user")

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop("queryset", None)
        super().__init__(*args, **kwargs)

        self.fields["tournament"].disabled = True
        self.fields["name"].label = "Team Name"
        self.fields["golfer_1"].label = "Golfer 1"
        self.fields["golfer_1"].queryset = queryset
        self.fields["golfer_2"].label = "Golfer 2"
        self.fields["golfer_2"].queryset = queryset
        self.fields["golfer_3"].label = "Golfer 3"
        self.fields["golfer_3"].queryset = queryset
        self.fields["golfer_4"].label = "Golfer 4"
        self.fields["golfer_4"].queryset = queryset
        self.fields["golfer_5"].label = "Golfer 5"
        self.fields["golfer_5"].queryset = queryset

        self.helper = FormHelper()
        self.helper.form_id = "id-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        # self.helper.form_action = 'submit_survey'

        self.helper.add_input(Submit("submit", "Submit"))


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ("tournament_id",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tournament_id"].label = "Enter Tournament ID to Import New Tournament"
        self.helper = FormHelper()
        self.helper.form_id = "id-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Submit"))
