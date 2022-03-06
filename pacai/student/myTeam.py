from pacai.util import reflection

import random
import time
import logging
from pacai.util.probability import flipCoin
from pacai.agents.capture.capture import CaptureAgent
from pacai.core.distanceCalculator import Distancer
from pacai.agents.capture.reflex import ReflexCaptureAgent
from pacai.core.directions import Directions

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

class Defense(ReflexCaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """
    # modeled off of reflex agent
    # strategy: patrol near middle?
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)

    def getFeatures(self, gameState, action):
        features = {}

        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if (myState.isPacman()):
            features['onDefense'] = 0

        # Computes distance to invaders we can see.
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)

        if (len(invaders) > 0):
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        if (action == Directions.STOP):
            features['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        if (action == rev):
            features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -1000,
            'onDefense': 100,
            'invaderDistance': -10,
            'stop': -100,
            'reverse': -2
        }

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest return from `ReflexCaptureAgent.evaluate`.
        """
        myState = gameState.getAgentState(self.index)
        # if no agents are on our sidee return on patrol
        # if len(getInvaders(gameState)) == 0:
        #     return self.onPatrol(gameState)
        if myState.isScaredGhost():
            return self.scaredActions(gameState)

        return self.onDefense(gameState)

    def getInvaderDistAndPos(self, gameState, action):
        # returns the closest invader with the closest distance to that invader
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        minDist = float('inf')
        minPos = None
        for i in invaders:
            if minDist > self.getMazeDistance(myPos, i.getPosition()):
                minDist = self.getMazeDistance(myPos, i.getPosition())
                minPos = i.getPosition()
        return minDist, minPos, myPos

    def scaredActions(self, gameState):
        """
        provides best actions if we are a scared ghost
        """
        # if you are in danger of being eaten, retreat
        # instead of finding best path, find furthest path
        # make sure that going to the invader is not one of the legal actions
        actions = gameState.getLegalActions(self.index)
        maxDist = -float('inf')
        bestAction = None
        for a in actions:
            if self.getInvaderDistAndPos(gameState, a)[0] < 3:
                # i think this does the opposite of what it should
                invaderDist = self.getInvaderDistAndPos(gameState, a)[0]
                invaderPos = self.getInvaderDistAndPos(gameState, a)[1]
                myPos = self.getInvaderDistAndPos(gameState, a)[2]
                # tempDist = self.getMazeDistance((myPos), (invaderPos))
                if invaderDist > maxDist:
                    maxDist = invaderDist
                    bestAction = a
        if bestAction is not None:
            return bestAction
        else:
            return random.choice(gameState.getLegalActions(self.index))
        # else:
            # onDefense finds the best path to agent
            # should be fine because it isnt closer than 3
        self.onDefense(gameState)

    # def onPatrol(self, gameState):
    #     """
    #     provides best actions if we are on patrol
    #     should patrol near middle or near the entrances to our side
    #     """
    def onDefense(self, gameState):
        actions = gameState.getLegalActions(self.index)

        start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        logging.debug('evaluate() time for agent %d: %.4f' % (self.index, time.time() - start))

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """

        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)

        return stateEval

