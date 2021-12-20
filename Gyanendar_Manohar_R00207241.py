# 
#  DECISION ANALYTICS ASSIGNMENT# 1 
#
#  AUTHOR: GYANENDAR MANOHAR
#  STUDENT ID: R00207241
#  DATE: 18/11/2021
#
#
#
#

from ortools.sat.python import cp_model
import numpy
import pandas as pd

#Solution printer:
class logic_puzzel_SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, puzzel_obj):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.puzzle_obj = puzzel_obj        
        self.solutions_ = 0
    
    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_ )
        
        for person in self.puzzle_obj.persons:
            print(" - "+person+":")
            for starter in self.puzzle_obj.starters:
                if (self.Value(self.puzzle_obj.person_starter[person][starter])):
                    print("    - ", starter)
            for main_course in self.puzzle_obj.main_courses:
                if (self.Value(self.puzzle_obj.person_main_course[person][main_course])):
                    print("    - ", main_course)
            for drink in self.puzzle_obj.drinks:
                if (self.Value(self.puzzle_obj.person_drink[person][drink])):
                    print("    - ", drink)
            for desert in self.puzzle_obj.deserts:
                if (self.Value(self.puzzle_obj.person_desert[person][desert])):
                    print("    - ", desert)


class soduku_SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self,soduku_obj):
        cp_model.CpSolverSolutionCallback.__init__(self)    
        self.soduku_obj = soduku_obj
        self.solutions = 0

    def OnSolutionCallback(self):
        
        self.solutions = self.solutions + 1
        print(f"Solution:#{self.solutions}")
        solved = numpy.zeros((9,9),numpy.int16)

        for row in range(9):
            for col in range(9):
                for var_num in range(1,10):
                    if(self.Value(self.soduku_obj.soduku_variables[row][col][var_num])):
                        solved[row][col]=var_num
        self.validate_solution(solved)
         

    def validate_solution(self,solved):
        # Validate solution as sum of all item in row/col
        # and squares(3*3) should be 45
        assert list(numpy.sum(solved,axis=0)).count(45)==9
        assert list(numpy.sum(solved,axis=1)).count(45)==9
        for i in range(0,9,3):
            for j in range(0,9,3):               
               assert numpy.sum(solved[i:i+3,j:j+3])==45
        print(solved)
        print()     
        print()    


class project_planner_SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self,project_planner_obj):
        cp_model.CpSolverSolutionCallback.__init__(self)    
        self.project_planner_obj = project_planner_obj
        self.solutions = 0   

    def OnSolutionCallback(self):
        
        self.solutions = self.solutions + 1
        print(f"Solution:{self.solutions}:")
        #Selected projects holds project name as key and job,month,contractor as value
        selected_projects = {}

        for project in self.project_planner_obj.project_names:
            job_contrator_details = []
            if( self.Value(self.project_planner_obj.project_variables[project])):
                # Reached here means project is selected
                # Findout job & contractors details
                for month,job in self.project_planner_obj.project_job_month[project]:
                    contactor_list = []
                    for contractor in self.project_planner_obj.contractors_names:
                        if(self.Value( self.project_planner_obj.project_month_job_contractor[project][month][job][contractor])):
                            contactor_list.append(contractor)
                    job_contrator_details.append((month,job,contactor_list[0]))

            # if project was not selected there wont be any item in job_contrator_details list
            if(len(job_contrator_details)>0):        
                selected_projects[project]=job_contrator_details        
        
        # print the solution
        for item in selected_projects:
            print(f"{item}->{selected_projects[item]}")
        
        #
        # Calculate the profile margin
        # margin = value - expense
        total_project_value = 0
        total_expense_value = 0
        for item in selected_projects:            
            total_project_value = total_project_value + self.project_planner_obj.project_value[item]             
            for _,job,contractor in selected_projects[item]:
                total_expense_value= total_expense_value + self.project_planner_obj.contractor_job_quote[contractor][job]
        
        print(f"Profit Margin = {total_project_value - total_expense_value}")    



class logic_puzzel:
    def __init__(self,model):

        self.model = model
        
        # James, Daniel, Emily, and Sophie go out for dinner. 
        # They all order a starter, a main course, a desert, and 
        # drinks and they want to order as many different things as possible.

        # object domain: person(james,daniel,emily,sophie)
       
        self.persons = ["James", "Daniel", "Emily", "Sophie"]    
        
        # predicates: starter, main course, drinks, desert    
        # attribute domain for starter
        self.starters = ["prawn_cocktail","onion_soup","mushroom_tart","carpaccio"]
        # attribute domain for main course
        self.main_courses = ["baked_mackerel","fried_chicken","filet_steak","vegan_pie"]
        # attribute domain for drink
        self.drinks = ["beer","red_wine","coke","white_wine"]
        # attribute domain for desert
        self.deserts = ["apple_crumble","ice_cream","chocolate_cake","tiramisu"]

        # placeholder for variables
        self.person_starter = {}
        self.person_main_course = {}
        self.person_desert = {}
        self.person_drink = {}

    
    def create_decision_variable(self):        
        #create variables for all combination of object and attributes
        #startes
        for person in self.persons:        
            variables = {}
            for starter in self.starters:    
                variables[starter] = \
                    self.model.NewBoolVar(person+"<->"+starter)
            self.person_starter[person] = variables
    
        #main course        
        for person in self.persons:        
            variables = {}
            for main_course in self.main_courses:    
                variables[main_course] = \
                    self.model.NewBoolVar(person+"<->"+main_course)
            self.person_main_course[person] = variables
    
        #desert        
        for person in self.persons:        
            variables = {}
            for desert in self.deserts:    
                variables[desert] = \
                    self.model.NewBoolVar(person+"<->"+desert)
            self.person_desert[person] = variables

        #drink
        for person in self.persons:        
            variables = {}
            for drink in self.drinks:    
                variables[drink] = \
                    self.model.NewBoolVar(person+"<->"+drink)
            self.person_drink[person] = variables
    
    def implicit_constraint(self):
        # every object has a different predicates
        #
        # Get all the combination for predicates with object
        #∀𝑥∀𝑦∀𝑧: 𝑥 ≠ 𝑦 ⇒ ¬(starter 𝑥, 𝑧 ∧ starter 𝑦, 𝑧 )
        #∀𝑥∀𝑦∀𝑧: 𝑥 ≠ 𝑦 ⇒ (¬starter 𝑥, 𝑧 ∨ ¬starter 𝑦, 𝑧 )
        for p_index in range(len(self.persons)):
            for p_index_next in range(p_index+1,len(self.persons)):
                #Every person taking different startes
                for s_index in range(len(self.starters)):
                    self.model.AddBoolOr([\
                        self.person_starter[self.persons[p_index]]
                                           [self.starters[s_index]].Not(),
                        self.person_starter[self.persons[p_index_next]]
                                           [self.starters[s_index]].Not()])
                #Every person taking different main courses    
                for m_index in range(len(self.main_courses)):
                    self.model.AddBoolOr([\
                        self.person_main_course[self.persons[p_index]]
                                                [self.main_courses[m_index]].Not(), 
                        self.person_main_course[self.persons[p_index_next]]
                                                [self.main_courses[m_index]].Not()])
                #Every person taking different desert
                for d_index in range(len(self.deserts)):
                    self.model.AddBoolOr([\
                        self.person_desert[self.persons[p_index]]
                                           [self.deserts[d_index]].Not(), 
                        self.person_desert[self.persons[p_index_next]]
                                          [self.deserts[d_index]].Not()])
                #Every person taking different drink
                for dk_index in range(len(self.drinks)):
                    self.model.AddBoolOr([\
                        self.person_drink[self.persons[p_index]]
                                         [self.drinks[dk_index]].Not(), 
                        self.person_drink[self.persons[p_index_next]]
                                         [self.drinks[dk_index]].Not()])
       
        # A predicates belongs to at least one object
        for person in self.persons:            
            
            # A person should take atleast one starter 
            variables = []
            for starter in self.starters:
                variables.append(\
                    self.person_starter[person][starter])
            self.model.AddBoolOr(variables)

            # A person should take atleast one main course 
            variables = []
            for main_course in self.main_courses:
                variables.append(\
                    self.person_main_course[person][main_course])
            self.model.AddBoolOr(variables)

            # A person should take atleast one desert
            variables = []
            for desert in self.deserts:
                variables.append(\
                    self.person_desert[person][desert])
            self.model.AddBoolOr(variables)

            # A person should take atleast one drink 
            variables = []
            for drink in self.drinks:
                variables.append(\
                    self.person_drink[person][drink])
            self.model.AddBoolOr(variables)                                    

        # A predicates belongs to max one object        
        for person in self.persons:
            # A person can take at max one starter
            for i in range(len(self.starters)):
                for j in range(i+1,len(self.starters)):
                    self.model.AddBoolOr([
                            self.person_starter[person]
                                               [self.starters[i]].Not(), 
                            self.person_starter[person]
                                               [self.starters[j]].Not()])
            # A person can take at max one main course
            for i in range(len(self.person_main_course)):
                for j in range(i+1,len(self.person_main_course)):                
                    self.model.AddBoolOr([
                            self.person_main_course[person]
                                                   [self.main_courses[i]].Not(), 
                            self.person_main_course[person]
                                                   [self.main_courses[j]].Not()])
            # A person can take at max one desert
            for i in range(len(self.deserts)):
                for j in range(i+1,len(self.deserts)): 
                    self.model.AddBoolOr([
                            self.person_desert[person]
                                              [self.deserts[i]].Not(), 
                            self.person_desert[person]
                                              [self.deserts[j]].Not()])
            # A person can take at max one drink
            for i in range(len(self.drinks)):
                for j in range(i+1,len(self.drinks)):
                    self.model.AddBoolOr([
                            self.person_drink[person]
                                             [self.drinks[i]].Not(), 
                            self.person_drink[person]
                                             [self.drinks[j]].Not()]) 


    def ex_constraint_1(self):
        # Explicit constraint
        # Emily does not like prawn cocktail as starter
        # nor does she want baked mackerel as main course 

        self.model.AddBoolAnd([
            self.person_starter["Emily"]["prawn_cocktail"].Not()])
        self.model.AddBoolAnd([
            self.person_main_course["Emily"]["baked_mackerel"].Not()])

    def ex_constraint_2(self):
        # Explicit constraint
        # Daniel does not want the prawn cocktail as starter 
        # and James does not drink beer        
        self.model.AddBoolAnd([
            self.person_starter["Daniel"]["prawn_cocktail"].Not()])
        self.model.AddBoolAnd([
            self.person_drink["James"]["beer"].Not()])

    def ex_constraint_3(self):
        # Explicit constraint
        # Sophie will only have fried chicken as main course 
        # if she does not have to take the prawn cocktail as starter
        #
        # So Sophie will have either fried chicken as main course 
        # or prawn cocktail as starter but not both together
                        
        self.model.AddBoolXOr([
            self.person_main_course["Sophie"]["fried_chicken"],
            self.person_starter["Sophie"]["prawn_cocktail"]])
        
        


    def ex_constraint_4(self):
        # Explicit constraint
        # The filet steak main course should be combined with the 
        # onion soup as starter and with the apple crumble for dessert
        
        for person in self.persons:        
            self.model.AddBoolAnd([
                self.person_starter[person]["onion_soup"],
                self.person_desert[person]["apple_crumble"]])\
                .OnlyEnforceIf(self.person_main_course[person]["filet_steak"])
        
    def ex_constraint_5(self):
        #Explicit constraint
        #The person who orders the mushroom tart as starter also orders the red wine
        for person in self.persons:        
            self.model.AddBoolAnd([self.person_starter[person]["mushroom_tart"]])\
                .OnlyEnforceIf(self.person_drink[person]["red_wine"])
            
    def ex_constraint_6(self):
        #Explicit constraint
        #The baked mackerel should not be combined with ice cream for dessert,  
        #vegan pie should not be ordered as main together with prawn cocktail or carpaccio as starter
        for person in self.persons:
            self.model.AddBoolOr([self.person_main_course[person]["baked_mackerel"].Not(),
                                  self.person_desert[person]["ice_cream"].Not()])   
                 
            self.model.AddBoolOr([self.person_main_course[person]["vegan_pie"].Not(),
                                  self.person_starter[person]["prawn_cocktail"].Not()])        
            self.model.AddBoolOr([self.person_main_course[person]["vegan_pie"].Not(),
                                  self.person_starter[person]["carpaccio"].Not()])        


    def ex_constraint_7(self):
        #Explicit constraint
        #The filet steak should be eaten with either beer or coke for drinks
        for person in self.persons:
            self.model.AddBoolOr([self.person_main_course[person]["filet_steak"].Not(),
                                  self.person_drink[person]["beer"],
                                  self.person_drink[person]["coke"]])

    def ex_constraint_8(self):
        
        #Explicit constraint
        #One of the women drinks white wine, while the other prefers red wine for drinks
        self.model.AddBoolOr([self.person_drink["Emily"]["white_wine"],
                              self.person_drink["Emily"]["red_wine"]])
        self.model.AddBoolOr([self.person_drink["Sophie"]["white_wine"],
                              self.person_drink["Sophie"]["red_wine"]])
    
    def ex_constraint_9(self):
        #Explicit constraint
        #One of the men has chocolate cake for dessert, 
        # while the other prefers not to have ice cream 
        #or coke but will accept one of the two if necessary 
        #
        #One of the men has chocolate cake for dessert 
        self.model.AddBoolXOr([self.person_desert["James"]["chocolate_cake"],
                               self.person_desert["Daniel"]["chocolate_cake"]])        
        
        
        #if one men takes chocolate_cake, other perfer not to have ice-cream or coke

        #if Daniel takes chocolate_cake than James wont take ice-cream of coke
        self.model.AddBoolOr([
            self.person_desert["James"]["ice_cream"].Not(),
            self.person_drink["James"]["coke"].Not()])\
                .OnlyEnforceIf(self.person_desert["Daniel"]["chocolate_cake"])
        #if James takes chocolate_cake than Daniel wont take ice-cream of coke
        self.model.AddBoolOr([
            self.person_desert["Daniel"]["ice_cream"].Not(),
            self.person_drink["Daniel"]["coke"].Not()])\
                .OnlyEnforceIf(self.person_desert["James"]["chocolate_cake"])

        # But they accept one if necessary
        # This implicitly means to me modifying last part of the statement 
        # as (while the other prefers to have either ice cream or coke ) 
        # 
        #
        # if James takes chocolate_cake as desert, 
        # James will not have ice cream anyway. so he can take coke
        self.model.AddBoolAnd([self.person_drink["James"]["coke"].Not()])\
            .OnlyEnforceIf(self.person_desert["James"]["chocolate_cake"])
        # if Daniel takes chocolate_cake as desert, 
        # James will not have ice cream anyway. so he can take coke
        self.model.AddBoolAnd([self.person_drink["Daniel"]["coke"].Not()])\
            .OnlyEnforceIf(self.person_desert["Daniel"]["chocolate_cake"])

        


    
    def put_all_constraint(self):
        self.create_decision_variable()
        self.implicit_constraint()
        self.ex_constraint_1()
        self.ex_constraint_2()
        self.ex_constraint_3()
        self.ex_constraint_4()
        self.ex_constraint_5()
        self.ex_constraint_6()
        self.ex_constraint_7()
        self.ex_constraint_8()
        self.ex_constraint_9()
        


class soduku():
    # Goal is to create soduku solution such that 
    # No digit occurs twice in any of the rows, 
    # In any of the columns, or 
    # In any of the 3x3 sub-grids

    def __init__(self,model):

        self.soduku_variables = {}
        self.model = model

    def create_variables(self):
        # Create decision variables
        # Creating nine boolean variable for each digit(1..9)
        # true will indicate the particular number peresent in that cell
        for row in range(9):
            columns = {}
            for col in range(9):
                variables = {}
                for var in range(1,10):
                    #Each cell may have any of the nine value(1..9)
                    variables[var] = \
                        self.model.NewBoolVar(f"Var_[{row}][{col}]_[{var}]")
                columns[col]=variables
            self.soduku_variables[row] = columns

    def create_row_col_constraints(self):
        #one constraint per cell
        for row in range(9):
            for col in range(9):
                variables = []
                for var in range(1,10):
                    variables.append(self.soduku_variables[row][col][var])
                self.model.AddBoolOr(variables)

        #no duplicates in each row
        for row in range(9):
            for col in range(9):
                for next_col in range(col+1,9):
                    for var_cell in range(1,10):
                        self.model.AddBoolOr([
                            self.soduku_variables[row][col][var_cell].Not(),
                            self.soduku_variables[row][next_col][var_cell].Not()])

        #no duplicates in each col
        for col in range(9):
            for row in range(9):
                for next_row in range(row+1,9):
                    for var_cell in range(1,10):
                        self.model.AddBoolOr([
                            self.soduku_variables[row][col][var_cell].Not(),
                            self.soduku_variables[next_row][col][var_cell].Not()])
        
        #Number from 1-9 exist in each row
        for row in range(9):
            for col in range(9):
                variables = []
                for var_cell in range(1,10):
                    variables.append(self.soduku_variables[row][col][var_cell])
                self.model.AddBoolOr(variables)

        #Number from 1-9 exist in each col
        for col in range(9):
            for row in range(9):
                variables = []
                for var_cell in range(1,10):
                    variables.append(self.soduku_variables[row][col][var_cell])
                self.model.AddBoolOr(variables)          

    def constraint_on_each_square(self):
        # no duplicates in each square(3*3)
        # creating suqare indexes
        # key (0,0),(0,3),(0,6),(3,0),(3,3),(3,6),(6,0),(6,3),(6,6)
        # value:(0,0)-->[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        square_indexes = {}
        for i in range(0,9,3):
            for j in range(0,9,3):
                index_in_square = []
                for x in range(i,i+3):
                    for y in range(j,j+3):
                        index_in_square.append((x,y))
                square_indexes[(i,j)]=index_in_square

        # Iterate the suqare indexes to add constraint for each 3*3 squares
        for item in square_indexes:
            indexs = square_indexes[item]
            for seq in range(len(indexs)):
                for next_seq in range(seq+1,len(indexs)):
                    for var_cell in range(1,10):
                        self.model.AddBoolOr([
                            self.soduku_variables[indexs[seq][0]][indexs[seq][1]][var_cell].Not(),
                            self.soduku_variables[indexs[next_seq][0]][indexs[next_seq][1]][var_cell].Not()])
        
        #Number from 1-9 exist in each square(3*3)
        for item in square_indexes:
            indexs = square_indexes[item]
            for seq in range(len(indexs)):
                variables=[]
                for var_cell in range(1,10):
                    variables.append(\
                        self.soduku_variables[indexs[seq][0]][indexs[seq][1]][var_cell])
                self.model.AddBoolOr(variables)                              

    def initial_values(self):
        # Given in assignment
        self.initial_value = numpy.array([[0, 0, 0, 0, 0, 0, 0, 3, 0],
                                [7, 0, 5, 0, 2, 0, 0, 0, 0],
                                [0, 9, 0, 0, 0, 0, 4, 0, 0],
                                [0, 0, 0, 0, 0, 4, 0, 0, 2],
                                [0, 5, 9, 6, 0, 0, 0, 0, 8],
                                [3, 0, 0, 0, 1, 0, 0, 5, 0],
                                [5, 7, 0, 0, 6, 0, 1, 0, 0],
                                [0, 0, 0, 3, 0, 0, 0, 0, 0],
                                [6, 0, 0, 4, 0, 0, 0, 0, 5]])

    def initialise_soduku_cells_with_initial_value(self):

        for row in range(9):
            for col in range(9):
                if self.initial_value[row][col]!=0:
                    self.model.AddBoolAnd([\
                        self.soduku_variables[row][col][self.initial_value[row][col]]])

    def task_A(self):
        self.create_variables()

    def task_B(self):
        self.initial_values()
        self.initialise_soduku_cells_with_initial_value()
    
    def task_C(self):
        self.create_row_col_constraints()
        self.constraint_on_each_square()

    def make_variable_constraint_ready(self):
        # Wrapper functions
        self.task_A()
        self.task_B()
        self.task_C()
        
        





class project_planning():
    def __init__(self,model,file_name) -> None:
        self.solution = 0
        self.xls_file_path = file_name
        self.model = model
        self.project_variables = {}
        self.project_month_job_contractor = {}        
        self.project_job_month = {}
        self.contractor_job_quote = {}
        self.project_value = {}    
       
    
    def load_excel_and_read(self):
        #Read each sheet of excel file and load in dataframe
        projectDF = pd.read_excel(self.xls_file_path,sheet_name="Projects")
        quotesDF = pd.read_excel(self.xls_file_path,sheet_name="Quotes")
        dependencyDF = pd.read_excel(self.xls_file_path,sheet_name="Dependencies")
        valueDF = pd.read_excel(self.xls_file_path,sheet_name="Value")

        # first columns doesnt have any header name
        # put header name as per data
        projectDF.rename(columns={'Unnamed: 0':'Project'}, inplace=True)
        quotesDF.rename(columns={'Unnamed: 0':'contractor'}, inplace=True)
        dependencyDF.rename(columns={'Unnamed: 0':'Project'}, inplace=True)
        valueDF.rename(columns={'Unnamed: 0':'Project'}, inplace=True)

        return projectDF,quotesDF,dependencyDF,valueDF

    def get_names(self):
        # Extract name from data frame and save in list
        # THis becomes handy while iterating over
        self.project_names = list(self.projectDF["Project"])
        self.contractors_names = list(self.quotesDF["contractor"])
        self.jobs_name = list(self.quotesDF.columns)[1:]
        self.month_name = list(self.projectDF.columns)[1:]

    def task_A(self):
        # Read all data from xls file and save in data frame & list
        self.projectDF,\
        self.quotesDF,\
        self.dependencyDF,\
        self.valueDF = self.load_excel_and_read()
        # Get Project,contractor,job & month names
        self.get_names()

    def create_variables(self):
        # VARIABLE CREATION
        # Project variable creation
        # project = [A,B,C..]
        # B>
        # This will answer "Identify and create the decision 
        # variables in a CP-SAT model that you need to decide 
        # what projects to take on  "
        # Create variable names for each project
        
        for project in self.project_names:
            self.project_variables[project] = \
                self.model.NewBoolVar(f"var_{project}")

        # VARIABLE CREATION
        # B> which contractor is working on which project and when
        # Project consists of job which needs to be completed 
        # in particular month by a contractor
        # So all are related with each other 
        # creating variable to relates all four
        # Project-Month-Job-Contractor relation
        # The sequance would be project done over month
        # jobs needs be done by contractors and should
        # finish in given month
        
        for project in self.project_names:
            project_var = {}
            for month in self.month_name:
                month_var = {}
                for job in self.jobs_name:
                    job_var = {}
                    for contractor in self.contractors_names:
                        job_var[contractor] = \
                            self.model.NewBoolVar\
                                (f"var_{project}_{month}_{job}_{contractor}")
                    month_var[job] = job_var
                project_var[month] = month_var
            self.project_month_job_contractor[project] = project_var    

    def create_mapping_lookup(self):
        # lookup table (helper structure) creation
        # Project & Job relations:
        # project(i)= [(M1,J1),(M2,J2)]
        #          
        #for project in project_names:        
        for _, row in self.projectDF.iterrows():  
            project = row["Project"]
            job_month=[]
            for month in self.month_name:            
                if (row[month]==row[month]):
                    job_month.append((month,row[month]))
            self.project_job_month[project] = job_month
        
        # contractor job cost mapping                
        for _, row in self.quotesDF.iterrows():
            contractor = row["contractor"]
            job_value = {}
            for job in self.jobs_name:
                if row[job]==row[job]:
                    job_value[job]=row[job]
            self.contractor_job_quote[contractor]=job_value        
        # 
        # Project Value dict
        #
        # In the Value sheet you will find the value of 
        # each project (e.g. Project A is worth €500).
        #        
        for item in self.valueDF.to_dict("records"):        
            self.project_value[item["Project"]]= item["Value"]
        

    def contractor_constraints(self):
        # only one contractor should be doing one job for given month
        for project in self.project_names:        
            for _,job in self.project_job_month[project]:           
                for month in self.month_name:
                    variables=[]
                    for contractor in self.contractors_names:
                        variables.append(\
                            self.project_month_job_contractor[project]\
                                            [month][job][contractor])
                    self.model.Add(sum(variables) <= 1)\
                        .OnlyEnforceIf(self.project_variables[project])

    def not_all_contractor_can_do_all_job(self):
        # B> not all contractors are qualified to work on all jobs
        #
        # if contractor is not qualified for a job,
        # there wont be any quote for that job by the contractor
        #        
        for contractor in self.contractors_names:
            for job in self.jobs_name:            
                if (0 == self.contractor_job_quote[contractor].get(job,0)):
                    # Reached here means contractor can not do job
                    # Should negate all the combination for this job & contractor
                    variables = []
                    for project in self.project_names:
                        for month in self.month_name:
                            variables.append(
                                self.project_month_job_contractor[project]\
                                            [month][job][contractor].Not())
                    self.model.AddBoolAnd(variables)

    def constraint_B(self):
        # Create all needed variable
        self.create_variables()
        self.create_mapping_lookup()
        self.project_month_contractor()
        self.contractor_constraints()
        self.not_all_contractor_can_do_all_job()        
        

    def constraint_C(self):
        #in any given month, a contractor can do only one job 
        #
        for month in self.month_name:
            for contractor in self.contractors_names:
                #In a month by contractor
                #project-job
                variables=[]                
                for project in self.project_names:
                    for job in self.jobs_name:
                        variables.append(
                            self.project_month_job_contractor[project]\
                                            [month][job][contractor])
                self.model.Add(sum(variables)<=1)

    
    def constraint_D(self):
        
        # project is accepted to be delivered 
        # then exactly one contractor per job of the project needs to work on it
        
        for project in self.project_names:        
            for month,job in self.project_job_month[project]:
                variables = []
                # for a given job, exactly one contractor 
                for contractor in self.contractors_names:
                    variables.append(\
                        self.project_month_job_contractor[project]\
                            [month][job][contractor])
                self.model.Add(sum(variables) == 1)\
                    .OnlyEnforceIf(self.project_variables[project])


    def constraint_E(self):
        #
        #  E>if a project is not taken on then no one 
        #  should be contracted to work on it        

        for project in self.project_names:
            variables=[]
            for month in self.month_name:
                for job in self.jobs_name:
                    for contractor in self.contractors_names:
                        variables.append(\
                            self.project_month_job_contractor[project]
                                              [month][job][contractor])
            self.model.Add(sum(variables)==0)\
                .OnlyEnforceIf(self.project_variables[project].Not())     

    def constraint_F(self):
        #
        # F> implement the project dependency and project conflict constraints 
        # project dependecy
        # 
        for _, row in self.dependencyDF.iterrows():          
            for project in self.project_names:
                if(row[project] == 'required'):                
                    self.model.AddBoolOr(
                        [self.project_variables[row["Project"]].Not(),
                        self.project_variables[project]])
                elif (row[project] == 'conflict'):
                    self.model.AddBoolOr(
                        [self.project_variables[row["Project"]].Not(),
                        self.project_variables[project].Not()]) 


    def constraint_G(self):
        #
        # G>constraint that the profit margin, i.e. the difference 
        # between the value of all delivered projects and the cost of all required 
        # subcontractors, is at least €2160
        #
        # Earning from each projects
        #   
        earning_per_project =[]          
        for project in self.project_names:
            earning_per_project.append(\
                self.project_value[project] * self.project_variables[project])

        # 
        # Expense per project
        #
        
        expense_per_project = []
        for project in self.project_names:
            for month in self.month_name:
                for job in self.jobs_name:
                    for contractor in self.contractors_names:
                        cost = int(self.contractor_job_quote[contractor].get(job,0))
                        expense_per_project.append(\
                            cost*self.project_month_job_contractor[project]\
                                                    [month][job][contractor])
        self.model.Add(sum(earning_per_project) - sum(expense_per_project) >= 2160)   

    def project_month_contractor(self):
        #
        # Relation between project month job contractor
        #         
        for project in self.project_names:
            for month in self.month_name:            
                for contractor in self.contractors_names:
                    for job in self.jobs_name:
                        self.model.AddBoolOr([
                            self.project_month_job_contractor[project]\
                                [month][job][contractor].Not(),
                            self.project_variables[project]
                            ])
                 

    def create_variable_and_constraints(self):
        #Load xls file read all section
        self.task_A()        
        self.constraint_B()
        self.constraint_C()
        self.constraint_D()
        self.constraint_E()
        self.constraint_F()
        self.constraint_G()
        

def problem_1():

    print("\n\n-----------------Question#1 Dinner Puzzel-----------------------\n\n")
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()  
    puzzle_obj = logic_puzzel(model) 
    puzzle_obj.put_all_constraint()
    status = solver.SearchForAllSolutions(
                       model, 
                       logic_puzzel_SolutionPrinter(puzzle_obj))
    print(solver.StatusName(status))   

def problem_2():
    print("\n\n-----------------Question#2 Soduku -----------------------------\n\n")
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()  
    soduku_obj = soduku(model) 
    soduku_obj.make_variable_constraint_ready()
    status = solver.SearchForAllSolutions(
                          model, 
                          soduku_SolutionPrinter(soduku_obj))
    print(solver.StatusName(status))   

def problem_3():
    print("\n\n-----------------Question#3 Project planner---------------------\n\n")
    model = cp_model.CpModel()
    solver = cp_model.CpSolver() 
    project_planner_obj = project_planning(model,"Assignment_DA_1_data.xlsx")
    project_planner_obj.create_variable_and_constraints()
    status = solver.SearchForAllSolutions(
                            model,
                            project_planner_SolutionPrinter(project_planner_obj))
    print(solver.StatusName(status))

def main():
    # call all warpper functions
    problem_1()
    problem_2()
    problem_3()


main()