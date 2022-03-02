from pacai.util import reflection

import random
from pacai.util.probability import flipCoin
from pacai.agents.capture.capture import CaptureAgent
from pacai.core.distanceCalculator import Distancer
from pacai.agents.capture.reflex import ReflexCaptureAgent


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


class Offense(ReflexCaptureAgent):
    """
    A reflex agent that seeks food.
    This agent will give you an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)

        # Compute distance to the nearest food.
        foodList = self.getFood(successor).asList()
        # capsuleList = self.getCapsules(self, gameState).asList()

        # This should always be True, but better safe than sorry.
        if (len(foodList) > 0):
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # if(len(capsuleList) > 0):
          #  myPos = successor.getAgentState(self.index).getPosition()
          #  minDistance = min([self.getMazeDistance(myPos, cap) for cap in capsuleList])
          #  features['distanceToCapsule'] = minDistance


        return features

    def getWeights(self, gameState, action):
        return {
            'successorScore': 100,
            'distanceToFood': -1
        }

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

