from poker.utils.enums import ActionType

class Action:
    def __init__(self, action_type: ActionType, amount=0):
        self.action_type = action_type
        self.amount = amount