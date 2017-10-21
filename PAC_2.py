import sys
import numpy as np
from enum import Enum
import pygame
from pygame.locals import *
import levels
from levels import *
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
                    adjG=tile.g+calculateContinuousDistance(tile, adjTile) #G value of the adjacent tile on the current path
                    #print("Adjacent G: ", adjG)
                    if(adjTile.f, adjTile) in self.openList: #The adjacent tile is already in the open list
                        if adjTile.g>adjG: #Adjacent tile previous G value is greater than the one it has on the current path
                            adjTile.updateTile(tile, adjG, calculateContinuousDistance(adjTile, end)) #Updates the tile parameters (parent, G and H)
                    else: #The adjacent tile is not in the open list
                        adjTile.updateTile(tile, adjG, calculateContinuousDistance(adjTile, end)) #Update the adjacent tile parameters
                        heapq.heappush(self.openList, [adjTile.f, adjTile]) #Add the adjacent tile to the open list

                        

class powerUP(pygame.sprite.Sprite):
    
    def __init__(self, initialPos): #Initialization fucntion which takes the initial position of the power up object
        pygame.sprite.Sprite.__init__(self)
        self.image = loadImage("imagenes/powerup.png", True) #Load the sprite image
        self.rect = self.image.get_rect() #Create the sprite collision rectangle using the loaded image dimensions
        self.rect.centery = ((initialPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centerx = ((initialPos[1]+1) * 5)
        
    def checkCollision(self, mainChar): #Checks collision with the main character
        if(pygame.sprite.collide_rect(self, mainChar)):
            mainChar.activatePower()
            return True
        return False



class characterClass(pygame.sprite.Sprite):
    currentPos=[4,1] #Current position in the level grid
    destPos=[4,1] #Destination corner position
    
    
    def __init__(self, spritePath):
        pygame.sprite.Sprite.__init__(self) #Call the parent class initializer
        self.image = loadImage(spritePath, True) #Load the sprite image
        self.rect = self.image.get_rect() #Create the sprite collision rectangle using the loaded image dimensions
        self.rect.centery = ((self.currentPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centerx = ((self.currentPos[1]+1) * 5)   
    
    
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
    objectivePos=[0,0]
    destPos=[0,0]
    FSMfunc=['waitForSpawn', #Functions to be executed for each state of the FSM
             'findPath',
             'move',
             'run'
             ]
    path=[] #Path to be followed by this enemy
    
    def __init__(self, objectiveChar, spritePath):
        self.sprite=spritePath #Save original sprite path to use it when going out of vulnerable state
        characterClass.__init__(self, spritePath) #Initialize the character
        self.objective=objectiveChar #Sets the input class as the objective character
        self.objectivePos[0]=self.objective.currentPos[0] #Sets the objective's tile index as the objective's destination tile
        self.objectivePos[1]=self.objective.currentPos[1]
        self.directionAngle=0
        
        
    def moveTo(self): #Function to get the next position and its direction respect to the current one
        #if(len(self.path)!=0): #Path is not empty (current position is not the main character destination tile)
        #    self.destPos=self.path.pop(0) #Gets the next waypoint in the path
        self.objectivePos[0]=self.objective.currentPos[0] #Gets the objective's position tile
        self.objectivePos[1]=self.objective.currentPos[1]        
        y=self.objectivePos[1]-self.currentPos[1]
        x=self.objectivePos[0]-self.currentPos[0]
        if (x==0):
            if(y>0):
                direction=math.pi/2
            elif(y<0):
                direction=-math.pi/2
        else:
            direction=math.atan(y/x) #Calculate the theoretical direction angle
            #Apply conditions to calculate the real angle
            if(x<0 and y<0):
                direction+=math.pi
            elif (x<0 and y>0):
                direction+=math.pi
            elif (y==0):
                if(x<0):
                    direction=math.pi
                elif(x>0):
                    direction=0
                
        self.directionAngle=direction
                
                
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
        nextX=int(centerX+3*(math.cos(self.directionAngle))) #Calculate next X position
        nextY=int(centerY+3*(math.sin(self.directionAngle))) #Calculate next Y position
        if(nextX<WIDTH2/5 and nextY<HEIGHT2/5 and nextX>0 and nextY>0): #The character is inside the limits
            self.currentPos[0]=nextX #Update X pos
            self.currentPos[1]=nextY #Update Y pos
    
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



class RedGhost(enemy): #Red (ambusher) enemy class
    
    def __init__(self, objectiveChar):
        enemy.__init__(self, objectiveChar, "imagenes/red.png")
        self.currentPos=[120,90] #Initial character position
        self.destPos=[120,90] #Initial destination position (same as initial position)        


    def waitForSpawn(self): #Function for the "Start" state
        self.currentState=self.states.Pathfollowing #Next state


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
        
        if(self.objective.powerUPflag): #Check for main character's powerUPflag
            self.image=loadImage("imagenes/vulnerable.png", True)
            self.currentState=self.states.Escape
        elif(self.objectivePos[0]!=self.objective.currentPos[0] or self.objectivePos[1]!=self.objective.currentPos[1]): #Main character's tile has changed
            #self.currentState=self.states.Pathfinding #Change state to find a new path since the main character destination tile has changed
                                                      #Changing the state rather than calling the path calculation routine makes this character take 1 cycle to "think" the path,
                                                      #giving the player a little speed advantage and reducing the game difficulty
            #self.findPath()
            self.moveTo()
        
        
        
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
            self.rect.centery = ((self.currentPos[0]+1) * 5) #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
            self.rect.centerx = ((self.currentPos[1]+1) * 5)
            
            
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
            if(nextX<WIDTH2/5 and nextY<HEIGHT2/5 and nextX>0 and nextY>0): #The character is inside the limits
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

    bg=loadImage('imagenes/level2.png', False) #Load background image
    clock = pygame.time.Clock() #Load PyGame clock
    
    #calcLevelMatrix() #Calculate walls positions matrix
    #print (levelMatrix)
    
    PAC=halfBakedPizza() #Create character instance
    blinky=RedGhost(PAC) #Create red enemy instance with PAC as it's objective
    #enemies=[blinky, pinky, clyde]
    powers=[powerUP([6,1]), powerUP([6,26]), powerUP([26,1]), powerUP([26,26])]
    
    pygame.key.set_repeat(50, 50) #(initialDelay, delayInterval)

    while 1:
        for event in pygame.event.get(): #Reads the pygame events that have happened
            if event.type == pygame.KEYDOWN: #Reads the pressed keys
                if event.key == pygame.K_LEFT: #Pressed key is left arrow
                    key = PAC.changeAngle(keys.LEFT)
                if event.key == pygame.K_RIGHT: #Pressed key is right arrow
                    key = PAC.changeAngle(keys.RIGHT)
                #if event.key == pygame.K_SPACE: #Pressed key is spacebar
                    #PAC.togglePower()

            if event.type == QUIT:
                exit()
                
        PAC.move() #Move the main character
        PAC.draw() #Draw the character on it's actual position
        
        blinky.executeState() #Execute function of the actual state of the red enemy
        blinky.draw() #Draw the enemy on it's actual position
        """pinky.executeState() #Execute function of the actual state of the pink enemy
        pinky.draw() #Draw the enemy on it's actual position        
        clyde.executeState() #Execute function of the actual state of the orange enemy
        clyde.draw() #Draw the enemy on it's actual position """

        screen.blit(bg, (0, 0)) #Put background in position 0,0 (it has to be drawn before other elements for them to appear on top of it)
        
        """for power in powers: #Checks collision with every power pellet
            screen.blit(power.image, power.rect) #Show pellet sprite (it has to be drawn before the characters in order to appear below them)
            if(power.checkCollision(PAC)): #If the pellet collides with the main character, remove it
                powers.remove(power) #Remove the object from the list and the garbage collector should delete it from memory"""
                
        screen.blit(PAC.image, PAC.rect) #Show character
        screen.blit(blinky.image, blinky.rect) #Show enemy 1
        """screen.blit(pinky.image, pinky.rect) #Show enemy 2
        screen.blit(clyde.image, clyde.rect) #Show enemy 3"""
        
        pygame.display.flip() #Update screen
        
        #Check collisions between the main character and the enemies:
        i=0 #Index of the enemy
        """for enemy in enemies:
            if(pygame.sprite.collide_rect(PAC, enemy)): #Check collision with each enemy
            #if (pygame.sprite.collide_rect(PAC, blinky) or pygame.sprite.collide_rect(PAC, pinky) or pygame.sprite.collide_rect(PAC, clyde)):
                if(PAC.powerUPflag): #The main character hass the power up
                    #Check which enemy is the "killed" one:
                    if(i==0): 
                        del blinky #Delete the enemy instance
                        blinky=RedGhost(PAC) #Create a new enemy instance
                    if(i==1):
                        del pinky
                        pinky=PinkGhost(PAC)
                    if(i==2):
                        del clyde
                        clyde=OrangeGhost(PAC)
                else:
                    #Delete the actual game state
                    del PAC
                    del blinky
                    del pinky
                    del clyde
                    #Restart the game state
                    PAC=halfBakedPizza() #Create character instance
                    blinky=RedGhost(PAC) #Create red enemy instance with PAC as it's objective
                    pinky=PinkGhost(PAC) #Create pink enemy instance with PAC as it's objective
                    clyde=OrangeGhost(PAC) #Create orange enemy instance with PAC as it's objective
                    key=keys.RIGHT #Set the initial value of key
                
                enemies=[blinky, pinky, clyde] #Restart the enemies list with the new instances
            i+=1 """
        
        clock.tick(10) #Mantains the FPS less or equal than 10 (Puts a delay to the frame actualization to mantain the game velocity to 10 cycles per second)
        
    return 0

pygame.init()
main()