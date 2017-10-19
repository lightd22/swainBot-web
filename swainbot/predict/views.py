from django.shortcuts import render

from .models import Position
# Create your views here.

class Submission():
    pass

def index(request):
    list_of_submissions = []
    positions = Position.objects.order_by('id')
    champs = ["ornn", "lux", "vayne", "ryze", "jarvaniv", "braum", "swain"]
    for pos in positions:
        submission = Submission()
        submission.display_name = champs.pop()
        submission.pos_id = pos.id
        list_of_submissions.append(submission)

    context ={
        "list_of_submissions": list_of_submissions,
    }
    return render(request, 'predict/index.html', context)
