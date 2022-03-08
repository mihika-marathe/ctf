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
        immune = False

        for e in enemies:
            if(e.isScaredGhost()):
                immune = True

        # This should always be True, but better safe than sorry.
        if (len(capsuleList) > 0 and not immune):
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

        # legal actions of our offense agent
        actions = gameState.getLegalActions(self.index)

        start = time.time()

        # determines if ghost is next to them when an action is taken
        values = []
        op = self.getOpponents(gameState)
        eat_food = False
        being_followed = False
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
                        if (dist <= 1):
                            bad_pos = True
                            being_followed = True
                        '''
                        # if op ghost is not in the way of the food
                        # determines if next pos will lead to food being eaten
                        else:
                            for i in self.food:
                                if i == next_pos:
                                    eat_food = True
                        '''

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

        # determines if we're stuck in a tunnel and should die to save time
        # only one action besides stop
        if (len(values) == 1 and being_followed is True and gameState.getAgentState(self.index).isPacman()):
            self.stuck += 1
        else:
            self.stuck = 0
        if (self.stuck > 5):
            return random.choice(actions)

        # determines best action otherwise
        for i in range(len(values)):
            if (values[i][1] > bestVal):
                bestVal = values[i][1]
                bestAction = values[i][0]
        if bestAction != None:
            self.prev.append(bestAction)
            return bestAction
        else:
            x = random.choice(actions)
            self.prev.append(x)
            return x

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
        myPosition = None
        enemyPosition = None
        isAtMidline = False
            # if you arent at x axis of midline by 2 spaces, go there
        for a in actions:
            successor = self.getSuccessor(gameState, a)
            myState = successor.getAgentState(self.index)
            myPos = myState.getPosition()
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            enemyPos = self.closestEnemy(gameState, enemies, myPos)[1]
            enemyDist = self.closestEnemy(gameState, enemies, myPos)[0]
            if self.midLineCheck(gameState, a) is True:
                isAtMidline = True
                myPosition = myPos
                enemyPosition = enemyPos
            if enemyDist < minDist:
                minDist = enemyDist
                bestAction = a
        if isAtMidline is True:
        # follow enemy y axis if at midline
            if enemyPosition[1] > myPosition[1]:
                if ("North" in actions):
                    # if self.midLineCheck(gameState, Directions.NORTH) is True:
                        return Directions.NORTH
                else:
                    return self.bestMidlineAction(gameState, actions, enemyPosition)
            elif enemyPosition[1] < myPosition[1]:
                if ("South" in actions):
                    # if self.midLineCheck(gameState, Directions.SOUTH) is True:
                        # return Directions.SOUTH
                        return Directions.SOUTH
                else:
                    return self.bestMidlineAction(gameState, actions, enemyPosition)
                # else:
                #     if self.red:
                #         act = gameState.getLegalActions(self.index)
                #         if ("East" in actions):
                #             act.remove("East")
                #         return random.choice(act)
                #     elif not self.red:
                #         act = gameState.getLegalActions(self.index)
                #         if ("West" in actions):
                #             act.remove("West")
                #         return random.choice(act)
            else:   
                # rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
                # # if self.midLineCheck(gameState, rev) is True:
                # return rev
                # if we are on red side then try to go to more to our side
                return self.bestMidlineAction(gameState, actions, enemyPosition)
        return bestAction
        # if bestAction is None:
        #     # if len(legalActions) > 0:
        #     #     return random.choice(legalActions)
        #     # else:
        #     return Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        # else:
    def bestMidlineAction(self, gameState, actions, enemyPos):
        """
        provides best actions if we are at the midline
        removes actions that would take us to the other side
        """
        minDist = float('inf')
        bestAction = None
        if self.red and ("East" in actions):
            actions.remove("East")
        elif (not self.red) and ("West" in actions):
            actions.remove("West")
        for a in actions:
            successor = self.getSuccessor(gameState, a)
            myState = successor.getAgentState(self.index)
            myPos = myState.getPosition()
            if minDist > self.getMazeDistance(myPos, enemyPos):
                minDist = self.getMazeDistance(myPos, enemyPos)
                bestAction = a
        return bestAction


    def midLineCheck(self, gameState, action):
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        isAtMidline = False
        midLine = int(gameState._layout.width / 2)
        lenToMidRed = midLine - myPos[0]
        lenToMidBlue = myPos[0] - (midLine-1)

        # if the action is not past midline will return true
        if (self.red and (lenToMidRed < 3)) or (not self.red and (lenToMidBlue < 3)):
            isAtMidline = True
        return isAtMidline
      
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

