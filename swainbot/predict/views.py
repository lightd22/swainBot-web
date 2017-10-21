from django.shortcuts import render
from django.core.exceptions import ValidationError

from .models import Champion, Position
from .forms import DraftForm
from . import ann_model
from .draftstate import DraftState, get_active_team
from .championinfo import getChampionIds
# Create your views here.

def validate_draft(form):
    RED = DraftState.RED_TEAM
    BLUE = DraftState.BLUE_TEAM
    # U G L Y  C O D E
    SUBMISSION_ORDER = ["blue_ban_0","red_ban_0","blue_ban_1","red_ban_1","blue_ban_2","red_ban_2",
                        "blue_pick_0","red_pick_0","red_pick_1","blue_pick_1","blue_pick_2","red_pick_2",
                        "red_ban_3","blue_ban_3","red_ban_4","blue_ban_4",
                        "red_pick_3","blue_pick_3","blue_pick_4","red_pick_4"]
    data = form.cleaned_data

    draft = []
    errors = {}
    MISSING_SUBMISSION = False
    missing_field = None
    # Process field into submission order and look for gaps in draft
    for submission in SUBMISSION_ORDER:
        (team,phase,pick_id) = submission.split("_")
        value = data[submission]
        if value:
            if MISSING_SUBMISSION:
                errors[missing_field] = "MISSING_SUBMISSION"
                return {"errors":errors, "states":None, "draft":None}
            if phase == "ban":
                cid = int(value) if int(value) != -1 else None
                pos = -1
            else:
                cid = int(value)
                pos = data["_".join([team,"pos",pick_id])]
            draft.append((team,cid,pos))
        else:
            MISSING_SUBMISSION = True
            missing_field = submission

    # Process draft into states and check them for validity
    states = {"blue":DraftState(BLUE,getChampionIds()), "red":DraftState(RED,getChampionIds())}
    for submission_id in range(len(draft)):
        submission = draft[submission_id]
        active_team = submission[0]
        inactive_team = "blue" if active_team == "red" else "red"

        (cid,pos) = submission[1:]
        inactive_pos = pos if pos==-1 else 0 # Mask inactive positions for non-bans

        states[active_team].updateState(cid,pos)
        states[inactive_team].updateState(cid,inactive_pos)

    for state in states.values():
        if(state.evaluateState() in DraftState.invalid_states):
            errors[SUBMISSION_ORDER[submission_id]] = "INVALID_SUBMISSION"

    return {"errors":errors, "states":states, "draft":draft}

def feed_swainbot(states):
    patch_to_model = os.path.dirname(os.path.abspath(__file__))+"/models/model"
    swain = ann_model.Model(path_to_model)
    predictions = swain.predict(states)
    return predictions

def predict(request):
    default_vals = ['','','','','']
    if(request.method == 'POST'):
        form = DraftForm(request.POST)
        blue_ban_1 = request.POST["blue_ban_1"]
        if(form.is_valid()):
#            print("blue ban 0= {}".format(form.cleaned_data['blue_ban_0']))
#            print(form.cleaned_data.keys())
            result = validate_draft(form)
            errors = result["errors"]
            states = result["states"]
            for key in errors:
                print("{} -> {}".format(key,errors[key]))
            if states:
                states["blue"].displayState()
            print(len(result["draft"]))
            #feed_swainbot(form)
    else:
        form = DraftForm()

    context ={
        "draft_form":form
    }
    return render(request, 'predict/index.html', context)
