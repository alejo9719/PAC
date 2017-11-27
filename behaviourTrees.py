import sys

class Node:
    def __init__(self):
        self.children=[]
    
    def executeNode(self):
        return
    
    def addChild(self, child):
        self.children.append(child)
        
    def removeChild(self, child):
        self.children.remove(child)
        
    def getChild(self, index):
        return self.children[index]
    
    def updateChild(self, index, newChild):
        self.children[index]=newChild


class SequenceNode(Node):
    def __init__(self):
        Node.__init__(self)
    
    def executeNode(self):
        for child in self.children:
            if child.executeNode()==False:
                return False
        return True #If no child returned False, returns True

    
class SelectorNode(Node):
    def __init__(self):
        Node.__init__(self)
        
    def executeNode(self):
        for child in self.children:
            if child.executeNode()==True:
                return True
        return False #If no children returned True, returns False
    
    
class Action(Node):
    def __init__(self, function, *args): #Create node and define its associated function, a variable number of parameters for the function are passed as *args.
        Node.__init__(self)
        self.actionFunc=function #Save the action function
        self.funcArguments=args #Save the arguments list in a variable
    
    def executeNode(self):
        return self.actionFunc(*self.funcArguments) #Executes the action function using the format: [function_name]([parameters]). The parameters are unfolded using the * operator. Returns the value returned by the function.
        
    def defineAction(self, function, *args):
        self.actionFunc=function #Save the action function
        self.funcArguments=args #Save the arguments list in a variable