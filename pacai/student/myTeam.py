from pacai.util import reflection

import random
import time
import logging
from pacai.core.distance import maze
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
        capsuleList = self.getCapsules(gameState)
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a.getPosition() for a in enemies]

        # This should always be True, but better safe than sorry.
        if (len(capsuleList) > 0):
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, cap) for cap in capsuleList])
            features['distanceToCapsule'] = minDistance

        elif(len(foodList) > 0):
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        return features

    def getWeights(self, gameState, action):
        return {
            'successorScore': 100,
            'distanceToFood': -1,
            'distanceToCapsule': -1,
            'distanceToGhost': -1
        }

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest return from `ReflexCaptureAgent.evaluate`.
        """

        actions = gameState.getLegalActions(self.index)

        start = time.time()

        # determines if ghost is next to them when an action is taken
        values = []
        op = self.getOpponents(gameState)
        for a in actions:
            # slug trap win condition = no stop?
            if (a != Directions.STOP):
                suc = self.getSuccessor(gameState, a)
                bad_pos = False
                for i in range(len(op)):
                    # put in: ignore if you are immune to ghosts 
                    # small incentive to get rid of ghosts on our side? or just completely ignore them
                    op_state = suc.getAgentState(op[i])
                    self_state = suc.getAgentState(self.index)
                    if (op_state.isScaredGhost() is False or (op_state.isPacman() is True and self_state.isScaredGhost is False)):
                        next_pos = suc.getAgentState(self.index).getPosition()
                        op_pos = gameState.getAgentState(op[i]).getPosition()
                        # difference between pos if action is taken and current pos
                        dist = self.getMazeDistance(next_pos, op_pos)
                        if (dist <= 1):
                            bad_pos = True
                # if action taken doesn't collide with a ghost
                if (bad_pos is False):
                    values.append((a, self.evaluate(gameState, a)))

        bestVal = -999999
        bestAction = None
        for i in range(len(values)):
            if (values[i][1] > bestVal):
                bestVal = values[i][1]
                bestAction = values[i][0]
        if bestAction != None:
            return bestAction
        else:
            return random.choice(actions)

class Defense(ReflexCaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at `pacai.core.baselineTeam` for more details about how to create an agent.
    """

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

