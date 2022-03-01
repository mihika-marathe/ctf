from pacai.util import reflection

import random
from pacai.util.probability import flipCoin
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

    # firstAgent = reflection.qualifiedImport(first)
    # secondAgent = reflection.qualifiedImport(second)

    return [
        eval(first)(firstIndex),
        eval(second)(secondIndex)]


class Offense(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

        self.qvalues = []

        self.foodlist = []
        self.opponents = []
        self.index = index

        self.pos = 0

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """

        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.

        self.opponents = self.getOpponents(gameState)
        self.foodlist = self.getFood(gameState).asList()
        self.pos = gameState.getAgentState(self.index).getPosition() 

    def getQValue(self, state, action):
        """
        Get the Q-Value for a `pacai.core.gamestate.AbstractGameState`
        and `pacai.core.directions.Directions`.
        Should return 0.0 if the (state, action) pair has never been seen.
        """

        if (state, action) in self.qvalues:
            return self.qvalues[(state, action)]
        else:
            return 0

    def getValue(self, state):
        """
        Return the value of the best action in a state.
        """

        value = -999999
        action = None
        actions = gameState.getLegalActions(self.index)
        if (len(actions) == 0):
            return None
        else:
            for a in actions:
                v = self.getQValue(state, a)
                if (v > value):
                    value = v
                    action = a
                # breaks ties between best actions
                elif (v == value):
                    ties = [a, action]
                    action = random.choice(ties)
        return action

    def update(self, state, action, nextState, reward):
        # (1 - a) Q(s, a) + a(sample) formula from ws4
        updated_q = (1 - self.getAlpha()) * self.getQValue(state, action)
        actions = self.getLegalActions(nextState)
        if (len(actions) == 0):
            updated_q += self.getAlpha() * reward
        else:
            value = -999999
            for a in actions:
                next_value = self.getQValue(nextState, a)
                if (next_value > value):
                    value = next_value
            updated_q += self.getAlpha() * (reward + (self.getDiscountRate() * value))
        self.qvalues[(state, action)] = updated_q

    def getPolicy(self, state):
        """
        Return the best action in a state.
        I.E., the action that solves: `max_action Q(state, action)`.
        Where the max is over legal actions.
        Note that if there are no legal actions, which is the case at the terminal state,
        you should return a value of None.

        This method pairs with `QLearningAgent.getValue`,
        which returns the value of the best action.
        Whereas this method returns the best action itself.
        """

        value = -999999
        action = None
        actions = state.getLegalActions(self.index)
        if (len(actions) == 0):
            return None
        else:
            for a in actions:
                v = self.getQValue(state, a)
                if (v > value):
                    value = v
                    action = a
                # breaks ties between best actions
                elif (v == value):
                    ties = [a, action]
                    action = random.choice(ties)
        return action

    def chooseAction(self, gameState):
        """
        Choose best action.
        """

        actions = gameState.getLegalActions(self.index)
        if (len(actions) == 0):
            return None
        else:
            # determines which action is chosen
            if (flipCoin(0.2) is True):
                return random.choice(actions)
            else:
                return self.getPolicy(gameState)

class Defense(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)
        self.food = [] # getFoodYouAreDefending(self).asList()
        self.mostDangerousOp = None

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the agent and populates useful fields,
        such as the team the agent is on and the `pacai.core.distanceCalculator.Distancer`.

        IMPORTANT: If this method runs for more than 15 seconds, your agent will time out.
        """
        super().registerInitialState(gameState)

        # Your initialization code goes here, if you need any.
        # initalizes a list of opponents on our side (aka dangerous opponents)
        self.food = self.getFoodYouAreDefending(gameState).asList()
        dangerousOpponents = ()
        '''
        for op in self.getOpponents(gameState):
            if self.red and gameState.isOnRedSide(op):
                dangerousOpponents.append(op)
            elif self.red is False and gameState.isOnBlueSide(op):
                dangerousOpponents.append(op)
        '''
        # the most dangerous opponent is on our side and closest to our food
        # the most in danger capsule is the capsule closest to the opponent
        for op in dangerousOpponents:
            for foo in self.food:
                if 5 < getDistance(op, foo):
                    self.mostDangerousOp = op
                    # mostDangerous.append(op)  # the most dangerous opponent

    # def foodToParse(self, gameState):

    def chooseAction(self, gameState):
        """
        Randomly pick an action.
        """
        actions = gameState.getLegalActions(self.index)
        # if none on our side, move toward food near middle or patrol around
        if self.mostDangerousOp != None:
            d = float("inf")
            bestAction = None
            # chase closest dangerous opponent
            shortest = min(getDistance(self.index, mostDangerous) for most in mostDangerous)
            for action in actions:
                suc = self.getSuccessor(gameState, action)
                if getDistance(suc, shortest) < d:
                    d = getDistance(suc, shortest)  # go for shortest opponent
                    bestAction = action
            if bestAction is not None:
                return bestAction
            # go to food and parse around the food closest to the middle
        return random.choice(actions)   # need to change this

