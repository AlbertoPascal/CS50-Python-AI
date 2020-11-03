import sys

from crossword import *
import itertools

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #We first need to iterate through every variable that exists. 
        for var in self.crossword.variables:
            #Now that we access the variables, we need to iterate through the words
            for word in self.crossword.words:
                #We need to check that the word's number of letters is the same of that of the variable
                #Since variables is an object from Variables class, we can use its .length property. 
                if not len(word) == var.length:
                    #We remove the word from that variable's domain. 
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        made_revision= False
        word_coordinates = self.crossword.overlaps[x, y]
        #print("Starting arc-consisten revision. Initial domains are: ")
        #print("X content: ", x)
        #print("Y content: ", y)
        #print("Domain X: ", self.domains[x])
        #print("Domain Y: ", self.domains[y])
        #print("Overlap value: ", word_coordinates)
        unusable_words = set()
        
        if bool(word_coordinates):
            #If there are intersections between the two words: 
            for word1 in self.domains[x]:
                #For each word of domain X I'll compare with coord in domain Y to see which word overlaps. 
                #print("word1 value", word1)
                can_use = False
                #For each word of domain Y, We will see if the overlap is true. 
                for word2 in self.domains[y]:
                    #print("word2 value", word2)
                    #Whenever an overlap is possible, we mark it as a "valid word" on domain1
                    if word1 != word2 and word1[word_coordinates[0]] == word2[word_coordinates[1]]:
                        can_use = True
                        #print("I can use the combo of ", word1, " and ", word2)
                        break
                    else:
                        #print("These words cannot be used: ", word1, ", ", word2)
                        continue
                #If no overlap was possible with word1, we need to eventually remove word1 from domain x. 
                if not can_use:
                    print("marking word as unsuable ", word1)
                    unusable_words.add(word1)
                    #we also update our flag because we will need to make some changes. 
                    made_revision = True
        #Here we update our set to remove the unsuable words. 
        
        
        self.domains[x].difference_update(unusable_words)
        print("returning that I made a revision: ", made_revision)
        return made_revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
       
        if arcs is None:
            #We should begin with an initial list of arcs to make consistent. 
            arcs = set()
            #To create the domain, we iterate through each permutation of variables
            for var1, var2 in itertools.permutations(self.crossword.variables,2):
                    #Since we only want those that overlap
                    if self.crossword.overlaps[var1, var2]:
                        arcs.add((var1, var2))
        #We create a list of our arcs. This is done to prevent iteration problems when adding to the set.                 
        arc_list = list(arcs)
        #By default, we are not expecting to have any empty domains.
        empty_domains = False
        for x,y in arc_list:
            if self.revise(x, y):
                if len(self.domains[x])<=0 or len(self.domains[y])<=0:
                    #my arc variable's domain is empty so we cannot have any arc consistency
                    empty_domains = True
                    break
                # Append arc to queue after making change to domain (to ensure other arcs stay consistent)
                for neighbor in self.crossword.neighbors(x):
                    arc_list.append((x, neighbor))
        return not(empty_domains)

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        #We are not expecting to have any missing assignments
        missing_assignment = False
        #We iterate through each variable
        for variable in self.crossword.variables:
            #if my variable were to be non-existent, we are missing something
            if variable is None:
                missing_assignment = True
                break
            #if my variable is not mapped in the assignment keys, we are missing something
            if variable not in assignment.keys():
                missing_assignment = True
                break
            if assignment[variable] == None:
                missing_assignment = True
                break
            
        return not(missing_assignment)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #print("Starting to check for consistent: ", assignment)
        
        for variable1, variable2 in itertools.permutations(assignment, 2):
            #We will iterate through the different combinations of variable1, variable2. 
            word1 = assignment[variable1]
            word2 = assignment[variable2]
            #print("Word1: ", word1, " Word2: ", word2)
            if word1 == None or word2 == None:
                #Then my solution is still in progress. Can't validate for this. 
                continue
            #Starting the checks:
            if word1 == word2:
                #words were mapped to a same variable. 
                #print(word1, " was equal to ", word2, " so returning false")
                return False
            if variable1.length != len(word1) or variable2.length != len(word2):
                #means one of my words is longer or shorter than needed. 
                #print("Variable lengths: ", variable1.length, " and ", variable2.length, " whereas words: ", len(word1), " and ", len(word2))
                return False
            #Finally, we need to check whether the variables overlap or not. 
            overlap_point = self.crossword.overlaps[variable1,variable2]
            #print("Overlap point was : ", overlap_point)
            if bool(overlap_point):
                #We have an overlap so we check that the characters are ok. 
                if word1[overlap_point[0]] != word2[overlap_point[1]]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        variable = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(variable, assignment):
            assignment[variable] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is None:
                    assignment[variable] = None
                else:
                    return result

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # structure = 'data/structure0.txt'
    # words = 'data/words0.txt'
    # output = None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

