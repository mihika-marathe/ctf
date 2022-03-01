from pacai.util import reflection

import random

from pacai.agents.capture.capture import CaptureAgent
from pacai.core.distanceCalculator import Distancer


def createTeam(firstIndex, secondIndex, isRed,
        first = 'Offense',
        second = 'Defense'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    firstAgent = reflection.qualifiedImport(first)
    secondAgent = reflection.qualifiedImport(second)

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]


class Offense(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """

        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.
        

    def chooseAction(self, gameState):
        """
        Randomly pick an action.
        """

        actions = gameState.getLegalActions(self.index)
        return random.choice(actions)

class Defense(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, red, blue, food, index, **kwargs):
        super().__init__(index, **kwargs)
        # checks which team self is on
        if self.isOnRedTeam(index):
            self.red = true
        if self.isOnBlueTeam(index):
            self.blue = true
        self.food = getFoodYouAreDefending(self).asList()

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """
        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.
        # initalizes a list of opponents on our side (aka dangerous opponents)
        dangerousOpponents = ()
        for op in getOpponents(gameState):
            if self.red and isOnRedSide(op):
                dangerousOpponents.append(op)
            elif self.blue and isOnBlueSide(op):
                dangerousOpponents.append(op)
        # the most dangerous opponent is on our side and closest to our food
        # the most in danger capsule is the capsule closest to the opponent
        closestDist = -float("inf")
        mostDangerousOp = None
        for op in dangerousOpponents:
            for foo in self.food:
                if closestDist > getDistance(op, foo):
                    closestDist = getDistance(op, foo)
                    mostDangerous = op  # the most dangerous opponent
    def chooseAction(self, gameState):
        """
        Randomly pick an action.
        """
        actions = gameState.getLegalActions(self.index)
        # if none on our side, move toward food near middle or patrol around
        if len(dangerousOpponents) > 0:
            d = float("inf")
            bestAction = None
            for action in actions:
                suc = self.getSuccessor(gameState, action)
                if getDistance(suc, mostDangerous) < d
                    d = getDistance(suc, mostDangerous)
                    bestAction = action
            if bestAction not None:
                return bestAction
        return random.choice(actions)