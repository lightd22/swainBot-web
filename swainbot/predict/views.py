from django.shortcuts import render

from .models import Champion, Position
from .forms import DraftForm
# Create your views here.


def predict(request):
    default_vals = ['','','','','']
    form = DraftForm(request.GET)

    list_of_submissions = []
    positions = Position.objects.order_by('id')
    champs = Champion.objects.all()
    red_submissions = []

    bans = [form.fields['blue_ban_{}'.format(k)] for k in range(5)]
    context = {
        "list_of_submissions": list_of_submissions,
        "champions": list(champs),
        "draft_form":form
    }

    errors = validate_draft(form)
    context.update(errors)
    
    return render(request, 'predict/index.html', context)

def validate_draft(draft):   
    errors = {
       # "critical_error": "BEEP BOOP BAD DRAFT DETECTED",
        "bb1e": "id=error",
        "swain_says": "SWAIN SAYS THE NEXT BEST PICKS ARE...",
        "picks": ["Kalista", "Tristana", "Varus"]
    }

    # check each side for validation errors
    # add errors found into dict

    return errors