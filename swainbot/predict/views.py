from django.shortcuts import render

from .models import Champion, Position
from .forms import DraftForm
# Create your views here.


def predict(request):
    default_vals = ['','','','','']
    if(request.method == 'POST'):
        form = DraftForm(request.POST)
        blue_ban_1 = request.POST["blue_ban_1"]
        if(form.is_valid()):
            print(form.cleaned_data['blue_ban_1'])

    else:
        form = DraftForm()

    list_of_submissions = []
    positions = Position.objects.order_by('id')
    champs = Champion.objects.all()
    red_submissions = []

    bans = [form.fields['blue_ban_{}'.format(k)] for k in range(5)]
    context ={
        "list_of_submissions": list_of_submissions,
        "champions": list(champs),
        "draft_form":form
    }
    return render(request, 'predict/index.html', context)
