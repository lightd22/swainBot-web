import numpy as np
from .champion_info import champion_name_from_id, valid_champion_id, get_champion_ids
from .draft import Draft

class InvalidDraftState(Exception):
    pass

class DraftState:
    """
    Args:
        team (int) : indicator for which team we are drafting for (RED_TEAM or BLUE_TEAM)
        champ_ids (list(int)) : list of valid championids which are available for drafting.
        num_positions (int) : number of available positions to draft for. Default is 5 for a standard 5x5 draft.

    DraftState is the class responsible for holding and maintaining the current state of the draft. For a given champion with championid c,
    that champion's state with respect to the draft is at most one of:
        - c is banned from selection.
        - c is selected as part of the opponent's team.
        - c is selected as one of our team's position.

     The state of the draft will be stored as a (numChampions) x (numRoles+2) numPy array. If state(c,k) = 1 then:
        - k = 0 -> champion c is banned from selection.
        - k = 1 -> champion c is selected as part of the enemy team.
        - 2 <= k = num_positions+1 -> champion c is selected as position k-1 in our draft.

    Default draft positions are interpreted as:
        Position 1 -> ADC/Marksman (Primary farm)
        Position 2 -> Middle (Secondary farm)
        Position 3 -> Top (Tertiary farm)
        Position 4 -> Jungle (Farming support)
        Position 5 -> Support (Primary support)
    """
    # State codes
    BAN_AND_SUBMISSION = 101
    DUPLICATE_SUBMISSION = 102
    DUPLICATE_ROLE = 103
    INVALID_SUBMISSION = 104
    TOO_MANY_BANS = 105
    TOO_MANY_PICKS = 106
    invalid_states = [BAN_AND_SUBMISSION, DUPLICATE_ROLE, DUPLICATE_SUBMISSION, INVALID_SUBMISSION,
                      TOO_MANY_BANS, TOO_MANY_PICKS]

    DRAFT_COMPLETE = 1
    BLUE_TEAM = Draft.BLUE_TEAM
    RED_TEAM = Draft.RED_TEAM
    BAN_PHASE = Draft.BAN
    PICK_PHASE = Draft.PICK

    def __init__(self, team, champ_ids = get_champion_ids(), num_positions = 5, draft = Draft('default')):
        #TODO (Devin): This should make sure that numChampions >= num_positions
        self.num_champions = len(champ_ids)
        self.num_positions = num_positions
        self.num_actions = (self.num_positions+1)*self.num_champions
        self.state_index_to_champ_id = {i:k for i,k in zip(range(self.num_champions),champ_ids)}
        self.champ_id_to_state_index = {k:i for i,k in zip(range(self.num_champions),champ_ids)}
        self.state = np.zeros((self.num_champions, self.num_positions+2), dtype=bool)
        self.picks = []
        self.bans = []
        self.selected_pos = []

        self.team = team
        self.draft_structure = draft
        # Get phase information from draft
        self.BAN_PHASE_LENGTHS = self.draft_structure.PHASE_LENGTHS[DraftState.BAN_PHASE]
        self.PICK_PHASE_LENGTHS = self.draft_structure.PHASE_LENGTHS[DraftState.PICK_PHASE]

        # The dicts pos_to_pos_index and pos_index_to_pos contain the mapping
        # from position labels to indices to the state matrix and vice versa.
        self.positions = [i-1 for i in range(num_positions+2)]
        self.pos_indices = [1,0]
        self.pos_indices.extend(range(2,num_positions+2))
        self.pos_to_pos_index = dict(zip(self.positions,self.pos_indices))
        self.pos_index_to_pos = dict(zip(self.pos_indices,self.positions))

    def reset(self):
        """
        Resets draft state back to default values.
        Args:
            None
        Returns:
            None
        """
        self.state[:] = False
        self.picks = []
        self.bans = []
        self.selected_pos = []

    def get_valid_actions(self, form="mask"):
        """
        Returns a valid actions for the current state.
        Input:
            self.state
            form (string): default returns actions as a mask. "list" returns actions as a list of ids
        Returns:
            action_ids (list[bool/int]): valid actions that can be taken from state. If form = "list" ids are returned as a list of action_ids,
                otherwise actions are returned as a boolean mask

        If the draft is complete or in an invalid state, get_valid_actions will return an empty list of actions.
        """
        # Check if draft is complete or invalid
        if(self.evaluate()):
            if(form == "list"):
                return np.array([])
            else:
                return np.zeros_like(self.state[:,1:].reshape(-1))

        sub_count = len(self.bans)+len(self.picks)
        phase = self.draft_structure.get_active_phase(sub_count)
        champ_available = np.logical_not(np.amax(self.state[:,:],axis=1))
        pos_available = [pos for pos in range(1, self.num_positions+1) if pos not in self.selected_pos]
        valid_actions = np.zeros_like(self.state[:,1:])
        if(phase == Draft.BAN):
            # only bans are (potentially) valid during ban phase
            valid_actions[:,0] = champ_available
        else:
            # only picks are (potentially) valid during pick phase
            for pos in pos_available:
                valid_actions[:,pos] = champ_available

        if(form == "list"):
            return np.nonzero(valid_actions.reshape(-1))
        else:
            return valid_actions.reshape(-1)

    def is_submission_legal(self, champion_id, position):
        """
        Checks if submission (champion_id, position) is a valid and legal submission for the current state.
        Returns:
            True if submission is legal, False otherwise.
        """
        if(not self.can_ban(champion_id) or not self.can_pick(champion_id)):
            return False
        sub_count = len(self.bans)+len(self.picks)
        phase = self.draft_structure.get_active_phase(sub_count)
        if phase == DraftState.BAN_PHASE and position != -1:
            return False
        if phase == DraftState.PICK_PHASE:
            pos_index = self.get_position_index(position)
            is_pos_filled = np.amax(self.state[:,pos_index])
            if(is_pos_filled):
                return False
        return True

    def get_champ_id(self,index):
        """
        get_champ_id returns the valid champion ID corresponding to the given state index. Since champion IDs are not contiguously defined or even necessarily ordered,
        this mapping will not be trivial. If index is invalid, returns -1.
        Args:
            index (int): location index in the state array of the desired champion.
        Returns:
            champ_id (int): champion ID corresponding to index (as defined by champ_ids)
        """
        if index not in self.state_index_to_champ_id.keys():
            return -1
        return self.state_index_to_champ_id[index]

    def get_state_index(self,champ_id):
        """
        get_state_index returns the state index corresponding to the given champion ID. Since champion IDs are not contiguously defined or even necessarily ordered,
        this mapping is non-trivial. If champ_id is invalid, returns -1.
        Args:
            champ_id (int): id of champion to look up
        Returns
            index (int): state index of corresponding champion id
        """
        if champ_id not in self.champ_id_to_state_index.keys():
            return -1
        return self.champ_id_to_state_index[champ_id]

    def get_position_index(self,position):
        """
        get_position_index returns the index of the state matrix corresponding to the given position label.
        If the position is invalid, returns False.
        Args:
            position (int): position label to look up
        Returns:
            index (int): index into the state matrix corresponding to this position
        """
        if position not in self.positions:
            return False
        return self.pos_to_pos_index[position]

    def get_position(self, pos_index):
        """
        get_position returns the position label corresponding to the given position index into the state matrix.
        If the position index is invalid, returns False.
        Args:
            pos_index (int): position index to look up
        Returns:
            position (int): position label corresponding to this position index
        """
        if pos_index not in self.pos_indices:
            return False
        return self.pos_index_to_pos[pos_index]

    def format_state(self):
        """
        Format the state so the Q-network can process it.
        Args:
            None
        Returns:
            A copy of self.state
        """
        if(self.evaluate() in DraftState.invalid_states):
            raise InvalidDraftState("Attempting to format an invalid draft state for network input with code {}".format(self.evaluate()))

        return self.state.reshape(-1)

    def format_secondary_inputs(self):
        """
        Produces secondary input information (information about filled positions and draft phase)
        to send to Q-network.
        Args:
            None
        Returns:
            Numpy vector of secondary network inputs
        """
        if(self.evaluate() in DraftState.invalid_states):
            raise InvalidDraftState("Attempting to format an invalid draft state for network input with code {}".format(self.evaluate()))

        # First segment of information checks whether each position has been or not filled in the state
        # This is done by looking at columns in the subarray corresponding to positions 1 thru 5
        start = self.get_position_index(1)
        end = self.get_position_index(5)
        secondary_inputs = np.amax(self.state[:,start:end+1],axis=0)

        # Second segment checks if the phase corresponding to this state is a pick phase
        # This is done by counting the number of bans currently submitted. Note that this assumes
        # that state is currently a valid state. If this is not necessarily the case a check can be made using
        # evaluate().
        submission_count = len(self.bans)+len(self.picks)
        phase = self.draft_structure.get_active_phase(submission_count)
        is_pick_phase = phase == DraftState.PICK_PHASE
        secondary_inputs = np.append(secondary_inputs, is_pick_phase)
        return secondary_inputs

    def format_action(self,action):
        """
        Format input action into the corresponding tuple (champ_id, position) which describes the input action.
        Args:
            action (int): Action to be interpreted. Assumed to be generated as output of ANN. action is the index
                          of the flattened 'actionable state' matrix
        Returns:
            (championId, position) (tuple of ints): Tuple of integer values which may be passed as arguments to either
            self.add_pick() or self.add_ban() depending on the value of position. If position = -1 -> action is a ban otherwise action
            is a pick.

        Note: format_action() explicitly indexes into 'actionable state' matrix which excludes the portion of the state
        matrix corresponding to opponent team submission. In practice this means that (cid, pos) = format_action(a) will
        never output pos = 0.
        """
        # 'actionable state' is the sub-state of the state matrix with 'enemy picks' column removed.
        actionable_state = self.state[:,1:]
        if(action not in range(actionable_state.size)):
            raise "Invalid action to format_action()!"
        (state_index, position_index) = np.unravel_index(action,actionable_state.shape)
        # Action corresponds to a submission that we are allowed to make, ie. a pick or a ban.
        # We can't make submissions to the enemy team, so the indicies corresponding to these actions are removed.
        # position_index needs to be shifted by 1 in order to correctly index into full state array
        position_index += 1
        position = self.get_position(position_index)
        champ_id = self.get_champ_id(state_index)
        return (champ_id,position)

    def get_action(self, champion_id, position):
        """
        Given a (champion_id, position) submission pair. Return the corresponding action index in the flattened actionable state array.
        Args:
            champion_id (int): id of a champion to be picked/banned.
            position (int): Position of champion to be selected. The value of position determines if championId is interpreted as a pick or ban:
                position = -1 -> champion ban submitted.
                0 < position <= num_positions -> champion selection submitted by our team for pos = position
        Returns:
            action (int): Action to be interpreted as index into the flattened actionable state vector. If no such action can be found, returns -1

        Note: get_action() explicitly indexes into 'actionable state' matrix which excludes the portion of the state
        matrix corresponding to opponent team submission. In practice this means that a = format_action(cid,pos) will
        produce an invalid action for pos = 0.
        """
        state_index = self.get_state_index(champion_id)
        pos_index = self.get_position_index(position)
        if ((state_index==-1) or (pos_index not in range(1,self.state.shape[1]))):
            print("Invalid state index or position out of range!")
            print("cid = {}".format(champion_id))
            print("pos = {}".format(position))
            return -1
        # Convert position index for full state matrix into index for actionable state
        pos_index -= 1
        action = np.ravel_multi_index((state_index,pos_index),self.state[:,1:].shape)
        return action

    def update(self, champion_id, position):
        """
        Attempt to update the current state of the draft and pick/ban lists with a given championId.
        Returns: True is selection was successful, False otherwise
        Args:
            champion_id (int): Id of champion to add to pick list.
            position (int): Position of champion to be selected. The value of position determines if championId is interpreted as a pick or ban:
                position = -1 -> champion ban submitted.
                position = 0 -> champion selection submitted by the opposing team.
                0 < position <= num_positions -> champion selection submitted by our team for pos = position
        """
        # Special case for NULL ban submitted.
        if (champion_id is None and position == -1):
            # Only append NULL bans to ban list (nothing done to state matrix)
            self.bans.append(champion_id)
            return True

        # Submitted picks of the form (champ_id, pos) correspond with the selection champion = champion_id in position = pos.
        # Bans are given pos = -1 and enemy picks pos = 0. However, this is not how they are stored in the state array.
        # Finally this doesn't match indexing used for state array and action vector indexing (which follow state indexing).
        if((position is None) or (position < -1) or (position > self.num_positions) or (not valid_champion_id(champion_id))):
            return False

        index = self.champ_id_to_state_index[champion_id]
        pos_index = self.get_position_index(position)
        if(position == -1):
            self.bans.append(champion_id)
        else:
            self.picks.append(champion_id)
            self.selected_pos.append(position)

        self.state[index,pos_index] = True
        return True

    def display(self):
        #TODO (Devin): Clean up display to make it prettier.
        print("=== Begin Draft State ===")
        print("There are {num_picks} picks and {num_bans} bans completed in this draft. \n".format(num_picks=len(self.picks),num_bans=len(self.bans)))

        print("Banned Champions: {0}".format(list(map(champion_name_from_id, self.bans))))
        print("Picked Champions: {0}".format(list(map(champion_name_from_id, self.picks))))
        pos_index = self.get_position_index(0)
        enemy_draft_ids = list(map(self.get_champ_id, list(np.where(self.state[:,pos_index])[0])))
        print("Enemy Draft: {0}".format(list(map(champion_name_from_id,enemy_draft_ids))))

        print("Ally Draft:")
        for pos_index in range(2,len(self.state[0,:])): # Iterate through each position columns in state
            champ_index = np.where(self.state[:,pos_index])[0] # Find non-zero index
            if not champ_index.size: # No pick is found for this position, create a filler string
                draft_name = "--"
            else:
                draft_name = champion_name_from_id(self.get_champ_id(champ_index[0]))
            print("Position {p}: {c}".format(p=pos_index-1,c=draft_name))
        print("=== End Draft State ===")

    def can_pick(self, champion_id):
        """
        Check to see if a champion is available to be selected.
        Returns: True if champion is a valid selection, False otherwise.
        Args:
            champion_id (int): Id of champion to check for valid selection.
        """
        return ((champion_id not in self.picks) and valid_champion_id(champion_id))

    def can_ban(self, champion_id):
        """
        Check to see if a champion is available to be banned.
        Returns: True if champion is a valid ban, False otherwise.
        Args:
            champion_id (int): Id of champion to check for valid ban.
        """
        return ((champion_id not in self.bans) and valid_champion_id(champion_id))

    def add_pick(self, champion_id, position):
        """
        Attempt to add a champion to the selected champion list and update the state.
        Returns: True is selection was successful, False otherwise
        Args:
            champion_id (int): Id of champion to add to pick list.
            position (int): Position of champion to be selected. If position = 0 this is interpreted as a selection submitted by the opposing team.
        """
        if((position < 0) or (position > self.num_positions) or (not valid_champion_id(champion_id))):
            return False
        self.picks.append(champion_id)
        self.selected_pos.append(position)
        index = self.get_state_index(champion_id)
        pos_index = self.get_position_index(position)
        self.state[index,pos_index] = True
        return True

    def add_ban(self, champion_id):
        """
        Attempt to add a champion to the banned champion list and update the state.
        Returns: True is ban was successful, False otherwise
        Args:
            champion_id (int): Id of champion to add to bans.
        """
        if(not valid_champion_id(champion_id)):
            return False
        self.bans.append(champion_id)
        index = self.get_state_index(champion_id)
        self.state[index,self.get_position_index(-1)] = True
        return True

    def evaluate(self):
        """
        evaluate checks the current state and determines if the draft as it is currently recorded is valid.
        Returns: value (int) - code indicating validitiy of state
            Valid codes:
                value = 0 -> state is valid but incomplete.
                value = DRAFT_COMPLETE -> state is valid and complete.
            Invalid codes:
                value = BAN_AND_SUBMISSION -> state has a banned champion selected for draft. This will also appear if a ban is submitted which matches an previously submitted champion.
                value = DUPLICATE_SUBMISSION -> state has a champion drafted which is already part of the opposing team or has already been selected by our team.
                value = DUPLICATE_ROLE -> state has multiple champions selected for a single role
                value = INVALID_SUBMISSION -> state has a submission that was included out of the draft phase order (ex pick during ban phase / ban during pick phase)
        """
        # Check for duplicate submissions appearing in picks or bans
        duplicate_picks = set([cid for cid in self.picks if self.picks.count(cid)>1])
        # Need to remove possible NULL bans as duplicates (since these may be legitimate)
        duplicate_bans = set([cid for cid in self.bans if self.bans.count(cid)>1]).difference(set([None]))
        if(len(duplicate_picks)>0 or len(duplicate_bans)>0):
            return DraftState.DUPLICATE_SUBMISSION

        # Check for submissions appearing in both picks and bans
        if(len(set(self.picks).intersection(set(self.bans)))>0):
            # Invalid state includes an already banned champion
            return DraftState.BAN_AND_SUBMISSION

        # Check for different champions that have been submitted for the same role
        for pos in range(2,self.num_positions+2):
            loc = np.argwhere(self.state[:,pos])
            if(len(loc)>1):
                # Invalid state includes multiple champions intended for the same role.
                return DraftState.DUPLICATE_ROLE

        # Check for out of phase submissions
        num_bans = len(self.bans)
        num_picks = len(self.picks)
        sub_count = num_bans+num_picks

        if(num_bans > self.draft_structure.NUM_BANS):
            return DraftState.TOO_MANY_BANS
        if(num_picks > self.draft_structure.NUM_PICKS):
            return DraftState.TOO_MANY_PICKS

        # validation is tuple of form (target_ban_count, target_blue_pick_count, target_red_pick_count)
        validation = self.draft_structure.submission_dist[sub_count]
        num_opponent_sub = np.count_nonzero(self.state[:,self.get_position_index(0)])
        num_ally_sub = num_picks - num_opponent_sub
        if self.team == DraftState.BLUE_TEAM:
            dist = (num_bans, num_ally_sub, num_opponent_sub)
        else:
            dist = (num_bans, num_opponent_sub, num_ally_sub)
        if(dist != validation):
            return DraftState.INVALID_SUBMISSION

        # State is valid, check if draft is complete
        if(num_ally_sub == self.num_positions and num_opponent_sub == self.num_positions):
            # Draft is valid and complete. Note that it isn't necessary
            # to have the full number of valid bans to register a complete draft. This is
            # because teams can be forced to forefit bans due to disciplinary factor (rare)
            # or they can elect to not submit a ban (very rare).
            return DraftState.DRAFT_COMPLETE

        # Draft is valid, but not complete
        return 0

if __name__=="__main__":
    state = DraftState(DraftState.BLUE_TEAM)
    print(state.evaluate())
    print(state.num_actions)
    state.display()
    actions = state.get_valid_actions()
    print(actions)

    state.update(1,-1)
    state.update(2,-1)
    state.update(3,-1)
    state.update(4,-1)
    state.update(5,-1)
    state.update(6,-1)

    state.update(7,1)
    state.update(8,0)
    state.update(9,0)

    new_actions = state.get_valid_actions()
    print(new_actions)
    print("")
    for aid in range(len(new_actions)):
        if(new_actions[aid]):
            print(state.format_action(aid))

    state.update(10,2)
    state.update(11,3)
    state.update(12,0)

    state.update(13,-1)
    state.update(14,-1)
    state.update(15,-1)
    state.update(16,-1)

    state.update(17,0)
    state.update(18,5)
    state.update(19,4)

    state.display()
    print(state.evaluate())
