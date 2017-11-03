from django import forms
from .models import Champion, Position

class DraftForm(forms.Form):
    CHAMPIONS = Champion.objects.order_by('display_name')
    CHAMPION_CHOICES = []
    for champion in CHAMPIONS:
        CHAMPION_CHOICES.append((champion.id, champion.display_name))

    PICK_CHOICES = [("","")]+CHAMPION_CHOICES
    NO_BAN = -1
    BAN_CHOICES = [("",""),(NO_BAN,"No Ban")]+CHAMPION_CHOICES

    #POSITIONS = Position.objects.order_by('id')
    #    for position in POSITIONS:
    #        POSITION_CHOICES.append((position.id, position.display_name))
    POSITION_CHOICES = [(None,""),
                        (1,"ADC"),
                        (2,"MID"),
                        (3,"TOP"),
                        (4,"JNG"),
                        (5,"SUP")]

    blue_style_class = "blue"
    red_style_class = "red"
    # fuck everything below this line
    widget_attrs = {'class':blue_style_class}
    blue_ban_0 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 0", initial="", choices=BAN_CHOICES, required=False)
    blue_ban_1 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 1", initial="", choices=BAN_CHOICES, required=False)
    blue_ban_2 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 2", initial="", choices=BAN_CHOICES, required=False)
    blue_ban_3 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 3", initial="", choices=BAN_CHOICES, required=False)
    blue_ban_4 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 4", initial="", choices=BAN_CHOICES, required=False)

    blue_pick_0 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 0", initial="", choices=PICK_CHOICES, required=False)
    blue_pick_1 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 1", initial="", choices=PICK_CHOICES, required=False)
    blue_pick_2 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 2", initial="", choices=PICK_CHOICES, required=False)
    blue_pick_3 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 3", initial="", choices=PICK_CHOICES, required=False)
    blue_pick_4 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 4", initial="", choices=PICK_CHOICES, required=False)

    blue_pos_0 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    blue_pos_1 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    blue_pos_2 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    blue_pos_3 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    blue_pos_4 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)

    widget_attrs = {'class':red_style_class}
    red_ban_0 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 0", initial="", choices=BAN_CHOICES, required=False)
    red_ban_1 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 1", initial="", choices=BAN_CHOICES, required=False)
    red_ban_2 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 2", initial="", choices=BAN_CHOICES, required=False)
    red_ban_3 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 3", initial="", choices=BAN_CHOICES, required=False)
    red_ban_4 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban 4", initial="", choices=BAN_CHOICES, required=False)

    red_pick_0 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 0", initial="", choices=PICK_CHOICES, required=False)
    red_pick_1 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 1", initial="", choices=PICK_CHOICES, required=False)
    red_pick_2 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 2", initial="", choices=PICK_CHOICES, required=False)
    red_pick_3 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 3", initial="", choices=PICK_CHOICES, required=False)
    red_pick_4 = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick 4", initial="", choices=PICK_CHOICES, required=False)

    red_pos_0 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    red_pos_1 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    red_pos_2 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    red_pos_3 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
    red_pos_4 = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=POSITION_CHOICES, required=False)
