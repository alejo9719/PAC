import sys
import numpy as np
from enum import Enum
import pygame
from pygame.locals import * #Difference between "import module" and "from module import": With the second you have to specify which functions to import (if you use *, you import everything),
#but you can use as "function" instead of "module.function".
from levels import *
from behaviourTrees import *
import heapq
import random

#THIS LEVEL IS A "CONTINUOUS" ONE. IT MEANS THAT THE CHARACTERS ARE ABLE TO MOVE IN ANY DIRECTION. TO ACHIEVE THIS, VECTORS ARE USED AND APPROXIMATED TO THE LEVEL'S GRID

class tileClass: #Class to represent a tile (node) in the A* algorithm
    parent=None #Parent corner in the path
    x=0 #Tile's x position
    y=0 #Tile's y position
    f=0 #Tile (node) cost evaluation function value
    g=0 #Traveled distance cost
    h=0 #Calculated heuristic value
    index=-1 #Tile's index


    def __init__(self, tileX, tileY, _index):
        self.x=tileX
        self.y=tileY
        self.index=_index
        
        
    def __lt__(self, other): #Less than function, used to compare elements inside structures like a priority queue when the chosen attribut comparison is not definitive.
        return self.f < other.f #Compares this tile's evaluation function with other corner's


    def updateTile(self, newParent, newG, newH): #Updates a the tile's parameters
        self.g=newG
        self.h=newH
        self.parent=newParent
        self.f=self.h+self.g
    
    
    
class AStar: #Class to calculate the shortest path between corners using A*. Based on http://www.laurentluce.com/posts/solving-mazes-using-python-simple-recursivity-and-a-search/
    
    def __init__(self):
        self.openList=[] #Create the open list
        heapq.heapify(self.openList) #Makes the open list a heap (priority queue, the smallest item in the first position)
        self.closedList=set() #The closed list is a set as the order doesn't matters and a set is faster than a list
        self.tileClasses=[] #List of tile classes
        

    def createTiles(self): #Fill the tile classes list
        for i in range(0, 200):
            for j in range(0, 140):
                self.tileClasses.append(tileClass(i, j, ((i*140)+j))) #Create a class for each tile and add it to the list in tile index order. Index is calculated based on the tile position.
            
            
    def getAdjTiles(self, tileIndex):
        tile=self.tileClasses[tileIndex]
        adjTiles=[]
        for i in range(tile.x-1, tile.x+1):
            for j in range(tile.y-1, tile.y+1):
                if(i>=0 and i<200 and j>=0 and j<140): #FALTA AGREGAR VERIFICACION DE MUROS
                    adjTiles.append(self.tileClasses[(i*140)+j]) #Add tile instance to the adjacent tiles list. Extracts the tile index using the level dimensions to calculate it
        return adjTiles #Return adjacent corners list
    
    
    def calculatePath(self, tileIndex):
        path=[] #List to save the path positions
        actualTile=self.tileClasses[tileIndex] #Variable to save the actual analyzed tile
        path.insert(0, [actualTile.x, actualTile.y]) #Adds the position of the ending tile to the path
        while(actualTile.parent!=None): #Follows the parent tree until it reaches the root
            actualTile=actualTile.parent #The tile to add is the parent of the current one
            path.insert(0, [actualTile.x, actualTile.y]) #Extracts the tile position adds it to the beginning of the path
        return path #Return the path list

    
    def algorithm(self, startPos, endPos):
        startIndex=startPos[0]*140+startPos[1]
        endIndex=endPos[0]*140+endPos[1]
        self.createTiles() #Create the array of classes corresponding to each tile
        start=self.tileClasses[startIndex] #Extracts the class corresponding to the starting tile
        end=self.tileClasses[endIndex] #Extracts the class corresponding to the ending tile
        heapq.heappush(self.openList, [start.f, start]) #Initialize the open list with the start tile
        while len(self.openList): #There are corners left in the open list
            f, tile=heapq.heappop(self.openList) #Get the tile with the lowest F from the open list
            self.closedList.add(tile.index) #Add tile to the closed list as it's being visited
            if tile.index==endIndex: #The destination has been reached
                return self.calculatePath(tile.index) #Returns the path of positions from the start tile to the end tile
            
            adjTiles=self.getAdjTiles(tile.index) #Gets the list of tiles adjacent to the current one
            for adjTile in adjTiles: #Checks each tile adjacent to the current one
                if adjTile.index not in self.closedList: #Adjacent tile hasn't been visited
                    adjG=tile.g+calculateContinuousDistance([tile.x,tile.y], [adjTile.x,adjTile.y]) #G value of the adjacent tile on the current path
                    #print("Adjacent G: ", adjG)
                    if(adjTile.f, adjTile) in self.openList: #The adjacent tile is already in the open list
                        if adjTile.g>adjG: #Adjacent tile previous G value is greater than the one it has on the current path
                            adjTile.updateTile(tile, adjG, calculateContinuousDistance([adjTile.x,adjTile.y], [end.x, end.y])) #Updates the tile parameters (parent, G and H)
                    else: #The adjacent tile is not in the open list
                        adjTile.updateTile(tile, adjG, calculateContinuousDistance([adjTile.x,adjTile.y], [end.x, end.y])) #Update the adjacent tile parameters
                        heapq.heappush(self.openList, [adjTile.f, adjTile]) #Add the adjacent tile to the open list

                        

class powerUP(pygame.sprite.Sprite):
    
    def __init__(self, initialPos): #Initialization fucntion which takes the initial position of the power up object
        pygame.sprite.Sprite.__init__(self)
        self.currentPos=[0,0]
        self.image = loadImage("imagenes/star.png", True) #Load the sprite image
        self.rect = self.image.get_rect() #Create the sprite collision rectangle using the loaded image dimensions
        self.currentPos[0]=initialPos[0]
        self.currentPos[1]=initialPos[1]
        self.rect.centerx = ((self.currentPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centery = ((self.currentPos[1]+1) * 5)
        
    def checkCollision(self, mainChar, mainEnemy): #Checks collision with the main character
        if(pygame.sprite.collide_rect(self, mainChar)):
            mainEnemy.killMinion()
            return True
        if(pygame.sprite.collide_rect(self, mainEnemy)):
            mainEnemy.respawnMinion()
            return True
        for minion in mainEnemy.minions:
            if(pygame.sprite.collide_rect(self, minion)):
                mainEnemy.respawnMinion()
                return True
        return False



class obstacle(pygame.sprite.Sprite):
    
    def __init__(self, initialPos):
        pygame.sprite.Sprite.__init__(self)
        self.image = loadImage("imagenes/obstacle.png", True) #Load the sprite image
        self.rect = self.image.get_rect() #Create the sprite collision rectangle using the loaded image dimensions
        self.rect.centerx = ((initialPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centery = ((initialPos[1]+1) * 5)
        self.currentPos=[0,0]
        self.currentPos[0]=initialPos[0]
        self.currentPos[1]=initialPos[1]
        repellingForce=10



class characterClass(pygame.sprite.Sprite):
    currentPos=[4,1] #Current position in the level grid
    destPos=[4,1] #Destination corner position
    
    
    def __init__(self, spritePath):
        pygame.sprite.Sprite.__init__(self) #Call the parent class initializer
        self.image = loadImage(spritePath, True) #Load the sprite image
        self.rect = self.image.get_rect() #Create the sprite collision rectangle using the loaded image dimensions
        self.rect.centerx = ((self.currentPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centery = ((self.currentPos[1]+1) * 5)   
    
    
    def move(self):
        return
    
    
    def draw(self): #Draws the character on the current position, looking to the current direction
        self.rect.centerx = ((self.currentPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centery = ((self.currentPos[1]+1) * 5)
        
        
        
class enemy(characterClass):
    states=Enum('states', 'Start Pathfinding Pathfollowing Escape') #Enumeration of the states of the FSM
    currentState=states.Start #Initial state of the enemy
    findClosestCorner=True #Flag to indicate that the corner closest to the main character must be calculated
    destinationTile=0
    FSMfunc=['waitForSpawn', #Functions to be executed for each state of the FSM
             'findPath',
             'move',
             'run'
             ]
    path=[] #Path to be followed by this enemy
    
    def __init__(self, spritePath):
        self.sprite=spritePath #Save original sprite path to use it when going out of vulnerable state
        characterClass.__init__(self, spritePath) #Initialize the character
        self.currentPos=[90,90] #Initial character position
        self.objectivePos=[0,0]
        self.destPos=[0,0]
        self.directionVector=[0,0]
        self.speed=3.9
        
        
    def moveTo(self): #Function to get the next position and its direction respect to the current one
        return
        
                
                
    def calculateClosestCorner(self, originCorner, pathFinder): #Calculates the closest exterior corner to a grid position
        mapCorners=[1, 6, 61, 64] #Exterior map corners
        distMin=200 #Initialize the minimum distance to a value greater to any distance value
        closestCorner=0 #Initialize the closest corner to a value that is not the index of any corner
        for corner in mapCorners: #Get each exterior corner
            distance=calculateDistance(originCorner, corner)
            if(distance<distMin): #Calculate the distance to each exterior corner and compare to the minimum distance found
                closestCorner=corner #Update the closest corner if the distance to the analyzed corner is shorter than the minimum distance previously found
                distMin=distance
        
        return closestCorner #Returns the closest corner found
                
                
    def executeState(self): #Executes the function corresponding to the current state
        eval('self.'+self.FSMfunc[self.currentState.value-1]+'()') #Evalues the expression func() using the following format: #eval('self'+'funcname'+'('+par+')')
        
        
    def waitForSpawn(self):
        return
        
        
    def findPath(self):
        self.moveTo()
        return
        
        
    def move(self): #Function for the "Pathfollowing" state
        #print('Im following the pizza')
        
        """if(self.currentPos==self.destPos): #The character needs to find a corner to move to (destination corner reached)
            self.moveTo() #Finds the next corner to move to.
            #print("moveToExec")"""
        
        centerX=self.currentPos[0]+0.5 #Calculate the center of the current tile
        centerY=self.currentPos[1]+0.5 #Calculate the center of the current tile
        #nextX=int(centerX+3*(math.cos(self.directionAngle))) #Calculate next X position
        #nextY=int(centerY+3*(math.sin(self.directionAngle))) #Calculate next Y position
        nextX=int(centerX+self.speed*self.directionVector[0]) #Calculate next X position
        nextY=int(centerY+self.speed*self.directionVector[1]) #Calculate next Y position
        
        if(nextX<WIDTH2/5 and nextY<HEIGHT2/5 and nextX>0 and nextY>0): #The character is inside the limits and is not colliding with any obstacle
            self.currentPos[0]=nextX #Update X pos
            self.currentPos[1]=nextY #Update Y pos
        else:
            self.directionVector=[0,0] #No force is applied
    
        #print(self.currentPos)
                                                      
                                                      
    def run(self): #Function for the "Escape" state
        #print('RUN!')
        pathFinder=AStar() #Creates instance of the A* path finder class
        closestObjCorner=self.calculateClosestCorner(self.objectiveIndex, pathFinder) #Calculate the external corner closest to the objective
        
        #If the next corner to be reached by the objective changes, recalculate the path to the closest
        #escaping corner. The first time after changing to this state, it must always be executed.
        if(self.objectiveIndex!=self.objective.nextCorner or self.destinationCorner==closestObjCorner or self.findClosestCorner):
            myCorner=cornerMatrix[self.destPos[0], self.destPos[1]] #Extracts the index of the next corner to be reached by self
            
            self.objectiveIndex=self.objective.nextCorner #Objective's destination corner update
            #self.destinationCorner=self.calculateClosestCorner(myCorner, pathFinder) #Initialize the destination corner as the closest one
            self.destinationCorner=0 #Initialize the destination corner
        
            #if(self.destinationCorner==closestObjCorner): #The closest corner is also the one closer to the objective
            exteriorCorners=[1, 6, 61, 64] #Define exterior corners
            exteriorCorners.remove(closestObjCorner) #Remove the corner closest to the main character from the possible choices
            self.destinationCorner=random.choice(exteriorCorners) #Pick a random corner between the possible choices
            
            self.path=pathFinder.algorithm(myCorner, self.destinationCorner) #Finds the shortest path to the closest corner (that is not the closest to the main character)
            self.path.pop(0) #As the first corner in the path is the current destination, pop it from the path to not try to reach it while being there                        
            
            del pathFinder #Free up the pathFinder instance memory
            self.findClosestCorner=False #The closest escaping corner and the path to it has been foud
        
        self.move() #Move following the calculated path
        
        if(self.objective.powerUPflag==False):
            findClosestCorner=True #Sets the find closest corner flag for the next time this state is executed
            self.image=loadImage(self.sprite, True) #Revert sprite image to the original one
            self.currentState=self.states.Pathfinding #Change to path finding state



class RedGhost(enemy): #Red (leader) enemy class
    
    def __init__(self, objectiveChar):
        enemy.__init__(self, "imagenes/red.png")
        self.separationCoefficient=1
        self.chasingCoefficient=8
        
        self.mainCharacter=objectiveChar
        self.objective=objectiveChar #Sets the input class as the objective character
        self.objectivePos[0]=self.objective.currentPos[0] #Sets the objective's tile index as the objective's destination tile
        self.objectivePos[1]=self.objective.currentPos[1]        
        
        #Behaviour tree definition:
        self.rootNode=SelectorNode()
        self.rootNode.addChild(SequenceNode())
        self.rootNode.addChild(SequenceNode())
        self.rootNode.addChild(SequenceNode())
        self.rootNode.getChild(0).addChild(Action(self.verifyMax, 0)) #Verify number of minions=max
        self.rootNode.getChild(0).addChild(Action(self.chaseCharacter)) #Chase character
        self.rootNode.getChild(1).addChild(Action(self.verifyMax, 1)) #Verify number of minions between threshold and max
        self.rootNode.getChild(1).addChild(Action(self.pickObjective)) #Decide to chase main character or reach power and do it
        self.rootNode.getChild(2).addChild(Action(self.verifyMax, 2)) #Verify number of minions below threshold
        self.rootNode.getChild(2).addChild(Action(self.reachPower)) #Reach power
        
        self.currentPos=[120,90] #Initial character position
        self.destPos=[120,90] #Initial destination position (same as initial position)
        self.directionVector=[1,1]
        
        self.numberOfMinions=5 #Number of initial minions the ghost has
        self.maxMinions=5 #Maximum minion capacity
        self.minionsThreshold=3 #Inferior threshold for the number of minions. Triggers the "star chase" mode.
        self.minions=[] #Create minions list
        for i in range(0,self.numberOfMinions): #Fill minions list
            self.minions.append(Minion(self, [self.currentPos[0], self.currentPos[1]])) #Create minion instance with self as its boss and ond self position
        
    
    def executeTree(self):
        self.rootNode.executeNode()
        
    
    def verifyMax(self, verificationType):
        if verificationType==0:
            return self.numberOfMinions==self.maxMinions
        elif verificationType==1:
            return (self.numberOfMinions<self.maxMinions and self.numberOfMinions>=self.minionsThreshold)
        elif verificationType==2:
            return self.numberOfMinions<self.minionsThreshold


    def chaseCharacter(self):
        print("Personaje")
        self.objective=self.mainCharacter
        self.move()
    
    
    def reachPower(self):
        print("Poder")
        if (len(powers)!=0):
            self.objective=powers[0]
        else:
            self.objective=self.mainCharacter
        self.move()
    
    
    def pickObjective(self):
        print("Escoger")
        if (len(powers)!=0):
            print("Hay poder")
            distanceToMainCharacter=calculateContinuousDistance(self.currentPos, self.mainCharacter.currentPos)
            distanceToPowerUp=calculateContinuousDistance(self.currentPos, powers[0].currentPos)
            if(distanceToPowerUp<distanceToMainCharacter):
                self.reachPower()
            else:
                self.chaseCharacter()
        else:
            print("No hay poder")
            self.chaseCharacter()
        
        
    def killMinion(self):
        if(self.numberOfMinions>0):
            self.minions.pop() #Remove minion from the list and the garbage collector should delete it from memory
            self.numberOfMinions-=1
    
    
    def respawnMinion(self):
        if(self.numberOfMinions<self.maxMinions):
            self.minions.append(Minion(self, [self.currentPos[0], self.currentPos[1]])) #Create minion instance with self as its boss and ond self position
            self.numberOfMinions+=1
            
            
    def checkCollision(self): #Checks collision with the main character
        if(pygame.sprite.collide_rect(self, self.mainCharacter)):
            return True
        for minion in self.minions:
            if(pygame.sprite.collide_rect(minion, self.mainCharacter)):
                return True
        return False


    """def findPath(self): #Function for the "Pathfinding" state
        pathFinder=AStar() #Creates instance of the A* path finder class
        self.objectivePos[0]=self.objective.currentPos[0] #Gets the objective's position tile
        self.objectivePos[1]=self.objective.currentPos[1]
        self.path=pathFinder.algorithm(self.currentPos, self.objectivePos) #Finds the shortest path to the objective's destination tile
        self.path.pop(0) #As the first tile in the path is the current destination, pop it from the path in order to not try to reach it while already on it
        
        del pathFinder #Releases the memory of the A* class instance
        self.currentState=self.states.Pathfollowing #A path has been found, follow it"""
        
        
    def move(self):
        enemy.move(self) #Call the regular enemy pathfollowing function
        
        self.objectivePos[0]=self.objective.currentPos[0] #Gets the objective's position tile
        self.objectivePos[1]=self.objective.currentPos[1]        
        x=self.objectivePos[0]-self.currentPos[0]
        y=self.objectivePos[1]-self.currentPos[1]
        distance=(abs(x)+abs(y))/10
        if(distance==0): #Distance is 0
            distance=0.1 #Set it to a very small value to avoid division by zero
        
        print("Ghost pos", self.currentPos)
        print("Obj pos", self.objectivePos)
        self.directionVector[0]=x*self.chasingCoefficient/distance
        self.directionVector[1]=y*self.chasingCoefficient/distance
        
        if len(obstacles): #There are obstacles in the level
            for obst in obstacles: #Apply separation rules to obstacles (concatenation of lists)
                x=obst.currentPos[0]-self.currentPos[0]
                y=obst.currentPos[1]-self.currentPos[1]
                distance=calculateMagnitude(x, y)
                if(distance<10): #Obstacle is too near (collision)
                    distance/=5
                if(distance): #Character's position is different
                    #Separation force is contrary to the vector from self to obstacle
                    self.directionVector[0]-=(x/distance)*self.separationCoefficient*10
                    self.directionVector[1]-=(y/distance)*self.separationCoefficient*10
                else: #Character position is the same. Apply force to "disassemble" the group (contrary to the cohesion force)
                    self.directionVector[0]-=self.cohesionVector[0]*self.separationCoefficient*10
                    self.directionVector[1]-=self.cohesionVector[1]*self.separationCoefficient*10
        
        self.directionVector=normalizeVector(self.directionVector)
        
        #if(self.objective.powerUPflag): #Check for main character's powerUPflag
            #self.image=loadImage("imagenes/vulnerable.png", True)
            #self.currentState=self.states.Escape
        if(self.objectivePos[0]!=self.objective.currentPos[0] or self.objectivePos[1]!=self.objective.currentPos[1]): #Main character's tile has changed
            #self.currentState=self.states.Pathfinding #Change state to find a new path since the main character destination tile has changed
                                                      #Changing the state rather than calling the path calculation routine makes this character take 1 cycle to "think" the path,
                                                      #giving the player a little speed advantage and reducing the game difficulty
            #self.findPath()
            self.moveTo()
        
        return True #Function correctly executed



class Minion(enemy): #Minion class. This are the class for the ghosts which follow the leader.
    def __init__(self, leader, initialPos):
        enemy.__init__(self, "imagenes/minion.png")
        self.neighbours=[]
        self.boss=leader #Assign the leader ghost as the boss of this minion
        self.directionVector=[0,0] #[x, y]
        self.currentPos=initialPos
        self.cohesionCoefficient=4
        self.alignmentCoefficient=2
        self.separationCoefficient=4

        
    def findNeighbours(self): #Function which simulates the minion view. Must be executed periodically.
        self.directionVector=[0,0] #The direction vector has to be set to 0 for recalculation
        neighbourhood=30
        visionAngle=240*math.pi/180
        self.neighbours=[]
        for partner in self.boss.minions: #Checks for every minion with the same boss (partners)
            x=partner.currentPos[0]-self.currentPos[0]
            y=partner.currentPos[1]-self.currentPos[1]
            partnerAngle=abs(calculateAngle(x, y)-calculateAngle(self.directionVector[0], self.directionVector[1]))
            if  partner!=self and calculateContinuousDistance(self.currentPos, partner.currentPos) < neighbourhood and partnerAngle < visionAngle: #240 degrees vision.
                self.neighbours.append(partner) #Add neighbour
                #print("Hola")
        #if calculateContinuousDistance(self.currentPos, self.boss.currentPos) < neighbourhood: #The leader is a neighour
            #self.neighbours.append(self.boss)
            #print("Mundo")
        self.neighbours.append(self.boss)
        
        
    def cohesionRule(self):
        if len(self.neighbours): #Checks if a neighbour exists
            averageX=0
            averageY=0
            for neighbour in self.neighbours: #Take each neighbour into account for calculating the average position for all of them
                averageX+=neighbour.currentPos[0] #Add X coordinate
                averageY+=neighbour.currentPos[1] #Add Y coordinate
            #Calculate averages by dividing by the number of neighbours
            averageX=averageX/len(self.neighbours)
            averageY=averageY/len(self.neighbours)
            
            x=averageX-self.currentPos[0]
            y=averageY-self.currentPos[1]
            direction=calculateAngle(x, y)
            distance=calculateMagnitude(x, y)
            self.cohesionVector=[x, y]
            self.directionVector[0]+=distance*self.cohesionVector[0]*self.cohesionCoefficient
            self.directionVector[1]+=distance*self.cohesionVector[1]*self.cohesionCoefficient
        
        
    def alignmentRule(self):
        if len(self.neighbours): #Checks if a neighbour exists
            averageXDirection=0
            averageYDirection=0
            ponderationTotal=0
            for neighbour in self.neighbours:
                #The ponderation coefficient is proportional to the direction difference
                ponderationCoefficient=calculateAngle(neighbour.directionVector[0],neighbour.directionVector[1])-calculateAngle(self.directionVector[0],self.directionVector[1])
                ponderationTotal+=ponderationCoefficient
                averageXDirection+=neighbour.directionVector[0]*ponderationCoefficient
                averageYDirection+=neighbour.directionVector[1]*ponderationCoefficient
            
            #Calculate averages by dividing by the total of ponderation coefficients
            if(ponderationTotal): #Ponderation total different from 0 (different neighbour angles)
                averageXDirection=averageXDirection/ponderationTotal
                averageYDirection=averageYDirection/ponderationTotal
            
            self.directionVector[0]+=averageXDirection*self.alignmentCoefficient
            self.directionVector[1]+=averageYDirection*self.alignmentCoefficient
    
    
    def separationRule(self):
        if len(self.neighbours+obstacles): #There are any neighbours or obstacles
            for neighbour in (self.neighbours+obstacles): #Apply separation rules to both neighbours and obstacles (concatenation of lists)
                x=neighbour.currentPos[0]-self.currentPos[0]
                y=neighbour.currentPos[1]-self.currentPos[1]
                distance=calculateMagnitude(x, y)
                #print("Vecino:", neighbour)
                if type(neighbour) is obstacle: #Check if the object is an obstacle in order to apply an special scalation factor
                    #print("Distancia:", distance)
                    if(distance<10): #Obstacle is too near (collision)
                        distance*=3
                    else:
                        distance*=15
                if(distance): #Character's position is different
                    #Separation force is contrary to the vector from self to neighbour
                    self.directionVector[0]-=(x/distance)*self.separationCoefficient*10
                    self.directionVector[1]-=(y/distance)*self.separationCoefficient*10
                else: #Character position is the same. Apply force to "disassemble" the group (contrary to the cohesion force)
                    self.directionVector[0]-=self.cohesionVector[0]*self.separationCoefficient*10
                    self.directionVector[1]-=self.cohesionVector[1]*self.separationCoefficient*10
                
    
    def flocking(self):
        self.findNeighbours()
        self.cohesionRule()
        self.alignmentRule()
        self.separationRule()
        self.directionVector=normalizeVector(self.directionVector)
        self.move()



class halfBakedPizza(pygame.sprite.Sprite): #Main character class
        lastKey=keys.RIGHT #Initial direction
        powerUPflag=False #Power up activated flag. Initially false
        currentPos=[] #Current position
        destPos=[] #Next corner position
        nextCorner=0 #Destination corner index
        lastCorner=0 #Last reached corner index
        directionAngle=0 #Character direction
        powerUPBegin=0 #Time value of the last power up activation
        
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.destPos=[30,50] #Initial facing corner
            self.currentPos=[30,50] #Initial position
            self.nextCorner=48 #Initial destination corner
            self.lastCorner=47 #Initial value of the previous corner
            self.image = loadImage("imagenes/pizza.png", True)
            self.rect = self.image.get_rect()
            self.rect.centerx = ((self.currentPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
            self.rect.centery = ((self.currentPos[1]+1) * 5)
            
            
        def activatePower(self):
            self.powerUPBegin=pygame.time.get_ticks() #Set the actual time value to powerUPbegin
            self.powerUPflag=True #Activate the power up
            
            
        def powerTimer(self):
            if(self.powerUPflag and pygame.time.get_ticks()-self.powerUPBegin>=4000): #The power up is activated and the time is up
                self.powerUPflag=False #Deactivate the power up
                
                
        def changeAngle(self, key):
            if(key==keys.LEFT):
                self.directionAngle-=0.35
            else:
                self.directionAngle+=0.35
        
        
        def move(self): #It's called on each cycle. It manages the movement of the character.
            centerX=self.currentPos[0]+0.5 #Calculate the center of the current tile
            centerY=self.currentPos[1]+0.5 #Calculate the center of the current tile
            nextX=int(centerX+4*(math.cos(self.directionAngle))) #Calculate next X position
            nextY=int(centerY+4*(math.sin(self.directionAngle))) #Calculate next Y position
            
            obstacleCollision=False #By default, the character is not colliding with any obstacle
            for obs in obstacles: #Check for every obstacle if the character collides with it
                if(calculateContinuousDistance([nextX, nextY], obs.currentPos)<10):
                    obstacleCollision=True #Raise flag

            if(nextX<WIDTH2/5 and nextY<HEIGHT2/5 and nextX>0 and nextY>0 and obstacleCollision==False): #The character is inside the limits
                self.currentPos[0]=nextX #Update X pos
                self.currentPos[1]=nextY #Update Y pos
            
            self.powerTimer() #Calls the method that checks if the power up is active and if it has to be deactivated yet

                
        def draw(self): #Draws the character on the current position, looking to the current direction. MIRAR SI SE CAMBIA POR EL DE LA CLASE PADRE
            self.rect.centerx = ((self.currentPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
            self.rect.centery = ((self.currentPos[1]+1) * 5)
            #DIBUJAR EL PERSONAJE EN LA POSICION CALCULADA MIRANDO EN LA DIRECCION ACTUAL Y CAMBIANDO ENTRE SPRITES "ABIERTO" Y "CERRADO" CADA QUE LO DIBUJE (USAR ARREGLO PARA IMAGENES DE DIRECCIONES)
            
        

def main():
    #Setup window
    screen = pygame.display.set_mode((WIDTH2, HEIGHT2)) #Set window size
    pygame.display.set_caption("PAC - Level 2") #Set window caption
    powerXlimits=[20, 180]
    powerYlimits=[20, 120]

    bg=loadImage('imagenes/level2.png', False) #Load background image
    clock = pygame.time.Clock() #Load PyGame clock
    
    #calcLevelMatrix() #Calculate walls positions matrix
    #print (levelMatrix)
    
    powers.append(powerUP([random.randint(powerXlimits[0],powerXlimits[1]),random.randint(powerYlimits[0],powerYlimits[1])])) #Place power on random position
    obstacles.append(obstacle([40,40]))
    obstacles.append(obstacle([40,100]))
    obstacles.append(obstacle([160,100]))
    obstacles.append(obstacle([160,40]))
    
    PAC=halfBakedPizza() #Create character instance
    blinky=RedGhost(PAC) #Create red enemy instance with PAC as it's objective
    #enemies=[blinky, pinky, clyde]
    
    pygame.key.set_repeat(50, 50) #(initialDelay, delayInterval)

    while 1:
        for event in pygame.event.get(): #Reads the pygame events that have happened
            if event.type == pygame.KEYDOWN: #Reads the pressed keys
                if event.key == pygame.K_LEFT: #Pressed key is left arrow
                    key = PAC.changeAngle(keys.LEFT)
                if event.key == pygame.K_RIGHT: #Pressed key is right arrow
                    key = PAC.changeAngle(keys.RIGHT)

            if event.type == QUIT:
                exit()
                
        PAC.move() #Move the main character
        PAC.draw() #Draw the character on it's actual position
        
        blinky.executeTree() #Execute function of the actual state of the red enemy
        blinky.draw() #Draw the enemy on it's actual position
        """pinky.executeState() #Execute function of the actual state of the pink enemy
        pinky.draw() #Draw the enemy on it's actual position        
        clyde.executeState() #Execute function of the actual state of the orange enemy
        clyde.draw() #Draw the enemy on it's actual position """

        screen.blit(bg, (0, 0)) #Put background in position 0,0 (it has to be drawn before other elements for them to appear on top of it)
        
        if(len(powers)==0): #Power has been consumed
            powers.append(powerUP([random.randint(powerXlimits[0],powerXlimits[1]),random.randint(powerYlimits[0],powerYlimits[1])]))
            
        power=powers[0] #Checks collision with the power pellet
        
        for obs in obstacles:
            screen.blit(obs.image, obs.rect)
            if(calculateContinuousDistance(power.currentPos, obs.currentPos)<13): #Recalculate power pos if it collides with any obstacle
                powers.pop()
                powers.append(powerUP([random.randint(powerXlimits[0],powerXlimits[1]),random.randint(powerYlimits[0],powerYlimits[1])]))
            
        screen.blit(power.image, power.rect) #Show pellet sprite (it has to be drawn before the characters in order to appear below them)
        if(power.checkCollision(PAC, blinky)): #If the pellet collides with the main character, remove it
            powers.pop() #Remove the object from the list and the garbage collector should delete it from memory
            
        if(blinky.numberOfMinions==0): #Enemy lose
            del blinky
            blinky=blinky=RedGhost(PAC)
            
        if(blinky.checkCollision()): #Restart game state
            del PAC #Delete main character
            del blinky #Delete main enemy
            if(len(powers)!=0):
                powers.pop() #Delete powerUP
            powers.append(powerUP([random.randint(powerXlimits[0],powerXlimits[1]),random.randint(powerYlimits[0],powerYlimits[1])])) #Place power on random position
            PAC=halfBakedPizza() #Create character instance
            blinky=RedGhost(PAC) #Create red enemy instance with PAC as it's objective
        
        screen.blit(PAC.image, PAC.rect) #Show character
        screen.blit(blinky.image, blinky.rect) #Show enemy 1
        
        for minion in blinky.minions:
            minion.flocking()
            minion.draw()
            screen.blit(minion.image, minion.rect) #Show minion 1
        
        pygame.display.flip() #Update screen
        
        clock.tick(10) #Mantains the FPS less or equal than 10 (Puts a delay to the frame actualization to mantain the game velocity to 10 cycles per second)
        
    return 0

pygame.init()
main()