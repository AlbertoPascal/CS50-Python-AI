import sys

from crossword import *
import itertools
import copy

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
                    unusable_words.add(word1)
                    #we also update our flag because we will need to make some changes. 
                    made_revision = True
        #Here we update our set to remove the unsuable words. 
        
        
        self.domains[x].difference_update(unusable_words)
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
        
        for variable1, variable2 in itertools.permutations(assignment, 2):
            #We will iterate through the different combinations of variable1, variable2. 
            word1 = assignment[variable1]
            word2 = assignment[variable2]
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
        
        words = self.domains[var]
        
        #I will first iterate through every possible word in my current domain
        #The idea is to see "what would happen" to other domains if I pick each word
        possible_options = {word:0 for word in words}
        
        for word in words:
        #For each of these words, I need to check the nuber of available neighbors
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment.keys():
                    #means I already assigned this neighbor so I should skip. 
                    continue
                #Now I check if this is a useful neighbor
                overlap_point = self.crossword.overlaps[var, neighbor]
                
                if overlap_point is not None:
                    #Means it has a useful word in there too so I look for them:
                    #I extract the overlapping points:
                    letter1, letter2 = overlap_point
                    #print("I had an overlap: ", letter1, " and ", letter2)
                    for second_word in self.domains[neighbor]:
                        #I go through the neighbors words and eliminate the words that conflict with current chosen word
                        if second_word[letter2] != word[letter1]:
                            #I should remove this value from the neighboring domain.
                            #This means I should only add 1 to the count of words discarded in this option. 
                            possible_options[word] = possible_options[word] + 1
                        else:
                            #Otherwise, we can continue searching
                            pass
        #Once I get to this point, I should have mapped all of the "eliminating" values I can when choosing each scenario
        #we sort the words by eliminating values: 
        possible_options =  dict(sorted(possible_options.items(), key=lambda x: -   x[1]))
        #Now that we have the list ordered, we only want to keep the keys:
        ordered_domain = possible_options.keys()
        return ordered_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        remaining_variables = {}
        #We need to store the remaining variables with their length of available words
        for variable in self.crossword.variables:
            if variable in assignment.keys():
                continue
            else:
                #It means it is a variable I have still not assigned so I could possibly return it. 
                #Therefore, I store a tuple of length of remaining values and number of neighbors (remaining_values, degrees)
                remaining_variables[variable] = (len(self.domains[variable]), len(self.crossword.neighbors(variable)))
        
        #Now that we know the remaining variables, we need to classify them according to their complexity
        #We want to sort so that the ones with less remainings are first, but also have the highest degree. 
        #(Therefore, its like remaining values asc, degrees desc)
        remaining_variables = sorted(remaining_variables.items(), key = lambda x:(x[1][0],-x[1][1]))
        #Now that they are ordered, I should have my lowest remaining domains in 
        #I should always be able to return my first value available since it should be both, lowest remainign and highest degree in its category
        return remaining_variables[0][0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        else:
            #if it was not complete, we first get an unassigned variable to start trying
            current_variable = self.select_unassigned_variable(assignment)
            #Then, we need to iterate through every word in that domain
            domain = self.order_domain_values(current_variable, assignment)
            for word in domain:
                #We assign the current variable
                new_assignment = copy.deepcopy(assignment)
                new_assignment[current_variable] = word
                #Then we need to check for arc consistency
                #we prepare the new arc set
                new_arcs = set()
                
                #We store the combination of variables in the assingment that overlap
                for var1, var2 in itertools.permutations(new_assignment.keys(),2):
                    #Since we only want those that overlap
                    if self.crossword.overlaps[var1, var2]:
                        new_arcs.add((var1, var2))
                
                #Then we check for ac3 consistency and assignment consistency
                if self.ac3(new_arcs) and self.consistent(new_assignment):
                    #if all arcs are consistent, we can continue assigning    
                    
                    next_assignment = self.backtrack(new_assignment)
                    if next_assignment is None:
                        #Means we cannot complete the assignment so we erase our bad attempt
                        new_assignment[current_variable] = None
                        pass
                    else:
                        #means our assignment was successful so we can keep it.
                        return next_assignment
                
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

