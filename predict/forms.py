from django import forms
from .models import Champion, Position

class DraftForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DraftForm, self).__init__(*args, **kwargs)
        teams = ["blue", "red"]
        NUM_PICKS = 5
        NUM_BANS = 5

        self.POSITION_CHOICES = [(None,""),
                            (1,"ADC"),
                            (2,"MID"),
                            (3,"TOP"),
                            (4,"JNG"),
                            (5,"SUP")]

        CHAMPIONS = Champion.objects.order_by('display_name')
        CHAMPION_CHOICES = []
        for champion in CHAMPIONS:
            CHAMPION_CHOICES.append((champion.id, champion.display_name))

        PICK_CHOICES = [("","")]+CHAMPION_CHOICES
        NO_BAN = -1
        BAN_CHOICES = [("",""),(NO_BAN,"No Ban")]+CHAMPION_CHOICES

        blue_style_class = "blue"
        red_style_class = "red"
        styles = {"blue":blue_style_class, "red":red_style_class}

        for team in teams:
            widget_attrs = {"class": styles[team]}
            for ban_count in range(NUM_BANS):
                name = "{}_{}_{}".format(team, "ban", ban_count)
                self.fields[name] = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Ban {}".format(ban_count), initial="", choices=BAN_CHOICES, required=False)

            for pick_count in range(NUM_PICKS):
                name = "{}_{}_{}".format(team, "pick", pick_count)
                self.fields[name] = forms.ChoiceField(widget=forms.Select(attrs=widget_attrs), label="Pick {}".format(pick_count), initial="", choices=PICK_CHOICES, required=False)

                name = "{}_{}_{}".format(team, "pos", pick_count)
                self.fields[name] = forms.TypedChoiceField(coerce=int, empty_value=None, widget=forms.Select(attrs=widget_attrs), label="Pos", choices=self.POSITION_CHOICES, required=False)
