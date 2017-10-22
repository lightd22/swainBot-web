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

    validation = {
        "errors":errors, 
        "states":states, 
        "draft":draft,
        "bb1e": "id=error",
    }

    return validation

def predict(request):
    form = DraftForm(request.GET)
    result = {}
    if(form.is_valid()):
        result = validate_draft(form)
        errors = result["errors"]
        states = result["states"]
        for key in errors:
            print("{} -> {}".format(key,errors[key]))
        if states:
            path_to_model = os.path.dirname(os.path.abspath(__file__))+"/models/model"
            swain = ann_model.Model(path_to_model)
            state = states["blue"]
            predictions = swain.predict([state])
            predictions = predictions[0,:]
            data = [(a,*state.formatAction(a),predictions[a]) for a in range(len(predictions))]
            data = [(a,championNameFromId(cid),pos,Q) for (a,cid,pos,Q) in data]
            df = pd.DataFrame(data, columns=['act_id','cname','pos','Q(s,a)'])
            df.sort_values('Q(s,a)',ascending=False,inplace=True)
            df.reset_index(drop=True,inplace=True)
            top_predictions = df.head().values.tolist()

        print(len(result["draft"]))

    print(top_predictions)
    context = {
        "draft_form": form,
        "top_predictions": top_predictions,
        "swain_says": "SWAIN SAYS YOU SHOULD..."
    }
    context.update(result)
    context["predictions"] = format_predictions(top_predictions)
    
    return render(request, 'predict/index.html', context)

def format_predictions(top_predictions):
    formatted_predictions = []
    positions = ["AD Carry", "Mid", "Top", "Jungle", "Support"]

    ban_format = "Ban {}"
    pick_format = "Pick {} as {}"
    for prediction in top_predictions:
        pick = ""
        if prediction[2] == -1:
            pick = ban_format.format(prediction[1])
        else:
            this_position = positions[prediction[2] - 1]
            pick = pick_format.format(prediction[1], this_position)
        formatted_predictions.append(pick)

    return formatted_predictions

    
