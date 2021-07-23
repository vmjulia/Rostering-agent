# Rostering-agent
## Intelligent rostering agent for the rostering task environment. It must:

1. Cover all days, hours and units for which a demand forecast is provided.
2. Minimize total costs given by regular labor costs and overtime bonus.
 Calculation of the overtime bonus: If employees work more than more than 40 hours per week, they
receive the overtime bonus (on top of their regular compensation) for these additional hours.
3. Fulfill the predicted demand.
4. Meet labor regulations in that no employee works more than 10 hours per day and 50 hours per week.
5. Only assign employees to a given period if they are available for that period.
1
6. Only assign employees to a given unit if they possess the required skill for that unit (unit = skill). E.g. an
employee must have the skill “kitchen” to work in unit “kitchen”.
7. Only assign an employee to one unit at the same time. E.g. an employee cannot work in the kitchen and at
the bar in parallel.

The output roster must have the following form:
 The roster is given by set of key value pairs (i.e. a Python dictionary).
 Its key is a tuple that identifies each element of the roster by the day, hour and unit, e.g. (day, hour, unit)
 Its value is a list of employees assigned to that particular element of the roster,
e.g. [employeeID1, employeeID2, ...]
 E.g. {(day, hour, unit): [employeeID1, employeeID2, ...], ...}.

