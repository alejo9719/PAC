import sys
import numpy as np
from enum import Enum
import pygame
from pygame.locals import *
import levels
from levels import *
import heapq
import random

#THE LEVEL GRAPH IS BUILT USING THE CORNERS (OR INTERSECTIONS) IN THE LEVEL. CORNER INDEXES ON THIS IMPLEMENTATION START FROM 1.

class cornerClass: #Class to represent a corner (node) in the A* algorithm
    parent=None #Parent corner in the path
    index=0 #Corner index
    f=0 #Corner (node) cost evaluation function value
    g=0 #Traveled distance cost
    h=0 #Calculated heuristic value


    def __init__(self, cornerIndex):
        self.index=cornerIndex
        
        
    def __lt__(self, other):
        return self.f < other.f


    def updateCorner(self, newParent, newG, newH): #Updates a the corner parameters
        self.g=newG
        self.h=newH
        self.parent=newParent
        self.f=self.h+self.g
    
    
    
class AStar: #Class to calculate the shortest path between corners using A*. Based on http://www.laurentluce.com/posts/solving-mazes-using-python-simple-recursivity-and-a-search/
    
    def __init__(self):
        self.openList=[] #Create the open list
        heapq.heapify(self.openList) #Makes the open list a heap (priority queue, the smallest item in the first position)
        self.closedList=set() #The closed list is a set as the order doesn't matters and a set is faster than a list
        self.cornerClasses=[] #List of corner classes
        

    def createCorners(self): #Fill the corner classes list
        for i in range(1, len(cornerList)+1): #Create a class for each corner and add it to the list in corner index order
            self.cornerClasses.append(cornerClass(i))
            
            
    def getAdjCorners(self, corner):
        adjCorners=[] #List to save the adjacent corners
        adjIndex=0 #Actual analyzed corner index
        for i in adjMatrix[corner.index-1]: #Gets each corner adjacency state respect to the input one
            if(i==1): #Checks if the analyzed corner is adjacent to the current one
                adjCorners.append(self.cornerClasses[adjIndex]) #Create corner instance and append to the adjacent corner list
            adjIndex+=1 #Increment the analyzed corner index
        return adjCorners #Return adjacent corners list
    
    
    def calculatePath(self, corner):
        path=[] #List to save the path positions
        actualCorner=corner #Variable to save the actual analyzed corner
        path.insert(0, cornerList[actualCorner.index-1]) #Adds the position of the ending corner to the path
        while(actualCorner.parent!=None): #Follows the parent tree until it reaches the root
            actualCorner=actualCorner.parent #The corner to add is the parent of the current one
            path.insert(0, cornerList[actualCorner.index-1]) #Extracts the corner position from cornerList and adds it to the path
        return path #Return the path list

    
    def algorithm(self, startIndex, endIndex):
        self.createCorners() #Create the array of classes corresponding to each corner
        start=self.cornerClasses[startIndex-1] #Extracts the class corresponding to the starting corner
        end=self.cornerClasses[endIndex-1] #Extracts the class corresponding to the ending corner
        heapq.heappush(self.openList, [start.f, start]) #Initialize the open list with the start corner
        while len(self.openList): #There are corners left in the open list
            f, corner=heapq.heappop(self.openList) #Get the corner with the lowest F from the open list
            self.closedList.add(corner.index) #Add corner to the closed list as it's being visited
            if corner.index==endIndex: #The destination has been reached
                return self.calculatePath(corner) #Returns the path of positions from the start corner to the end corner
            
            adjCorners=self.getAdjCorners(corner) #Gets the list of corners adjacent to the current one
            for adjCorner in adjCorners: #Checks each corner adjacent to the current one
                if adjCorner.index not in self.closedList: #Adjacent corner hasn't been visited
                    adjG=corner.g+calculateDistance(corner.index, adjCorner.index) #G value of the adjacent corner on the current path
                    #print("Adjacent G: ", adjG)
                    if(adjCorner.f, adjCorner) in self.openList: #The adjacent corner is already in the open list
                        if adjCorner.g>adjG: #Adjacent corner previous G value is greater than the one it has on the current path
                            adjCorner.updateCorner(corner, adjG, calculateDistance(adjCorner.index, end.index)) #Updates the corner parameters (parent, G and H)
                    else: #The adjacent corner is not in the open list
                        adjCorner.updateCorner(corner, adjG, calculateDistance(adjCorner.index, end.index)) #Update the adjacent corner parameters
                        heapq.heappush(self.openList, [adjCorner.f, adjCorner]) #Add the adjacent corner to the open list

                        

class powerUP(pygame.sprite.Sprite):
    
    def __init__(self, initialPos): #Initialization fucntion which takes the initial position of the power up object
        pygame.sprite.Sprite.__init__(self)
        self.image = loadImage("imagenes/powerup.png", True) #Load the sprite image
        self.rect = self.image.get_rect() #Create the sprite collision rectangle using the loaded image dimensions
        self.rect.centery = ((initialPos[0]+1) * HEIGHT / 36)-10 #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centerx = ((initialPos[1]+1) * WIDTH / 28)-10
        
    def checkCollision(self, mainChar): #Checks collision with the main character
        if(pygame.sprite.collide_rect(self, mainChar)):
            mainChar.powerUPflag=True
            return True
        return False



class characterClass(pygame.sprite.Sprite):
    currentPos=[4,1] #Current position in the level grid
    destPos=[4,1] #Destination corner position
    lastKey=keys.RIGHT #Facing direction
    
    
    def __init__(self, spritePath):
        pygame.sprite.Sprite.__init__(self) #Call the parent class initializer
        self.image = loadImage(spritePath, True) #Load the sprite image
        self.rect = self.image.get_rect() #Create the sprite collision rectangle using the loaded image dimensions
        self.rect.centery = ((self.currentPos[0]+1) * HEIGHT / 36)-10 #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centerx = ((self.currentPos[1]+1) * WIDTH / 28)-10   
    
    
    def move(self):
        return
    
    
    def draw(self): #Draws the character on the current position, looking to the current direction
        self.rect.centery = ((self.currentPos[0]+1) * HEIGHT / 36)-9 #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
        self.rect.centerx = ((self.currentPos[1]+1) * WIDTH / 28)-9
        
        
        
class enemy(characterClass):
    states=Enum('states', 'Start Pathfinding Pathfollowing Escape') #Enumeration of the states of the FSM
    currentState=states.Start #Initial state of the enemy
    findClosestCorner=True #Flag to indicate that the corner closest to the main character must be calculated
    destinationCorner=0
    FSMfunc=['waitForSpawn', #Functions to be executed for each state of the FSM
             'findPath',
             'move',
             'run'
             ]
    path=[] #Path to be followed by this enemy
    
    def __init__(self, objectiveChar, spritePath):
        characterClass.__init__(self, spritePath) 
        self.objective=objectiveChar #Sets the input class as the objective character
        self.objectiveIndex=self.objective.nextCorner #Sets the objective's corner index as the objective's destination corner
        
        
    def moveTo(self): #Function to get the next position and its direction respect to the current one
        if(len(self.path)!=0): #Path is not empty (current position is not the main character destination corner)
            self.destPos=self.path.pop(0) #Gets the next waypoint in the path
            #Checks the direction of the destination corner respect to the current one
            if (self.destPos[0]>self.currentPos[0]):
                self.lastKey=keys.DOWN
            elif (self.destPos[0]<self.currentPos[0]):
                self.lastKey=keys.UP
            elif (self.destPos[1]>self.currentPos[1]):
                self.lastKey=keys.RIGHT
            elif (self.destPos[1]<self.currentPos[1]):
                self.lastKey=keys.LEFT
                
                
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
        return
        
        
    def move(self): #Function for the "Pathfollowing" state
        #print('Im following the pizza')
        
        if(self.currentPos==self.destPos): #The character needs to find a corner to move to (destination corner reached)
            self.moveTo() #Finds the next corner to move to.
            #print("moveToExec")
        
        if(self.currentPos!=self.destPos): #The destination hasn't been reached. Keeps moving (if the position had been reached in the previous IF, but recalculated, keeps moving)
            if(self.lastKey==keys.UP or self.lastKey==keys.DOWN):
                j=-1 if self.lastKey==keys.UP else 1 #If lastKey is UP, moves upwards, otherwise moves downwards
                self.currentPos=[self.currentPos[0]+j,self.currentPos[1]] #Moves one tile up or down
            else:
                j=-1 if self.lastKey==keys.LEFT else 1 #If lastKey is LEFT, moves left, otherwise moves right
                self.currentPos=[self.currentPos[0],self.currentPos[1]+j] #Moves one tile up or down
    
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
            self.currentState=self.states.Pathfinding



class RedGhost(enemy): #Red (ambusher) enemy class
    
    def __init__(self, objectiveChar):
        enemy.__init__(self, objectiveChar, "imagenes/red.png")
        self.currentPos=[4,26] #Initial character position
        self.destPos=[4,26] #Initial destination position (same as initial position)        


    def waitForSpawn(self): #Function for the "Start" state
        self.currentState=self.states.Pathfinding #Next state


    def findPath(self): #Function for the "Pathfinding" state
        pathFinder=AStar() #Creates instance of the A* path finder class
        selfIndex=cornerMatrix[self.destPos[0], self.destPos[1]] #Extracts the index of the next corner to be reached by self
        self.objectiveIndex=self.objective.nextCorner #Gets the corner index of the objective's next destination corner
        self.path=pathFinder.algorithm(selfIndex, self.objectiveIndex) #Finds the shortest path to the objective's destination corner
        self.path.pop(0) #As the first corner in the path is the current destination, pop it from the path to not try to reach it while being there
        
        del pathFinder #Releases the memory of the A* class instance
        self.currentState=self.states.Pathfollowing #A path has been found, follow it
        
        
    def move(self):
        enemy.move(self) #Call the regular enemy pathfollowing function
        
        if(self.objective.powerUPflag): #Check for main character's powerUPflag
            self.currentState=self.states.Escape
        elif(self.objectiveIndex!=self.objective.nextCorner): #Main character's destination corner has changed
            #self.currentState=self.states.Pathfinding #Change state to find a new path since the main character destination corner has changed
                                                      #Changing the state rather than calling the path calculation routine makes this character take 1 cycle to "think" the path,
                                                      #giving the player a little speed advantage and reducing the game difficulty
            self.findPath()
        
        
        
class PinkGhost(enemy): #Pink (follower) enemy class
    
    def __init__(self, objectiveChar):
        enemy.__init__(self, objectiveChar, "imagenes/pink.png")
        self.currentPos=[4,12] #Initial character position
        self.destPos=[4,12] #Initial destination position (same as initial position)
        
    
    def waitForSpawn(self): #Function for the "Start" state
        self.currentState=self.states.Pathfinding #Next state
        
        
    def findPath(self): #Function for the "Pathfinding" state
        pathFinder=AStar() #Creates instance of the A* path finder class
        selfIndex=cornerMatrix[self.destPos[0], self.destPos[1]] #Extracts the index of the next corner to be reached by self
        self.objectiveIndex=self.objective.nextCorner #Gets the corner index of the objective's next destination corner
        destinationCorner=self.objective.lastCorner #Gets the corner index of the objective's last reached corner to set it as the path destination
        self.path=pathFinder.algorithm(selfIndex, destinationCorner) #Finds the shortest path to the destination corner
        self.path.pop(0) #As the first corner in the path is the current destination, pop it from the path to not try to reach it while being there
        
        del pathFinder #Releases the memory of the A* class instance
        self.currentState=self.states.Pathfollowing #A path has been found, follow it
        
        
    def move(self):
        enemy.move(self) #Call the regular enemy pathfollowing function
        
        if(self.objective.powerUPflag): #Check for main character's powerUPflag
            self.currentState=self.states.Escape
        elif(self.objectiveIndex!=self.objective.nextCorner): #Main character's destination corner has changed
            #self.currentState=self.states.Pathfinding #Change state to find a new path since the main character destination corner has changed
                                                      #Changing the state rather than calling the path calculation routine makes this character take 1 cycle to "think" the path,
                                                      #giving the player a little speed advantage and reducing the game difficulty
            self.findPath()
        
        
        
class OrangeGhost(enemy): #Orange (stupid, a.k.a. random) enemy class #PODRIA IR A LA ESQUINA EXTERIOR MAS CERCANA AL PERSONAJE EN LUGAR DE A UNA ALEATORIA
    
    def __init__(self, objectiveChar):
        enemy.__init__(self, objectiveChar, "imagenes/orange.png")
        self.currentPos=[17,18] #Initial character position
        self.destPos=[17,18] #Initial destination position (same as initial position)
        
        
    def moveTo(self):
        enemy.moveTo(self) #Executes the regular enemy moveTo function to get positions of the path
        if(len(self.path)==0 and self.objective.powerUPflag==False): #If the path is empty (the destination exterior corner has been reached) calculates a new one immediately unless the main character has the power up
            self.findPath()
        
        
    def waitForSpawn(self): #Function for the "Start" state
        self.currentState=self.states.Pathfollowing #Next state (Makes a decision at each intersection, no previous path calculation is made)
        
        
    def findPath(self): #Function for the "Pathfinding" state
        pathFinder=AStar() #Creates instance of the A* path finder class
        selfIndex=cornerMatrix[self.destPos[0], self.destPos[1]] #Extracts the index of the next corner to be reached by self
        self.objectiveIndex=self.objective.nextCorner #Gets the corner index of the objective's next destination corner
        destinationCorner=random.choice([1, 6, 61, 64]) #Picks one exterior corner to go to
        self.path=pathFinder.algorithm(selfIndex, destinationCorner) #Finds the shortest path to the destination corner
        self.path.pop(0) #As the first corner in the path is the current destination, pop it from the path to not try to reach it while being there
        
        del pathFinder #Releases the memory of the A* class instance
        self.currentState=self.states.Pathfollowing #A path has been found, follow it
        
        
    def move(self):
        enemy.move(self) #Call the regular enemy pathfollowing function
        
        if(self.objective.powerUPflag): #Check for main character's powerUPflag
            self.currentState=self.states.Escape
        #Here, the main character's destination corner doesn't matter as this enemy moves randomly across the map
        
        
        
class halfBakedPizza(pygame.sprite.Sprite): #Main character class
        lastKey=keys.RIGHT #Initial direction
        powerUPflag=False #Power up activated flag. Initially false
        currentPos=[] #Current position
        destPos=[] #Next corner position
        nextCorner=0 #Destination corner index
        lastCorner=0 #Last reached corner index
        
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.destPos=[26,15] #Initial facing corner
            self.currentPos=[26,13] #Initial position
            self.nextCorner=48 #Initial destination corner
            self.lastCorner=47 #Initial value of the previous corner
            self.image = loadImage("imagenes/pizza.png", True)
            self.rect = self.image.get_rect()
            self.rect.centery = ((self.currentPos[0]+1) * HEIGHT / 36)-10 #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
            self.rect.centerx = ((self.currentPos[1]+1) * WIDTH / 28)-10
            
            
        def togglePower(self):
            if(self.powerUPflag):
                self.powerUPflag=False
            else:
                self.powerUPflag=True
            #CAMBIAR LA ACCION AL COLISIIONAR CON FANTASMAS
        
        
        def moveTo(self, key): #Calculates the corner the character has to move to (if possible) when it reaches a corner or the direction changes
            found=0
            if(key==keys.UP or key==keys.DOWN): #Checks for corners connected to the current one upwards or downwards (key pressed is UP or DOWN)
                i=self.currentPos[0]
                j=-1 if key==keys.UP else 1 #If key is UP, looks upwards, otherwise looks downwards
                while(i>=0 and i<35 and found==0): #Searches for corners on top or below the current position until one is found. 0 and 35 are the limits of the cornerMatrix
                    i+=j
                    found=cornerMatrix[i,self.currentPos[1]]
            elif(key==keys.LEFT or key==keys.RIGHT): #Similar to the previous IF, but using LEFT and RIGHT
                i=self.currentPos[1]
                j=-1 if key==keys.LEFT else 1
                while(i>=0 and i<27 and found==0):
                    i+=j
                    found=cornerMatrix[self.currentPos[0],i]
                    
            if(found!=0): #A corner was found on the specified direction from the actual one
                #print('Found: ',found)
                if(adjMatrix[self.nextCorner-1][found-1]==1): #The current corner and the found one are connected
                    self.destPos=cornerList[found-1] #The found corner is the new destination
                    #print("Destpos: ", self.destPos)
                    self.lastCorner=self.nextCorner #The previous destination corner is now the last one
                    self.nextCorner=cornerMatrix[self.destPos[0], self.destPos[1]] #Updates the destination corner
                    self.lastKey=key #Updates the movement direction
                elif(key!=self.lastKey): #If no adjacent corner was found on the specified direction, keeps looking on the current one
                    self.moveTo(self.lastKey)
            elif(key!=self.lastKey): #If no adjacent corner was found on the specified direction, keeps looking on the current one
                self.moveTo(self.lastKey)
            #If there is no corner connected to the current one on the specified direction, the destination corner stays the same
        
        
        def move(self, key): #It's called on each cycle.
            if(self.currentPos==self.destPos or key!=self.lastKey): #The character needs to find a corner to move to (corner reached or direction changed)
                self.moveTo(key) #Finds the corner. If the direction hasn't changed, keeps moving in the same direction

            if(self.currentPos!=self.destPos): #The destination hasn't been reached. Keeps moving (if the position had been reached in the previous IF, but recalculated, keeps moving)
                if(self.lastKey==keys.UP or self.lastKey==keys.DOWN):
                    j=-1 if self.lastKey==keys.UP else 1 #If lastKey is UP, moves upwards, otherwise moves downwards
                    self.currentPos=[self.currentPos[0]+j,self.currentPos[1]] #Moves one tile up or down
                else:
                    j=-1 if self.lastKey==keys.LEFT else 1 #If lastKey is LEFT, moves left, otherwise moves right
                    self.currentPos=[self.currentPos[0],self.currentPos[1]+j] #Moves one tile up or down
            
            #VER EL CASO EN QUE MUERE (SE DEBEN BORRAR Y CREAR DE NUEVO LAS INSTANCIAS DEL PERSONAJE, ENEMIGOS Y REINICIAR LOS PUNTOS EN EL MAPA, PERO MANTENER PUNTAJES)

                
        def draw(self): #Draws the character on the current position, looking to the current direction. MIRAR SI SE CAMBIA POR EL DE LA CLASE PADRE
            self.rect.centery = ((self.currentPos[0]+1) * HEIGHT / 36)-9 #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
            self.rect.centerx = ((self.currentPos[1]+1) * WIDTH / 28)-9
            #DIBUJAR EL PERSONAJE EN LA POSICION CALCULADA MIRANDO EN LA DIRECCION ACTUAL Y CAMBIANDO ENTRE SPRITES "ABIERTO" Y "CERRADO" CADA QUE LO DIBUJE (USAR ARREGLO PARA IMAGENES DE DIRECCIONES)
            
        

def main():
    #Setup window
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Set window size
    pygame.display.set_caption("PAC") #Set window caption

    bg=loadImage('imagenes/Level1.png', False) #Load background image
    clock = pygame.time.Clock() #Load PyGame clock
    
    calcCornerMatrix(cornerList) #Calculate position corner number matrix
    
    PAC=halfBakedPizza() #Create character instance
    blinky=RedGhost(PAC) #Create red enemy instance with PAC as it's objective
    pinky=PinkGhost(PAC) #Create pink enemy instance with PAC as it's objective
    clyde=OrangeGhost(PAC) #Create orange enemy instance with PAC as it's objective
    enemies=[blinky, pinky, clyde]
    powers=[powerUP([6,1]), powerUP([6,26]), powerUP([26,1]), powerUP([26,26])]
    
    key=keys.RIGHT #Initially pressed key

    while 1:
        for event in pygame.event.get(): #Reads the pygame events that have happened
            if event.type == pygame.KEYDOWN: #Reads the pressed keys
                if event.key == pygame.K_UP: #Pressed key is up arrow
                    key = keys.UP
                if event.key == pygame.K_DOWN: #Pressed key is down arrow
                    key = keys.DOWN
                if event.key == pygame.K_LEFT: #Pressed key is left arrow
                    key = keys.LEFT
                if event.key == pygame.K_RIGHT: #Pressed key is right arrow
                    key = keys.RIGHT
                if event.key == pygame.K_SPACE: #Pressed key is spacebar
                    PAC.togglePower()

            if event.type == QUIT:
                exit()
                
        PAC.move(key) #Move the main character
        PAC.draw() #Draw the character on it's actual position
        
        blinky.executeState() #Execute function of the actual state of the red enemy
        blinky.draw() #Draw the enemy on it's actual position
        pinky.executeState() #Execute function of the actual state of the pink enemy
        pinky.draw() #Draw the enemy on it's actual position        
        clyde.executeState() #Execute function of the actual state of the orange enemy
        clyde.draw() #Draw the enemy on it's actual position

        screen.blit(bg, (0, 0)) #Put background in position 0,0 (it has to be drawn before other elements for them to appear on top of it)
        
        for power in powers: #Checks collision with every power pellet
            screen.blit(power.image, power.rect) #Show pellet sprite (it has to be drawn before the characters in order to appear below them)
            if(power.checkCollision(PAC)): #If the pellet collides with the main character, remove it
                powers.remove(power) #Remove the object from the list and the garbage collector should delete it from memory
                
        screen.blit(PAC.image, PAC.rect) #Show character
        screen.blit(blinky.image, blinky.rect) #Show enemy 1
        screen.blit(pinky.image, pinky.rect) #Show enemy 2
        screen.blit(clyde.image, clyde.rect) #Show enemy 3
        
        pygame.display.flip() #Update screen
        
        #Check collisions between the main character and the enemies:
        i=0 #Index of the enemy
        for enemy in enemies:
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
            i+=1
        
        clock.tick(10) #Mantains the FPS less or equal than 10 (Puts a delay to the frame actualization to mantain the game velocity to 10 cycles per second)
        
    return 0

pygame.init()
main()
