# Author: Gyanendar Manohar
# Student Id: R00207241


import math
import pandas as pd
from ortools.linear_solver import pywraplp


def task1(excel_path):
    print()
    print()
    print()
    print("TASK->1")
    print()
    # Part A
    # Read each sheet from excel file in panda dataframe
    supplier_stock_df = pd.read_excel(excel_path, sheet_name="Supplier stock")
    rmaterial_cost_df = pd.read_excel(
        excel_path, sheet_name="Raw material costs")
    rmaetrial_shipping_df = pd.read_excel(
        excel_path, sheet_name="Raw material shipping")
    product_req_df = pd.read_excel(
        excel_path, sheet_name="Product requirements")
    prod_capacity_df = pd.read_excel(
        excel_path, sheet_name="Production capacity")
    prod_cost_df = pd.read_excel(excel_path, sheet_name="Production cost")
    cust_demand_df = pd.read_excel(excel_path, sheet_name="Customer demand")
    shipping_cost_df = pd.read_excel(excel_path, sheet_name="Shipping costs")

    # Assign name to first column of each dataframe
    supplier_stock_df.rename(columns={'Unnamed: 0': 'supplier'}, inplace=True)
    rmaterial_cost_df.rename(columns={'Unnamed: 0': 'supplier'}, inplace=True)
    rmaetrial_shipping_df.rename(
        columns={'Unnamed: 0': 'supplier'}, inplace=True)
    product_req_df.rename(columns={'Unnamed: 0': 'product'}, inplace=True)
    prod_capacity_df.rename(columns={'Unnamed: 0': 'product'}, inplace=True)
    prod_cost_df.rename(columns={'Unnamed: 0': 'product'}, inplace=True)
    cust_demand_df.rename(columns={'Unnamed: 0': 'product'}, inplace=True)
    shipping_cost_df.rename(columns={'Unnamed: 0': 'factory'}, inplace=True)

    # fill missing value with zero for each data frame
    supplier_stock_df = supplier_stock_df.fillna(0)
    rmaterial_cost_df = rmaterial_cost_df.fillna(0)
    product_req_df = product_req_df.fillna(0)
    prod_capacity_df = prod_capacity_df.fillna(0)
    prod_cost_df = prod_cost_df.fillna(0)
    cust_demand_df = cust_demand_df.fillna(0)

    # Get Supplier Name
    suppliers = set(supplier_stock_df['supplier'])
    # Get Factory name
    factories = set(shipping_cost_df['factory'])
    # Get Product name
    products = set(product_req_df['product'])
    # Get material name
    rawmaterials = set(rmaterial_cost_df.columns[1:])
    # Get customer name
    customers = set(cust_demand_df.columns[1:])

    # Print all names
    print(suppliers)
    print(factories)
    print(products)
    print(rawmaterials)
    print(customers)
    print()

    # Create solver object
    solver = pywraplp.Solver(
        'LPWrapper', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    objective_cost = solver.Objective()
    objective_cost.SetMinimization()

    # Four sheet talks about cost
    # Four sheet talks about unit
    # Supplier bill -> shipping + material cost
    # production cost
    # delivery cost
    # objectice-> minimise(shipping cost + material cost + production cost + delivery cost)
    # Objective is to minimise cost
    #

    # Part B
    # Flow is Raw Material-> supplier->Factory->product->customer
    # Given data has relation between
    #
    # Material - supplier
    # Factory - supplier
    # Material - product
    # Factory - product
    # product - customer
    # Factory - customer
    #
    # By taking three at a time,total two collection needed for expression relation (creating variables)
    # I am creating two collection to express relation between them
    # (Raw Material,supplier,Factory) & (Factory,Product,customer)

    # Factory->product->customer

    # Decision variable for factory_customer_product
    fact_cust_prod_unit = {}
    # For each factory,product,customer combination, create variable
    for factory_v1 in factories:
        for product_v1 in products:
            for customer_v1 in customers:
                # for variable
                # Lower bound->0
                # upper bound can be anything
                fact_cust_prod_unit[(factory_v1, customer_v1, product_v1)] = \
                    solver.NumVar(0, solver.infinity(),
                                  f"{factory_v1}_{customer_v1}_{product_v1}")

    # Supplier->factor->material
    # Decision variable for supplier_factory_material combination
    sup_fact_mat_unit = {}
    for supplier_v2 in suppliers:
        for factory_v2 in factories:
            for material_v2 in rawmaterials:
                # for variable
                # Lower bound->0
                # upper bound can be anything
                sup_fact_mat_unit[(supplier_v2, factory_v2, material_v2)] = \
                   solver.NumVar(0, 
                   solver.infinity(), f"{supplier_v2}_{factory_v2}_{material_v2}")

    

    # supplier stock
    # Sheet1
    #
    # Part E
    # Supplier can not supply more than what it has in stock
    for supplier_s1 in suppliers:
        for material_s1 in rawmaterials:
            # Get Supplier stock
            supplier_stock = \
                supplier_stock_df[supplier_stock_df['supplier'] == \
                                supplier_s1][material_s1].tolist()[0]
            # Upper bound is stock limit
            supplier_stock_constraint = solver.Constraint(0, supplier_stock)
            # Set coffecicient
            for factory_s1 in factories:
                supplier_stock_constraint.SetCoefficient(
                    sup_fact_mat_unit[(supplier_s1, factory_s1, material_s1)], 1.0)

    # Sheet5
    #
    # Part G:
    # Each product each factory able to manufacture
    # Such that manufacturing capacity shouldn't exceed
    for factory_s5 in factories:
        for product_s5 in products:
            # Get factory manufacturing capacity 
            prod_capacity = \
                prod_capacity_df[prod_capacity_df['product'] == \
                product_s5][factory_s5].to_list()[0]
            # Max factory can produce is its predefined manufacturing capacity
            # So Constraint Max value-> capacity,Min->0
            production_capacity_constraint = solver.Constraint(0, prod_capacity)
            #Set coeff for each customer
            for customer_s5 in customers:
                production_capacity_constraint.SetCoefficient(
                    fact_cust_prod_unit[(factory_s5, customer_s5, product_s5)], 1.0)

    
    # Part C
    # Part D
    # Part F
    # Sheet4
    # Product RAW Material Requirements
    # Raw Material required to manufacture a unit of product
    # Factory consumes raw materials which supplied by suppliers and produces products
    # thats shipped to customer
    # Here factory is main intersection point to join this chain
    #
    # product produced by factory should be atlast equal to customer demand
    # and can be of any value greater than demand
    # but wont cross the maximum production capacity(of factory)
    #
    for factory_s4 in factories:
        for raw_mat_s4 in rawmaterials:
            # Factory production adds to its inventory
            # Serving customer order takes product out of inventory
            # At end, the net count for factory should be minimum zero
            # which will ensure customer demand is met
            # and enough raw material ordered to meet the demand
            # The equation would be like x>=y where x is production and y is demand
            factory_inout_constraint = solver.Constraint(0, solver.infinity())
            #Part F
            #sufficient Rawmat to manufactor all item
            for supplier_s4 in suppliers:
                factory_inout_constraint.SetCoefficient(
                    sup_fact_mat_unit[(supplier_s4, factory_s4, raw_mat_s4)], 1.0)
            # Part D
            # sufficent production to meet customer demand
            for customer_s4 in customers:
                for product_s4 in products:
                    factory_inout_constraint.SetCoefficient(\
                        fact_cust_prod_unit[(factory_s4, customer_s4, product_s4)], 
                    float(-1.0*product_req_df[product_req_df['product'] ==\
                         product_s4][raw_mat_s4].to_list()[0]))
    
    # Sheet7
    #    
    #
    # Factory should produce enough to meet the customer demand
    # So minimum value should be customer demand
    for product_s7 in products:
        for customer_s7 in customers:
            cust_demand = \
                cust_demand_df[cust_demand_df['product'] == \
                                 product_s7][customer_s7].to_list()[0]
            # Min-> customer demand
            # Max-> can be anything above it
            customer_demand_factory_output_constraint = \
                solver.Constraint(
                cust_demand, solver.infinity())
            # Set the coefficient    
            for factory_s7 in factories:
                customer_demand_factory_output_constraint.SetCoefficient(
                    fact_cust_prod_unit[(factory_s7, customer_s7, product_s7)], 1.0)


    # Set objective
    #
    # Part H
    # Objective is to minimise cost
    # Supplier bill -> shipping + material cost
    # production cost
    # delivery cost
    # objectice-> minimise(shipping cost + material cost + production cost + delivery cost)

    #
    # Sheet8
    # factory customer shipping cost
    # Sheet6
    # Production cost
    # cost of manufactring one product in each factory
    for factory in factories:
        for customer in customers:
            for product in products:  
                #totalcost -> production cost + product shipping charge (to customer)             
                objective_cost.SetCoefficient(fact_cust_prod_unit[(factory, customer, product)], \
                float(shipping_cost_df[shipping_cost_df['factory'] == factory][customer].to_list()[0]+\
                    prod_cost_df[prod_cost_df['product'] == product][factory].to_list()[0]))

    # Sheet2
    # Row Material cost
    # Supplier charging for each unit raw materials
    # Sheet3
    # RawMaterial shipping cost
    # Shipping cost per unit of raw material to each factory
    for factory in factories:
        for supplier in suppliers:
            for raw_mat in rawmaterials:
                #total cost for factory,supplier,raw Material-> raw mat cost + raw mat shipping charge
                objective_cost.SetCoefficient(sup_fact_mat_unit[(supplier, factory, raw_mat)], \
                    float(rmaterial_cost_df[rmaterial_cost_df['supplier'] == supplier][raw_mat].to_list()[0]+\
                        rmaetrial_shipping_df[rmaetrial_shipping_df['supplier'] == supplier][factory].to_list()[0]))

    # Part I:Solve and determine overall optimal cost
    solver.Solve()
    print("==================================================")
    print(f"I.Optimal cost:{objective_cost.Value()}")
    print("==================================================")


    # part J:
    # For each factory aterial has to be ordered from each individual supplier
    #
    print("J.For each factory, Material ordered from each supplier")
    print("==================================================")
    # SOlution Value of sup_fact_mat_unit would give the required value
    for factory in factories:
        print()
        print(factory)
        print()
        for supplier in suppliers:
            for raw_mat in rawmaterials:
                # For each factory,supplier,raw mat combination, if solutionValue>0
                # Supplier has supplied the raw mat to the factory
                if sup_fact_mat_unit[(supplier, factory, raw_mat)].SolutionValue() > 0:
                    print(f"{supplier}->{raw_mat}->\
                        {round(sup_fact_mat_unit[(supplier,factory,raw_mat)].SolutionValue(),2)}")

    # part K:
    #
    # Each factory supplier bill (material cost + delivery charges)
    print()
    print("K.Supplier bill for each factory:")
    print("==================================================")
    for factory in factories:
        print()
        print(factory)
        print()
        # across suppliers calulate the cost
        for supplier in suppliers:
            bill = 0.0
            for raw_mat in rawmaterials:
                material_qty = sup_fact_mat_unit[(
                    supplier, factory, raw_mat)].SolutionValue()
                # if supplied material qty is greater than zero, calculate the bill
                # as (raw mat cost+ shipping cost)* qty
                if material_qty > 0:
                    bill = bill + \
                        material_qty*(rmaterial_cost_df[rmaterial_cost_df['supplier'] == supplier][raw_mat].to_list()[0]\
                            +rmaetrial_shipping_df[rmaetrial_shipping_df['supplier'] == supplier][factory].to_list()[0])
            print(f"{supplier}->{round(bill,2)}")

    # part L
    #
    # Each factory, Unit of each product being manufactured
    # Total Manufacturing cost for individual factory
    print()
    print("L.Unit of product manufactured and production cost for each factory:")
    print("==================================================")
    for factory in factories:
        print()
        print(factory)
        print()
        # Total manufactring cost per factory
        total_manufacturing_cost = 0
        for product in products:
            # Get Sum of Unit of each product manufactured by factory
            # for each customer
            prod_qty = 0.0
            for customer in customers:
                prod_qty = prod_qty + \
                    fact_cust_prod_unit[(
                        factory, customer, product)].SolutionValue()
            #production cost woud be product quantity*production cost for the product
            total_manufacturing_cost = total_manufacturing_cost + prod_qty * \
                prod_cost_df[prod_cost_df['product'] == product][factory].to_list()[0]

            print(f"{product}->{round(prod_qty,2)}")

        print()
        print(f"Production Cost:{round(total_manufacturing_cost,2)}")

    print()

    # Part M
    # Unit of product shipped from each factory for each customer:
    # Total Shipping cost per customer
    print("M.Unit of product shipped from each Factory for customer and total shipping cost:")
    print("==================================================")
    for customer in customers:
        print()
        print(customer)
        print()
        # Total shipping cost per customer
        shipping_cost_per_customer = 0.0
        for factory in factories:
            print(f"->{factory}")
            for product in products:
                # Get the product quantity shipped to customer from factory
                product_qty = fact_cust_prod_unit[(
                    factory, customer, product)].SolutionValue()
                if(product_qty > 0.0):
                    print(f"-->{product}->{round(product_qty,2)}")
                    #Add shipping cost for all product 
                    shipping_cost_per_customer = shipping_cost_per_customer + \
                        shipping_cost_df[shipping_cost_df['factory'] == factory][customer].to_list()[
                            0]
        print()
        print("Total Shipping Cost:", shipping_cost_per_customer)

    # Part N
    #
    # For each customer
    # Fraction of each raw material each factory has ordered
    print()
    print("N.Fraction of raw material factory has ordered for each customer")
    print("==================================================")
    print()
    # needs raw material need for customer order 
    # devided by total raw material ordered by factory devided
    # For factory_customer_raw material combination
    for factory in factories:
        print()
        print(factory)
        for customer in customers:
            print()
            print(customer)
            for raw_mat in rawmaterials:
                # Get Raw material ordered by factory from all supplier
                # This will give total raw material
                factory_raw_materials = 0.0
                for supplier in suppliers:
                    factory_raw_materials = factory_raw_materials + \
                        sup_fact_mat_unit[(
                            supplier, factory, raw_mat)].SolutionValue()

                # Now Get Raw material needed for producing the all customer order 
                raw_mat_needed_for_cust = 0.0
                for product in products:
                    # summation of 
                    # raw material needed for producing product * product delivered by factory to
                    # the customer
                    raw_mat_needed_for_cust = \
                        raw_mat_needed_for_cust+product_req_df[product_req_df['product'] == \
                            product][raw_mat].to_list()[0] * \
                            fact_cust_prod_unit[(factory, customer, product)].SolutionValue()

                print(f"{raw_mat}->{round(raw_mat_needed_for_cust/factory_raw_materials,2)}")

    # Part N
    # overall unit cost for each product
    print()
    print("N.Overall Unit cost for each product per customer:")
    print("==================================================")
    for customer in customers:
        print()
        print(f"{customer}:")
        for product in products:
            # Need to find out total cost incurred by factory for producing 
            # product and total quantity of product produced
            # Dividing them would give unit product cost
            total_product_cost = 0.0
            total_product_qty = 0

            for factory in factories:

                # Cost for factory per product unit would be
                # manufactring cost + shipping cost + cost incurred in procuring raw material
                qty_of_product_ordered_by_customer = fact_cust_prod_unit[(
                    factory, customer, product)].SolutionValue()
                #shipping cost    
                shipping_cost_of_prod_to_customer = \
                    shipping_cost_df[shipping_cost_df['factory'] == factory][customer].to_list()[0]
                
                # Calculate Manufacturing cost for factory
                manufactring_cost_for_factory = 0.0
                for raw_mat in rawmaterials:
                    # Get Raw material quantity and its cost
                    raw_mat_qty_for_product = \
                        product_req_df[product_req_df['product'] == product][raw_mat].to_list()[0]
                    
                    material_cost_for_factory = 0.0

                    # Raw materail is sourced from different suppliers
                    # Need to accuumate the cost across suppliers
                    raw_material_cost = 0.0
                    raw_mat_qty_total = 0
                    for supplier in suppliers:
                        # Raw material price + shipping price * quantity
                        raw_mat_qty = \
                            sup_fact_mat_unit[(supplier, factory, raw_mat)].SolutionValue()

                        raw_mat_qty_total = raw_mat_qty_total + raw_mat_qty
                        #Get Raw material price
                        raw_mat_price = \
                            rmaterial_cost_df[rmaterial_cost_df['supplier'] == \
                                supplier][raw_mat].to_list()[0]
                        
                        # Get raw materail shipping price 
                        raw_mat_shipping_price = \
                            rmaetrial_shipping_df[rmaetrial_shipping_df['supplier'] == \
                                supplier][factory].to_list()[0]

                        # Raw material cost for factory would be raw mat price + shipping charges times
                        # raw maetrial quantity
                        raw_material_cost = raw_material_cost + \
                            (raw_mat_price + raw_mat_shipping_price)*raw_mat_qty

                    # If raw material quantity sourced is zero, 
                    # materail cost for factory should be kept at zero
                    if raw_mat_qty_total > 0:
                        material_cost_for_factory = raw_material_cost/raw_mat_qty_total

                    manufactring_cost_for_factory = manufactring_cost_for_factory + \
                        raw_mat_qty_for_product*material_cost_for_factory

                # Add production cost
                manufactring_cost_for_factory = manufactring_cost_for_factory + \
                    prod_cost_df[prod_cost_df['product'] == product][factory].to_list()[0]
                
                #total production cost would be sum of qtantity of product ordered by customer*
                # summation of shipping and production cost
                total_product_cost = total_product_cost + qty_of_product_ordered_by_customer * \
                    (shipping_cost_of_prod_to_customer +
                     manufactring_cost_for_factory)

                #Keep track of total product ordered by customer
                total_product_qty = total_product_qty + qty_of_product_ordered_by_customer

            # If factory has not produced particular product, its quantity would be zero
            # No Need to display that
            if total_product_qty > 0:
                print(
                    f"{product} -> {round(total_product_cost/total_product_qty,2)}")


def task2(excel_path,starting_city):
    print()
    print()
    print()
    print("TASK->2")
    print()
    # Load xls file and get all distance in dataframe
    city_distance_df = pd.read_excel(excel_path, sheet_name="Distances")
    # Renamed the first column which contains city name
    city_distance_df.rename(columns={'Unnamed: 0': 'city'}, inplace=True)
    # Get all city names
    city_names = [str(name) for name in city_distance_df['city']]

    #print(city_names)
    # Cities that driver must visit
    # Given with assignment
    must_visit_city = ['Dublin', 'Limerick',
                       'Waterford', 'Galway',
                       'Wexford', 'Belfast',
                       'Athlone', 'Rosslare',
                       'Wicklow']
    
    solver = pywraplp.Solver(
        'LPWrapper', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    
    # Part A
    #
    # Create decision variable
    # For each pair of towns that need to be visited 
    tour_legs = {}
    #select each pair of city(all combination)
    for city_1 in city_names:
        for city_2 in city_names:
            # There wont be any leg between same city
            if city_1!=city_2:
                # city can be visited zero or one time( value bound of variable)
                tour_legs[(city_1, city_2)] = \
                    solver.IntVar(0, 1, f"{city_1}->{city_2}")

    # Part B
    # Ensure that the delivery driver arrives in
    # each of the towns that need to be visited 
    # all city in must visit should be visited
    for city in must_visit_city:
        # As driver can visit town in any order,create constraint 
        # for both combination
        city_city_1_constraint = solver.Constraint(1, solver.infinity())
        city_1_city_constraint = solver.Constraint(1, solver.infinity())

        for city_1 in city_names:
            # ensure city are not same
            # As there wont be any leg with one city
            if city_1 != city:
                city_city_1_constraint.SetCoefficient(tour_legs[(city, city_1)], 1)
                city_1_city_constraint.SetCoefficient(tour_legs[(city_1, city)], 1)

    # Part C
    # driver departs each of the towns that need to be visited
    # All entered town should have exit aswel
    for city_1 in city_names:
        # Enter ->1
        # Exit ->-1
        # its like x-y = 0
        # Lower,uppper bound for entry/exit ->0
        entry_exit_constraint = solver.Constraint(0, 0)
        for city_2 in city_names:
            if city_1!=city_2:
                #Coefficient for entry
                entry_exit_constraint.SetCoefficient(
                    tour_legs[(city_2, city_1)], 1)
                #Coefficient for exit
                entry_exit_constraint.SetCoefficient(
                    tour_legs[(city_1, city_2)], -1)

    # Part D
    # No disconnected Self contained circle
    # There are two ways to do this
    # 1. If there are n city ,enforce to select n-1 legs and to do this
    # requires lots of constraints 
    # 2.  Define variable (say var) for order of city visited such that 
    # if var(i) = k, city i is at kth postion in tour
    # And enforce that there is no link from kth city to (1,k-1)th city
    #
    #Define variable for sequance of city visited
    city_visit_sequance = {}
    for city in city_names:
        #lower bound ->1
        #upper bound -> total number of city driver can visit
        city_visit_sequance[city] = solver.IntVar(1, len(city_names), f"[{city}]")

    # Its standard problem in graph 
    # to avoid isolated circle the constraint needs to be inforced is of form
    # pi-pj+<=(n-1)(1-xij) where pi,pj are i & jth node in tour, n is total node
    
    for city_1 in city_names:
        for city_2 in city_names:
    #        
            if city_1 != starting_city and city_2 != starting_city:
                if city_1!=city_2:
                    # For all intermediate city of tour the constarint would be 
                    # 2-n<= -pi+pj + (1-n)xij
                    city_visit_constraint = solver.Constraint(2 - len(city_names), solver.infinity())
                    # Set coeff as per the above equation
                    city_visit_constraint.SetCoefficient(city_visit_sequance[city_1], 1)
                    city_visit_constraint.SetCoefficient(city_visit_sequance[city_2], -1)
                    city_visit_constraint.SetCoefficient(tour_legs[(city_1, city_2)], 1-len(city_names))                
            else:
                # Starting city 
                # Position in route ->1
                first_city_constraint = solver.Constraint(1, 1)
                first_city_constraint.SetCoefficient(
                    city_visit_sequance[starting_city], 1)


    # Part E
    # objective function to minimise the overall distance
    # Objective: Minimise overall distance travelled
    objective_route = solver.Objective()
    objective_route.SetMinimization()
    # Get all legs combination and their distance for tour minimisation
    for city_1 in city_names:
        for city_2 in city_names:
            if city_1!=city_2:
                #Set coefficient
                objective_route.SetCoefficient(tour_legs[(city_1, city_2)], \
                    city_distance_df[city_distance_df['city'] == city_1][city_2].tolist()[0])

    # Part F
    # Solve the linear program and determine the overall distance 
    # that needs to be travelled to visit all towns
    solver.Solve()
    print(f"F. Distance needs to travelled :{objective_route.Value()}")

    # Part F
    # Print route
    # Get final route dictionary
    # key is current city
    # value is next city
    final_route = {}
    # Fill the dictionary
    for city_1 in city_names:
        for city_2 in city_names:
            # Valid leg
            if city_1!=city_2:
                if tour_legs[(city_1, city_2)].SolutionValue() == 1:
                    # Add key value pair
                    final_route[city_1] = city_2

    current_city = starting_city
    # traverse the dict key->value->value-> .. unitl reach to starting city
    while final_route[current_city] != starting_city:
        print(f"{current_city}->{final_route[current_city]}")
        current_city = final_route[current_city]
    # need to print the final leg
    print(f"{current_city}->{final_route[current_city]}")


def task3(excel_path):
    print()
    print()
    print()
    print("TASK->3")
    print()
    # Part A
    # Load xls file and get all details in dataframe
    stops_df = pd.read_excel(excel_path, sheet_name="Stops")
    distances_df = pd.read_excel(excel_path, sheet_name="Distances")
    passangers_df = pd.read_excel(excel_path, sheet_name="Passengers")
    trains_df = pd.read_excel(excel_path, sheet_name="Trains")

    # Renamed the first column which contains station/line name
    stops_df.rename(columns={'Unnamed: 0': 'station'}, inplace=True)
    distances_df.rename(columns={'Unnamed: 0': 'station'}, inplace=True)
    passangers_df.rename(columns={'Unnamed: 0': 'station'}, inplace=True)
    trains_df.rename(columns={'Unnamed: 0': 'line'}, inplace=True)

    passangers_df = passangers_df.fillna(0)

    #Get All station names
    station_names = [str(name) for name in stops_df['station']]
    #['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
    #Get All line names
    line_names = [str(name) for name in trains_df['line']]
    #['L1', 'L2', 'L3', 'L4']

    # Part B   
    # For each pair of train stations determine the amount of time required to travel
    # Get Shortes path between pair of stations
    shortest_path = []
    
    # Get Pair of stations
    station_name_pair = []
    for leg_1 in station_names:
        for leg_2 in station_names:
            if leg_1!=leg_2: #(station (A,A) is not valid pair)
                station_name_pair.append((leg_1,leg_2))

    # Get all station of line sorted as per their occurance
    # is it circular
    # total distance in one direction
    line_station_pair = {}  #[line] = [stations],distance(time),iscircular
    for train_line in line_names:       
       station_order_pair = []
       for station in station_names:
           # if NaN is returned for line,station combination means that station
           # doesnt belongs to the line and should be ignored
           if(not math.isnan(stops_df[stops_df['station']==station][train_line].tolist()[0])):
               # Store number and station name
               station_order_pair.append((stops_df[stops_df['station']==station][train_line].tolist()[0],station))
       #Sort the ltuple list , the and get station in sorted order as per their position in line
       station_order_pair = sorted(station_order_pair)  
       #for station name list as per their occurance
       sorted_station = [name for _,name in station_order_pair]
       # Get Length/time taken to cover the line
       line_length = 0
       for index in range(len(sorted_station)-1):
           line_length = line_length+ distances_df[distances_df['station']==sorted_station[index]][sorted_station[index+1]].tolist()[0]
       #if distance between two end station of line is not defined, means line is not circular
       is_circular = False if math.isnan(distances_df[distances_df['station']==sorted_station[0]][sorted_station[-1]].tolist()[0])else True
       if is_circular == True:
           #if line is circular, consider distance between last and 1st station as well for total length
           line_length = line_length+ distances_df[distances_df['station']==sorted_station[-1]][sorted_station[0]].tolist()[0]
       # Save
       line_station_pair[train_line] = (sorted_station,line_length,is_circular)

    # form lookup for train-pair and train line
    station_leg_pair_line_lookup = {}
    for train_line in line_names:
        # Keep seperate list of forward and back ward legs pair
        # This will give all combination of train
        forward_station_list = line_station_pair[train_line][0]
        #backward
        return_station_list = forward_station_list[::-1]
        is_circular = line_station_pair[train_line][2]
        #fill the station pair and line in dict
        for index in range(len(forward_station_list)-1):
            #train station pair is key and line as value
            station_leg_pair_line_lookup[(forward_station_list[index],forward_station_list[index+1])] = train_line
            station_leg_pair_line_lookup[(return_station_list[index],return_station_list[index+1])] = train_line
            #for circular line add last and 1st station as new leg
            if is_circular == True:
                station_leg_pair_line_lookup[(forward_station_list[-1],forward_station_list[0])] = train_line
                station_leg_pair_line_lookup[(return_station_list[-1],return_station_list[0])] = train_line

    #Iterate through the station name pair list and 
    # get the shortest path and shortes distance between them

    for source_station,destination_station in station_name_pair:
       
        # Here each iteration is new problem with different source and distination
        # So have get new solver each time
        solver = pywraplp.Solver('LPWrapper',pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
   
        # Create decision variable for pair of stations
        # create a decision variable to 
        # decide if this leg should be included into the route
        # For each two stations connected
        station_pairs = {}
        for stop_1 in station_names:
            for stop_2 in station_names:
                #Leg not included->0
                #Leg included->1
                station_pairs[(stop_1,stop_2)] = solver.IntVar(0, 1, f"[{stop_1}->{stop_2}]")

        
        # source
        # train station where the journey originated is included in the path
        source_conncted_constraint = solver.Constraint(1, solver.infinity())
        for stop_1 in station_names:
            if stop_1 != source_station:                
                source_conncted_constraint.SetCoefficient(station_pairs[(source_station,stop_1)], 1)
        
        # destination
        # the destination train station is included in the path 
        # Lower bound ->1 (minimum one connection)
        destination_conncted_constraint = solver.Constraint(1, solver.infinity())
        for stop_1 in station_names:
            if stop_1 != destination_station:                
                destination_conncted_constraint.SetCoefficient(station_pairs[(stop_1,destination_station)], 1)

        # Path should be on one direction only
        # There shouldn't be path where legs are repeating(forward & reverse)
        for stop_1 in station_names:
            for stop_2 in station_names:
                if stop_1!=stop_2:
                    directional_constraint = solver.Constraint(0, 1)
                    #Either one of them should exist
                    directional_constraint.SetCoefficient(station_pairs[(stop_1,stop_2)],1)
                    directional_constraint.SetCoefficient(station_pairs[(stop_2,stop_1)],1)                
        
        # No dead end in path
        # all station will have next & previous station except source and destination
        # so there wont be dead path
        for stop_1 in station_names:
            if stop_1!= source_station and stop_1!=destination_station:                
                two_way_route_constraint = solver.Constraint(0, 0)
                for stop_2 in station_names:
                    if stop_1!=stop_2:
                        two_way_route_constraint.SetCoefficient(station_pairs[(stop_1,stop_2)], 1)
                        two_way_route_constraint.SetCoefficient(station_pairs[(stop_2,stop_1)], -1)

        # its minimisation problem
        # Set objective 
        time_objective = solver.Objective()
        time_objective.SetMinimization()
        # Set objective
        for stop_1 in station_names:
            for stop_2 in station_names:
                # Get distance(time) between two station from distance sheet
                # if distance is not defined, take it large number(say 1000)
                distance = distances_df[distances_df['station']==stop_1][stop_2].tolist()[0]
                if math.isnan(distance):
                    distance = 1000
                # Set the coefficient
                time_objective.SetCoefficient(station_pairs[(stop_1,stop_2)], int(distance))

        #Solve
        solver.Solve()
        #Shortest path taken
        #Save in list
        path = []
        current_station = source_station
        path.append(current_station)
        # Start with current station and travel until current station becomes
        #destination station
        while current_station!=destination_station:
            for next_station in station_names:
                # If leg exist from the current station, add that as next station
                # and come out of the loop
                if station_pairs[(current_station,next_station)].SolutionValue() == 1:
                    path.append(next_station)
                    current_station = next_station
                    break
               
        shortest_path.append((source_station,destination_station,time_objective.Value(),path))

    #Print the source,destination,
    #travel time, path used
    #and train lines for each pair of station
    for item in shortest_path:
        path = item[3]
        # Get train line for each leg
        train_lines = []
        for index in range(len(path)-1):            
            train_lines.append(station_leg_pair_line_lookup[(path[index],path[index+1])])
        # Print source, destination, travel time, optimal route and lines to which each leg of 
        # route belongs to
        print(f"{item[0]}-->{item[1]}:Travel Time:{item[2]} Travel Route:{path}: Train Line:{train_lines}")

    # Part C
    # 
    # 

    #create solver object
    #Set objective     
    solver = pywraplp.Solver('LPWrapper',pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)


    # a. create decision variable to determine 
    # number of train required to meet the passanger demand
    #
    # for simplification
    # take forward and backward journey seperately 
    # create decision variables for total train on 
    # forward & backward journey seperately
    train_on_forward_journey = {}
    train_on_return_journey = {}
    # Train is for per line
    for train_line in line_names:
        #Forward
        train_on_forward_journey[train_line] = \
            solver.IntVar(0, solver.infinity(), f"fw>>[{train_line}]>>")
        #Backward
        train_on_return_journey[train_line] = \
            solver.IntVar(0, solver.infinity(), f"bw<<[{train_line}]<<")

    # Train frequency is per hour
    # Need decision variable to account this as wel
    # Train required per hour
    hourly_train_count_forward_journey = {}
    hourly_train_count_return_journey = {}
    for train_line in line_names:
        hourly_train_count_forward_journey[train_line] = \
            solver.IntVar(0, solver.infinity(), f"fw_hr>>[{train_line}]>>")
        hourly_train_count_return_journey[train_line] = \
            solver.IntVar(0, solver.infinity(), f"bw_hr<<[{train_line}]<<") 
    ########################################################################
    # passenger load on forward and backward journey
    # Need to create map for passenger load  requirement 
    # for each station combination in line basis    
    forward_journey_pass_load = {}
    #passanger load on return journey per line
    return_journey_pass_load = {}
    for train_line in line_names:
        # Create dict for each station combination of station for that line
        forward_journey_pass_load[train_line] = \
            {(stop_1,stop_2):0 for stop_1 in station_names for stop_2 in station_names} 

        return_journey_pass_load[train_line] = \
            {(stop_1,stop_2):0 for stop_1 in station_names for stop_2 in station_names} 
    
    # Passagner capacity for train on each lines -> 
    # All train for the line will have same passanger capacity
    for train_line in line_names:
        # Get capacity for the line
        line_passenger_capacity = trains_df[trains_df['line']==train_line]['Capacity'].tolist()[0]
        # Get All train list for the line and information about circular/non-circular
        fw_station_list,_,is_circular = line_station_pair[train_line]
        # Reverse station order
        rev_station_list = fw_station_list[::-1]
        # Fill the forward & return passanger load
        #all train for the line will have same CAPACITY
        for index in range(len(fw_station_list)-1):
                # The passanger load woul be the line capacity
                forward_journey_pass_load[train_line]\
                    [(fw_station_list[index],fw_station_list[index+1])] = line_passenger_capacity
                return_journey_pass_load[train_line]\
                    [(rev_station_list[index],rev_station_list[index+1])] = line_passenger_capacity
        
        # for circular line, a leg need from last station to first station 
        # of the route which will make path complete circle
        if is_circular == True:
            # The passanger load woul be the line capacity
            forward_journey_pass_load[train_line]\
                [(fw_station_list[-1],fw_station_list[0])] = line_passenger_capacity
            return_journey_pass_load[train_line]\
                [(rev_station_list[-1],rev_station_list[0])] = line_passenger_capacity  
    
    # Passenger Load from shortest path
    # Passanger use shortest route for travelling 
    # All possible pair of station, the number of passanger 
    # may travel between them
    shortest_path_passenger_load = {}
    for stop_1 in station_names:        
        for stop_2 in station_names:     
                #initial value->0 
            shortest_path_passenger_load[(stop_1,stop_2)] = 0
    
    #Passanger travel is taken hourly basis
    for item in shortest_path:     
        # item[0] is source
        # item[1] is destination   
        # item[3] has optimised path used for travelling
        # Get the passanger count value from passanger sheet( which is hourly load)
        # and add it to shortest_path_passenger_load(source,destination)
        for index in range(len(item[3])-1):            
            shortest_path_passenger_load[(item[3][index],item[3][index+1])]+= \
                int(passangers_df[passangers_df['station']==item[0]][item[1]].tolist()[0]) 
    # Above passanger load is hourly requirement
    # use this for creating constraint on hourly conditional variable
    for stop_1 in station_names:        
        for stop_2 in station_names: 
            # create constraint for hourly passanger load 
            # lower bound would be value from passanger sheet( for optimised path)
            hourly_passenger_load_constraint = \
                solver.Constraint(int(shortest_path_passenger_load[(stop_1,stop_2)]), solver.infinity())
            # for each line
            # coefficient need to be set for hourly train count variable
            for train_line in line_names:
                # for forward & return journey
                hourly_passenger_load_constraint\
                    .SetCoefficient(hourly_train_count_forward_journey[train_line],\
                         int(forward_journey_pass_load[train_line][(stop_1,stop_2)]))
                hourly_passenger_load_constraint\
                    .SetCoefficient(hourly_train_count_return_journey[train_line],\
                         int(return_journey_pass_load[train_line][(stop_1,stop_2)]))

    # For circular line, minimum 2 train would be running
    # For non-circular line, same train go forward and returns
    # hence total train count for forward journey and return
    # Journey should be same
   
    
    # freqency of train is hourly
    # here the ask is to get total number of train requirement
    # which would be total time taken by train to complete its journey
    # times frequency
    # Apply this on forward & backward jounery conditional variable
    for train_line in line_names:
        # Get total journey time for each line
        #forward journey time
        time = line_station_pair[train_line][1]
        # if line is not circular, the journey time would be double 
        # of forward journey time value
        time = time + (time if line_station_pair[train_line][2] is False else 0)
        # this is in minute. convert it to hour
        time = time/60
        # for forward journey
        forward_journey_constraint = solver.Constraint(0, solver.infinity())            
        forward_journey_constraint.SetCoefficient(train_on_forward_journey[train_line], 1)
        forward_journey_constraint.SetCoefficient(hourly_train_count_forward_journey[train_line], -time)
        # for backward journey
        return_journey_constraint = solver.Constraint(0, solver.infinity())        
        return_journey_constraint.SetCoefficient(train_on_return_journey[train_line], 1)
        return_journey_constraint.SetCoefficient(hourly_train_count_return_journey[train_line], -time)

    
    #########################################################################


    # c. Objective
    # minimise the number of trains operated on the network 
    train_count_objective = solver.Objective()
    # for minimisation task
    train_count_objective.SetMinimization()
    # Set objective
    #
    for train_line in line_names:
        # train on non-circular line 
        # always going back and forth between the terminal stations
        train_count_objective\
            .SetCoefficient(train_on_forward_journey[train_line], 1)
        
        # for circular line: 
        # one in clockwise direction the other in anti-clockwise direction.
        # so minimum 2 train required at any point of time
        # take return journey train count also
        if line_station_pair[train_line][2]== True:
            train_count_objective\
                .SetCoefficient(train_on_return_journey[train_line], 1)

    # d. 
    solver.Solve()
    print()
    print(f"Total train required:{train_count_objective.Value()}")
    #Train required per line
    for train_line in line_names:
        if line_station_pair[train_line][2]!= True:
            print(f"{train_line}:{train_on_forward_journey[train_line].SolutionValue()}")
        # For circular line, take return_journey value aswel
        if line_station_pair[train_line][2]== True:
            print(f"{train_line}:\
                {train_on_forward_journey[train_line].SolutionValue()},\
                    {train_on_return_journey[train_line].SolutionValue()}")

def main():    
    task1('Assignment_DA_2_Task_1_data.xlsx')
    task2('Assignment_DA_2_Task_2_data.xlsx','Cork')
    task3('Assignment_DA_2_Task_3_data.xlsx')


main()
