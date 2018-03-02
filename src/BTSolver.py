import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you assign them
        Return: true is assignment is consistent, false otherwise
    """
    def forwardChecking ( self ):
        for v in self.network.variables:
            if v.isAssigned():
                for vNeighbor in self.network.getNeighborsOfVariable(v):
                    if v.domain.values[0] in vNeighbor.domain.values:
                        self.trail.push(vNeighbor)
                        vNeighbor.removeValueFromDomain(v.domain.values[0])
        return self.assignmentsCheck()
    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you assign them
        Return: true is assignment is consistent, false otherwise
    """
    def norvigCheck ( self ):
        for v in self.network.variables:
            if v.isAssigned():
                for vNeighbor in self.network.getNeighborsOfVariable(v):
                    if v.domain.values[0] in vNeighbor.domain.values:
                        self.trail.push(vNeighbor)
                        vNeighbor.removeValueFromDomain(v.domain.values[0])
        for v in self.network.variables:
            if not v.isAssigned():
                assign_val = True
                for d in v.domain.values:
                    for vNeighbor in self.network.getNeighborsOfVariable(v):
                        if d in vNeighbor.domain.values:
                            assign_val = False
                    if assign_val == True:
                        self.trail.push(v)
                        v.assignValue(d)
        return self.assignmentsCheck()

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        firstUnassigned = self.getfirstUnassignedVariable()
        if firstUnassigned == None:
            return None
        sLen = firstUnassigned.domain.size()
        result = firstUnassigned
        for v in self.network.variables:
            if not v.isAssigned() and v.domain.size() < sLen:
                sLen = v.domain.size()
                result = v
        return result
    """
        Part 2 TODO: Implement the Degree Heuristic

        Return: The unassigned variable with the most unassigned neighbors
    """
    def getDegree ( self ):
        num = 0 
        result = self.getfirstUnassignedVariable()
        if result == None:
            return None
        for v in self.network.variables:
            if not v.isAssigned:
                vNum = 0
                for vNeigh in self.network.getNeighborsOfVariable(v):
                    if not vNeigh.isAssigned:
                        vNum += 1
                if vNum > num:
                    result = v
        return result

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
        firstUnassigned = self.getfirstUnassignedVariable()
        if firstUnassigned == None:
            return None
        sLen = firstUnassigned.domain.size()
        result = [firstUnassigned]
        for v in self.network.variables:
            if not v.isAssigned() and v.domain.size() < sLen:
                sLen = v.domain.size()
                result = [v]
            elif not v.isAssigned() and v.domain.size() == sLen:
                result.append(v)
        final_result = result[0]
        if len(result) > 1:
            num = 0
            for r in result:
                rNum = 0
                for rNeigh in self.network.getNeighborsOfVariable(v):
                    if not rNeigh.isAssigned:
                        rNum += 1
                if rNum > num:
                    final_result = r
        return final_result
    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):
        import operator
        dictionary = dict()
        for val in v.domain.values:
            num = 0 
            for vNeigh in self.network.getNeighborsOfVariable(v):
                if not vNeigh.isAssigned:
                    if val in vNeigh.domain.values:
                        num +=1
            dictionary[val] = num
        result = []
        for key,val in sorted(dictionary.items(), key=operator.itemgetter(1)):
            result.append(key)
        return result

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
