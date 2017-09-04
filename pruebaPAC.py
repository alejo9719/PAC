import sys
import numpy as np
from enum import Enum
import pygame
from pygame.locals import *
import levels
from levels import *
import heapq

class cornerClass:
    parent=None
    index=0
    f=0
    g=0
    h=0


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
    cornerClasses=[] #List of corner classes
    
    def __init__(self):
        self.openList=[] #Create the open list
        heapq.heapify(self.openList) #Makes the open list a heap (priority queue, the smallest item in the first position)
        self.closedList=set() #The closed list is a set as the order doesn't matters and a set is faster than a list
        

    def createCorners(self): #Fill the corner classes list
        for i in range(1, len(cornerList)): #Create a class for each corner and add it to the list in corner index order
            self.cornerClasses.append(cornerClass(i))
            
            
    def getAdjCorners(self, corner):
        adjCorners=[]
        adjIndex=0
        for i in adjMatrix[corner.index-1]:
            if(i==1):
                adjCorners.append(self.cornerClasses[adjIndex]) #Create corner instance and append to the adjacent corner list
            adjIndex+=1
        return adjCorners
        
        
    def calculateDistance(self, corner1, corner2):
        #Extracts the corners' positions and calculates the distance in tiles:
        distance=abs(cornerList[corner1.index-1][0]-cornerList[corner2.index-1][0])+abs(cornerList[corner1.index-1][1]-cornerList[corner2.index-1][1])
        return distance
    
    
    def calculatePath(self, corner):
        path=[]
        actualCorner=corner
        path.insert(0, cornerList[actualCorner.index-1]) #Adds the position of the ending corner to the path
        while(actualCorner.parent!=None): #Follows the parent tree until it reaches the root
            actualCorner=actualCorner.parent #The corner to add is the parent of the current one
            path.insert(0, cornerList[actualCorner.index-1]) #Extracts the corner position from cornerList and adds it to the path
        return path

    
    def algorithm(self, startIndex, endIndex):
        self.createCorners()
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
                    adjG=corner.g+self.calculateDistance(corner, adjCorner) #G value of the adjacent corner on the current path
                    #print("Adjacent G: ", adjG)
                    if(adjCorner.f, adjCorner) in self.openList: #The adjacent corner is already in the open list
                        if adjCorner.g>adjG: #Adjacent corner previous G value is greater than the one it has on the current path
                            adjCorner.updateCorner(corner, adjG, self.calculateDistance(adjCorner, end)) #Updates the corner parameters (parent, G and H)
                    else: #The adjacent corner is not in the open list
                        adjCorner.updateCorner(corner, adjG, self.calculateDistance(adjCorner, end)) #Update the adjacent corner parameters
                        heapq.heappush(self.openList, [adjCorner.f, adjCorner]) #Add the adjacent corner to the open list

                        

class character(pygame.sprite.Sprite):
    currentPos=[0,0]
    
    def findPath(self):
        return
    
    
    def move(self):
        return
    
    
    def draw(self):
        return



class RedGhost: #Red enemy class
    states=Enum('states', 'Start Pathfinding Pathfollowing Escape') #Enumeration of the states of the FSM
    currentState=states.Start #Initial state of the enemy
    FSMfunc=['waitForSpawn', #Functions to be executed for each state of the FSM
             'calculatePath',
             'followPath',
             'run'
             ]


    def executeState(self): #Executes the function corresponding to the current state
        eval('self.'+self.FSMfunc[self.currentState.value-1]+'()') #Evalues the expression func() using the following format: #eval('self'+'funcname'+'('+par+')')


    def waitForSpawn(self): #Function for the "Start" state
        print('Im waiting')
        self.currentState=self.states.Pathfinding #Next state


    def calculatePath(self): #Function for the "Pathfinding" state
        print('Finding best path...')
        self.currentState=self.states.Pathfollowing


    def followPath(self): #Function for the "Pathfollowing" state
        print('Im following the pizza')
        self.currentState=self.states.Escape


    def run(self): #Function for the "Escape" state
        #print('RUN!')
        self.currentState=self.states.Escape
        
        
        
class halfBakedPizza(pygame.sprite.Sprite): #Main character class
        currentPos=[26,13] #Initial position
        destPos=[26,15] #Initial facing corner
        lastCorner=48 #Initial destination corner
        lastKey=keys.RIGHT #Initial direction
        
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = loadImage("imagenes/pizza.png", True)
            self.rect = self.image.get_rect()
            self.rect.centery = ((self.currentPos[0]+1) * HEIGHT / 36)-10 #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
            self.rect.centerx = ((self.currentPos[1]+1) * WIDTH / 28)-10      
        
        
        def moveTo(self, key): #Calculates the corner the character has to move to (if possible) when it reaches a corner or the direction changes
            found=0
            if(key==keys.UP or key==keys.DOWN): #Checks for corners connected to the current one upwards or downwards (key pressed is UP or DOWN)
                i=self.currentPos[0]
                j=-1 if key==keys.UP else 1 #If key is UP, looks upwards, otherwise looks downwards
                while(i>0 and i<35 and found==0): #Searches for corners on top or below the current position until one is found. 0 and 35 are the limits of the cornerMatrix
                    i+=j
                    found=cornerMatrix[i,self.currentPos[1]]
            elif(key==keys.LEFT or key==keys.RIGHT): #Similar to the previous IF, but using LEFT and RIGHT
                i=self.currentPos[1]
                j=-1 if key==keys.LEFT else 1
                while(i>0 and i<27 and found==0):
                    i+=j
                    found=cornerMatrix[self.currentPos[0],i]
                    
            if(found!=0): #A corner was found on the specified direction from the actual one
                print('Found: ',found)
                if(adjMatrix[self.lastCorner-1][found-1]==1): #The current corner and the found one are connected
                    self.destPos=cornerList[found-1] #The found corner is the new destination
                    print("Destpos: ", self.destPos)
                    self.lastCorner=cornerMatrix[self.destPos[0], self.destPos[1]] #Actualiza la esquina destino
                    self.lastKey=key #Updates the movement direction
                elif(key!=self.lastKey): #If no adjacent corner was found on the specified direction, keeps looking on the current one
                    self.moveTo(self.lastKey)
            elif(key!=self.lastKey): #If no adjacent corner was found on the specified direction, keeps looking on the current one
                self.moveTo(self.lastKey)
            #If there is no corner connected to the current one on the specified direction, the destination corner stays the same
        
        
        def move(self, key): #It's called on each cycle.
            if(self.currentPos==self.destPos or key!=self.lastKey): #The character needs to find a corner to move to (corner reached or direction changed)
                self.moveTo(key) #Finds the corner. If the direction hasn't changed, keeps moving in the same direction
                print("moveToExec")

            if(self.currentPos!=self.destPos): #The destination hasn't been reached. Keeps moving (if the position had been reached in the previous if but recalculated, keeps moving)
                if(self.lastKey==keys.UP or self.lastKey==keys.DOWN):
                    j=-1 if self.lastKey==keys.UP else 1 #If lastKey is UP, moves upwards, otherwise moves downwards
                    self.currentPos=[self.currentPos[0]+j,self.currentPos[1]] #Moves one tile up or down
                else:
                    j=-1 if self.lastKey==keys.LEFT else 1 #If lastKey is LEFT, moves left, otherwise moves right
                    self.currentPos=[self.currentPos[0],self.currentPos[1]+j] #Moves one tile up or down
            
            print(self.currentPos)

                
        def draw(self): #Draws the character on the current position, looking to the current direction
            #HACER MAPEO DE TILES A POSICION EN PIXELES
            self.rect.centery = ((self.currentPos[0]+1) * HEIGHT / 36)-9 #The tile position is converted to pixels position (1 is added to currentPos to eliminate 0 based indexing)
            self.rect.centerx = ((self.currentPos[1]+1) * WIDTH / 28)-9
            #DIBUJAR EL PERSONAJE EN LA POSICION CALCULADA MIRANDO EN LA DIRECCION ACTUAL Y CAMBIANDO ENTRE SPRITES "ABIERTO" Y "CERRADO" CADA QUE LO DIBUJE (USAR ARREGLO PARA IMAGENES DE DIRECCIONES)
            return
            
        

def main():
    #Setup window
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Set window size
    pygame.display.set_caption("PAC") #Set window caption

    bg=loadImage('imagenes/Level1.png', False) #Load background image
    clock = pygame.time.Clock() #Load PyGame clock
    
    calcCornerMatrix(cornerList) #Calculate position corner number matrix
    
    blinky=RedGhost() #Create red enemy instance
    PAC=halfBakedPizza() #Create character instance
    pathFinder=AStar()
    
    path=pathFinder.algorithm(6, 42)
    print("Path: ",path)
    
    key=keys.RIGHT #Initially pressed key

    while 1:
        blinky.executeState() #Execute function of the actual state of the red enemy
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    key = keys.UP
                if event.key == pygame.K_DOWN:
                    key = keys.DOWN
                if event.key == pygame.K_LEFT:
                    key = keys.LEFT
                if event.key == pygame.K_RIGHT:
                    key = keys.RIGHT

            if event.type == QUIT:
                exit()
                
        #CADA QUE SE CUMPLA EL TIEMPO PARA ACTUALIZAR FRAME:
        PAC.move(key) #Move the main character
        PAC.draw()

        screen.blit(bg, (0, 0)) #Put background in position 0,0
        screen.blit(PAC.image, PAC.rect) #Draw character
        pygame.display.flip() #Update screen
        
        clock.tick(10) #Mantains the FPS less or equal than 10
        
    return 0

pygame.init()
main()
