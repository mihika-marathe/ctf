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

        self.prev = [] # keeps track of previous moves to see if we're stuck somewhere?
        self.capsules = []
        self.food = []
        self.change = False
        self.immune = False
        self.closestfood = None

    def getFeatures(self, gameState, action):
        features = {}
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)

        # Compute distance to the nearest food.
        foodList = self.getFood(successor).asList()
        self.food = foodList
        capsuleList = self.getCapsules(gameState)
        self.capsules = capsuleList
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a.getPosition() for a in enemies]

        # This should always be True, but better safe than sorry.
        if (len(capsuleList) > 0):
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, cap) for cap in capsuleList])
            features['distanceToCapsule'] = minDistance
            '''
            if self.immune is False:
                features['distanceToCapsule'] = minDistance * 60
            else:
                print("immune")
                features['distanceToCapsule'] = 0.5
            '''

        elif(len(foodList) > 0):
            myPos = successor.getAgentState(self.index).getPosition()
            if self.change is False:
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                self.min_distance = minDistance
                for food in foodList:
                    if (self.getMazeDistance(myPos, food) == minDistance):
                        self.closestfood = food
            else:
                minDistance = max([self.getMazeDistance(myPos, food) for food in foodList])
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

        # legal actions of our offense agent
        actions = gameState.getLegalActions(self.index)

        start = time.time()

        # determines if ghost is next to them when an action is taken
        values = []
        op = self.getOpponents(gameState)
        eat_food = False
        being_followed = False
        bad_action = None
        immunity = False

        # if immune, then no * 50 for capsules
        '''
        for i in op:
            if gameState.getAgentState(i).isScaredGhost():
                immunity = True
        self.immune = immunity
        '''

        for a in actions:
            # slug trap win condition = no stop
            if (a != Directions.STOP):
                suc = self.getSuccessor(gameState, a)
                bad_pos = False
                for i in range(len(op)):
                    # put in: ignore if you are immune to ghosts 
                    # small incentive to get rid of ghosts on our side? or just completely ignore them
                    op_state = suc.getAgentState(op[i])
                    self_state = suc.getAgentState(self.index)
                    # don't avoid ghosts if the enemy ghosts are scared or
                    # the enemy is pacman on our side of the board and we are not scared ghosts
                    if (op_state.isScaredGhost() is True or (op_state.isPacman() is False and self_state.isScaredGhost() is True)):
                        next_pos = self_state.getPosition()
                        op_pos = gameState.getAgentState(op[i]).getPosition()
                        # difference between pos if action is taken and current pos
                        dist = self.getMazeDistance(next_pos, op_pos)
                        '''
                        if self.immune:
                            for i in range(len(self.capsules)):
                                if next_pos == self.capsules[i]:
                                    bad_pos = True
                        '''
                        # print(op[i], dist)
                        # if (dist <= 1):
                            # bad_pos = True
                            # being_followed = True
                            # keeps track of move that runs into the ghost
                            # if it moves us closer towards closest food
                            # print(self.getMazeDistance(next_pos, self.closestfood), self.min_distance)
                            # if (self.getMazeDistance(next_pos, self.closestfood) < self.min_distance):
                                # bad_action = a
                                # print(a)
                                # bad_action_value = self.evaluate(gameState, a)
                # if action taken doesn't collide with a ghost
                if (bad_pos is False):
                    # if the successor state doesn't lead into a dead end 
                    # if (self_state.getLegalActions(self.index) > 2):
                    values.append((a, self.evaluate(gameState, a)))

        bestVal = -999999
        bestAction = None

        '''
        # randomization only if there aren't any moves that will lead to food being eaten
        if (gameState.getAgentState(self.index).isPacman() and eat_food is False):
            if (flipCoin(0.1) and len(values) != 0):
                x = random.choice(values)
                return x[0]
        '''
        '''
        # determines if we're stuck in a tunnel and should die to save time
        # only one action besides stop
        if (len(values) == 1 and being_followed is True and gameState.getAgentState(self.index).isPacman()):
            self.stuck += 1
        else:
            self.stuck = 0
        if (self.stuck > 5):
            return random.choice(actions)
        '''

        # determines best actions from actions that aren't stop or run into the ghost
        for i in range(len(values)):
            if (values[i][1] > bestVal):
                bestVal = values[i][1]
                bestAction = values[i][0]

        # edge case to us being blocked to the closest food by an agent
        # if this happens, change path to furthest food instead
        if bad_action != None:
            self.change = not self.change

        # perform best action, otherwise just perform the bad action
        # because it means our only viable moves are stop and the bad action
        # since we are in a dead end
        if bestAction != None:
            self.prev.append(bestAction)
            return bestAction
        else:
            self.prev.append(bad_action)
            return random.choice(actions)

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
        Picks among the actions with 
        the highest return from 
        `ReflexCaptureAgent.evaluate`.
        """
        myState = gameState.getAgentState(self.index)
        # if no agents are on our sidee return on patrol
        op = self.getOpponents(gameState)
        invaders = 0
        for a in gameState.getLegalActions(self.index):
            for i in range(len(op)):
                suc = self.getSuccessor(gameState, a)
                op_state = suc.getAgentState(op[i])
                if op_state.isPacman():
                    invaders = invaders + 1
        if invaders == 0:
            return self.onPatrol(gameState)
        if myState.isScaredGhost():
            return self.scaredActions(gameState)

        return self.onDefense(gameState)

    def getInvaderDistAndPos(self, gameState, action):
        """
        returns the closest invader's position and distance
        and my position which is used in the scaredActions
        functioni
        """
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
        stays out of danger but in close range so that
        the ghost can eat the pacman once it is not scared
        """
        actions = gameState.getLegalActions(self.index)
        maxDist = -float('inf')
        bestAction = None
        for a in actions:
            # retreat if too close
            if self.getInvaderDistAndPos(gameState, a)[0] < 3:
                invaderDist = self.getInvaderDistAndPos(gameState, a)[0]
                invaderPos = self.getInvaderDistAndPos(gameState, a)[1]
                myPos = self.getInvaderDistAndPos(gameState, a)[2]
                if invaderDist > maxDist:
                    maxDist = invaderDist
                    bestAction = a
        if bestAction is not None:
            return bestAction
        else:
            # onDefense finds the best path to the agent if too far
            return self.onDefense(gameState)

    def closestEnemy(self, gameState, enemies, myPos):
        minDist = float('inf')
        minPos = None
        for e in enemies:
            if minDist > self.getMazeDistance(myPos, e.getPosition()):
                minDist = self.getMazeDistance(myPos, e.getPosition())
                minPos = e.getPosition()
        return minDist, minPos

    def onPatrol(self, gameState):
        """
        provides best actions if we are on patrol
        should patrol near middle or near the entrances to our side
        """
        actions = gameState.getLegalActions(self.index)
        bestAction = None
        minDist = float('inf')
            # if you arent at x axis of midline by 2 spaces, go there
        for a in actions:
            successor = self.getSuccessor(gameState, a)
            myState = successor.getAgentState(self.index)
            myPos = myState.getPosition()
            # isPastMidline = myPos[0] >= int(gameState._layout.width / 2)
            isPastMidline = False
            if(self.red and gameState.isOnBlueSide(myPos) or (self.red is False and gameState.isOnRedSide(myPos))):
                isPastMidline = True
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            enemyPos = self.closestEnemy(gameState, enemies, myPos)[1]
            enemyDist = self.closestEnemy(gameState, enemies, myPos)[0]
            if enemyDist < minDist:
                minDist = enemyDist
                bestAction = a
        # if isPastMidline:
        if isPastMidline is True:
            return Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        return bestAction

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

