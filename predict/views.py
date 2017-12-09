from django.shortcuts import render
from django.core.exceptions import ValidationError
import os
import numpy as np
import pandas as pd

from .models import Champion, Position
from .forms import DraftForm
from . import ann_model
from .draftstate import DraftState, get_active_team
from .championinfo import getChampionIds, championNameFromId
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
                break
            if phase == "ban":
                cid = int(value) if int(value) != DraftForm.NO_BAN else None
                pos = -1
            else:
                cid = int(value)
                pos = data["_".join([team,"pos",pick_id])]
            draft.append((team,cid,pos))
        else:
            MISSING_SUBMISSION = True
            missing_field = submission

    if(errors):
        return {"errors":errors, "active_state":None, "draft":[]}
    # Process draft into states and check them for validity
    states = {"blue":DraftState(BLUE,getChampionIds()), "red":DraftState(RED,getChampionIds())}

    submission_id = -1
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
                print(state.evaluateState())
                state.displayState()
                errors[SUBMISSION_ORDER[submission_id]] = "INVALID_SUBMISSION"

    if submission_id == (len(SUBMISSION_ORDER)-1):
        # If draft is complete (no picks remaining), set active team to None
        active_team = None
        active_state = None
    else:
        (active_team,_,_) = SUBMISSION_ORDER[submission_id+1].split("_")
        active_state = states[active_team]

    validation = {
        "errors":errors,
        "active_state":active_state,
        "draft":draft,
        "bb1e": "id=error",
        "swain_says": "SWAIN SAYS THE NEXT BEST PICKS FOR {} TEAM ARE...".format(active_team).upper(),
    }

    return validation

def predict(request):
    form = DraftForm(request.GET)
    result = {}
    errors = {}
    pos_labels = {key:value for (key,value) in form.POSITION_CHOICES}
    pos_labels[-1] = "BAN"
    if(form.is_valid()):
        result = validate_draft(form)
        errors = result["errors"]
        active_state = result["active_state"]
        for key in errors:
            print("{} -> {}".format(key,errors[key]))
        if not errors and active_state:
            path_to_model = os.path.dirname(os.path.abspath(__file__))+"/models/model"
            swain = ann_model.Model(path_to_model)
            predictions = swain.predict([active_state])
            predictions = predictions[0,:]
            data = [(a,*active_state.formatAction(a),predictions[a]) for a in range(len(predictions))]
            data = [(championNameFromId(cid),pos_labels[pos],Q) for (a,cid,pos,Q) in data]
            df = pd.DataFrame(data, columns=['cname','pos','Q(s,a)'])
            df.sort_values('Q(s,a)',ascending=False,inplace=True)
            df.reset_index(drop=True,inplace=True)
            df['rank'] = df.index+1

            top_predictions = df[['rank','cname','pos','Q(s,a)']].round({'Q(s,a)':4}).head().values.tolist()
        else:
            top_predictions = []

    context = {
        "draft_form":form,
        "top_pred":top_predictions,
        "errors": errors
    }
    context.update(result)

    return render(request, 'predict/predict.html', context)
