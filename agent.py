def RosteringAgent():

    from agents import Thing, Agent
    import numpy as np
    import pandas as pd
    from pyomo.opt import SolverFactory
    from pyomo.environ import  AbstractModel, Binary, RangeSet, Set, Var, Param, Objective, Constraint, NonNegativeReals 
    from pyomo.environ import NonNegativeIntegers, PercentFraction, Boolean, minimize, SolverFactory, value 
    infinity = float('inf')
    from itertools import product
    
    def program(percept):         
        
        def iterate_dict_unit(mylist, parents=[]):
            r = []

            for d in mylist:
                for key,value in d.items():
                    if key == 'targetPlanningPerUnit':
                        for b in value:
                            for k, v in b.items():
                                if k == 'unit':
                                      r.append(v)

            return set(r)
        def iterate_dict_hour(mylist, parents=[]):
            """
            This function iterates over one dict and returns a list of tuples: (key, value, parent_keys)
            Usefull for looping through a multidimensional dictionary.
            """
            r = []

            for d in mylist:
                for key,value in d.items():
                    if key == 'targetPlanningPerUnit':
                        for b in value:
                            for k, v in b.items():
                                if k == 'targetPlanningPerHour':
                                    for c in v:
                                        for kk, vv in c.items():
                                            if kk == 'hour':
                                               r.append(vv)

            return set(r)
        def convert_flatten(mylist, parent_key ='', sep ='_',parents=[]):
            """
            This function iterates over one dict and returns a list of tuples: (key, value, parent_keys)
            Usefull for looping through a multidimensional dictionary.
            """
            r = []
            a = []

            for d in mylist:
                for k, v in d.items():
                    if k == 'day':
                        new_key = parent_key + sep + v if parent_key else v
                    if k == 'targetPlanningPerUnit':
                        for b in v:
                            for key, value in b.items():
                                if key == 'unit':
                                   key_key =  parent_key + sep + value if parent_key else value
                                if key == 'targetPlanningPerHour':
                                   for c in value:
                                      for kk, vv in c.items():
                                            if kk == 'hour':
                                                key_key_key =  parent_key + sep + vv if parent_key else vv
                                            if kk == 'numberOfRequiredEmployees':
                                                new_values =  parent_key + sep + vv if parent_key else vv



                                                r.append((new_key, key_key, key_key_key))
                                                a.append(new_values)

            dictionary_demand= dict(zip(r, a))                        
            return (dictionary_demand)

        units = iterate_dict_unit(percept[0])
        days = [li['day'] for li in percept[0]]
        hours = iterate_dict_hour(percept[0])
        employees = [li['id'] for li in percept[1]]

        compensation = [li['compensation'] for li in percept[1]]
        bonus = [li['overtime_bonus'] for li in percept[1]]
        skills = [li['skills'] for li in percept[1]]
        availability = [li['availability'] for li in percept[1]]

        def make_workinghours(availability_data):
            r = []

            for i in availability_data:
                   r_new = list(range(i[0],i[1]+1, 1))
                   r.append(r_new)
            return(r)

        availability_correct = make_workinghours(availability)

        dictionary_compensation = dict(zip(employees, compensation))
        dictionary_bonus = dict(zip(employees, bonus))
        dictionary_skills = dict(zip(employees, skills))
        dictionary_availability = dict(zip(employees, availability_correct))
        dictionary_demand = convert_flatten(percept[0])


        values = list(set([ x for y in dictionary_skills.values() for x in y]))
        data = {}
        for key in dictionary_skills.keys():
            data[key] = [ True if value in dictionary_skills[key] else False for value in values ]
        data_skills = pd.DataFrame(data, index=values).transpose()



        values_1 = list(set([ x for y in dictionary_availability.values() for x in y]))
        data_1 = {}
        for key in dictionary_availability.keys():
            data_1[key] = [ True if value in dictionary_availability[key] else False for value in values_1 ]
        data_availability = pd.DataFrame(data_1, index=values_1).transpose()


        model = AbstractModel()

        model.HOURS = Set(initialize = hours)
        model.DAYS = Set(initialize = days)


        model.EMPLOYEES= Set(initialize = employees)
        model.UNITS = Set(initialize = units)



        def s_init(Model, i, j):
                  if data_skills.at[i, j] == True:
                     return (1)
                  else:
                     return (0)

        def h_init(Model, i, j):
                  if data_availability.at[i, j] == True:
                     return (1)
                  else:
                     return (0)           



        model.skills = Param(model.EMPLOYEES, model.UNITS, initialize=s_init)
        model.availability = Param(model.EMPLOYEES, model.HOURS, initialize=h_init)
        model.compensation = Param(model.EMPLOYEES, initialize = dictionary_compensation)
        model.bonus = Param(model.EMPLOYEES, initialize = dictionary_bonus)
        model.demand = Param (model.DAYS, model.UNITS, model.HOURS, initialize = dictionary_demand)


        model.a = Var(model.DAYS, model.UNITS, model.HOURS, model.EMPLOYEES, domain=Binary, initialize = 0)
        model.b = Var(model.EMPLOYEES,initialize = 0)

        def obj_expression(model):
            cost = 0
            for day, unit, hour, employee in product(model.DAYS,  model.UNITS, model.HOURS, model.EMPLOYEES):
                 cost += model.compensation[employee]* model.a[day, unit, hour, employee]
            bonus=0
            for employee in  model.EMPLOYEES:
                 bonus += model.bonus[employee]* model.b[employee]
            total_cost = cost + bonus
            return total_cost 

        model.OBJ = Objective(rule=obj_expression, sense=minimize)

        def rule_variable(model, i):  
                return (model.b[i]) ==  max(np.count_nonzero(model.a[n,m,j,i] for n in model.DAYS for m in model.UNITS for j in model.HOURS )-40,0)


        model.constraint_variable = Constraint(model.EMPLOYEES, rule=rule_variable)
        
        

        def rule_first(model, n, m, j ):  
                return sum(model.a[n,m,j,i] for i in model.EMPLOYEES) >= model.demand[n,m,j] 

        model.constraint_first = Constraint(model.DAYS, model.UNITS, model.HOURS, rule=rule_first)
        
        

        def rule_second(model, i):  
                return sum(model.a[n,m,j,i] for n in model.DAYS for m in model.UNITS for j in model.HOURS) <= 50 

        model.constraint_second = Constraint(model.EMPLOYEES, rule=rule_second)
        

        def rule_second_day(model, n, i):  
                return sum(model.a[n,m,j,i]  for m in model.UNITS for j in model.HOURS) <= 10 

        model.constraint_second_day = Constraint(model.DAYS, model.EMPLOYEES, rule=rule_second_day)
        
        

        def rule_third(model, n,m,j,i):  
                return model.a[n,m,j,i]  <= model.availability[i,j]

        model.constraint_third = Constraint(model.DAYS, model.UNITS, model.HOURS, model.EMPLOYEES, rule=rule_third)
        
        

        def rule_fourth(model, n,m,j,i):  
                return model.a[n,m,j,i] <= model.skills[i,m]


        model.constraint_fourth = Constraint(model.DAYS, model.UNITS, model.HOURS, model.EMPLOYEES, rule=rule_fourth)
        
        

        def rule_fifth(model, n,j, i):  
                return sum(model.a[n,m,j,i] for m in model.UNITS) <= 1


        model.constraint_fifth = Constraint(model.DAYS, model.HOURS, model.EMPLOYEES, rule=rule_fifth)
        

        opt = SolverFactory('glpk')


        instance = model.create_instance() # reading in a datafile
        results = opt.solve(instance, tee=True)

        

        d = {}
        variables= []
        for v in instance.component_objects(Var, active=True):
               d[v] = {} 
               varobject = getattr(instance, str(v))
               for index in varobject:
                   d[v][index] = varobject[index].value
                   variables.append(v)


        mylist= []
        for key in d:
            mylist.append(key)



        def iterate_new(listlistt, parents=[]):

            r = []
            for k in listlistt:
                if k == mylist[0]: 
                     new_dic = d[k]

                     return(new_dic)


        new_dic = iterate_new(d) 
        
        
        final = {} 
        for day in days:
            for hour in hours:
                for unit in units:
                    final[(day, hour, unit)] = []        
        
        
        
        
        def iterate_again(new_new_dic, parents=[]):
            for k,v in new_new_dic.items():
                if v == 1:
                   for key, value in final.items():
                       if key[0]==k[0] and key[1]==k[2] and key[2]==k[1]:
                          final[key].append(k[3])




            return(final)


        final_new_dic = iterate_again(new_dic)
        
            
        
        
        return final_new_dic

    return Agent(program)
    
