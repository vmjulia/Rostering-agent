from rostering_agent import RosteringAgent
from forecast import forecast
from employees import employees as employee_data

days = ['Monday', 'Tuesday']
hours = [8, 9, 10, 11, 12, 13, 14, 15, 16]
units = ['5ddedba73f6de700081c88cf', '5ddedba73f6de700081c88d3',
         '5ddedba73f6de700081c88d1', '5ddedba73f6de700081c88ce',
         '5ddedba73f6de700081c88d0', '5ddedba73f6de700081c88d2']
employees = ['5ddedba83f6de700081c899a', '5ddedba83f6de700081c89d6',
             '5ddedba83f6de700081c894f', '5ddedba83f6de700081c8959',
             '5ddedba83f6de700081c89bd', '5ddedba83f6de700081c89cc',
             '5ddedba83f6de700081c8968', '5ddedba83f6de700081c89c2',
             '5ddedba83f6de700081c8981', '5ddedba83f6de700081c895e',
             '5ddedba83f6de700081c8940', '5ddedba83f6de700081c8977',
             '5ddedba83f6de700081c896d', '5ddedba83f6de700081c898b',
             '5ddedba73f6de700081c8936', '5ddedba83f6de700081c8995',
             '5ddedba83f6de700081c89a4', '5ddedba83f6de700081c8963',
             '5ddedba83f6de700081c8954', '5ddedba83f6de700081c89b8',
             '5ddedba73f6de700081c892c', '5ddedba83f6de700081c899f',
             '5ddedba83f6de700081c8990', '5ddedba83f6de700081c8945',
             '5ddedba83f6de700081c894a', '5ddedba83f6de700081c8972',
             '5ddedba83f6de700081c89b3', '5ddedba83f6de700081c89a9',
             '5ddedba73f6de700081c8931', '5ddedba83f6de700081c897c',
             '5ddedba83f6de700081c89ae', '5ddedba83f6de700081c89d1',
             '5ddedba83f6de700081c8986', '5ddedba83f6de700081c893b',
             '5ddedba83f6de700081c89c7', '5ddedba83f6de700081c8a8f',
             '5ddedba83f6de700081c8a94', '5ddedba83f6de700081c8a8a',
             '5ddedbb33f6de700081ca7f0']


def test_roster_output():

    percept = forecast, employee_data

    agent = RosteringAgent()

    roster = agent.program(percept)

    assert isinstance(roster, dict)

    for (shift_identifier), employee_list in roster.items():
        assert isinstance(shift_identifier, tuple)
        assert len(shift_identifier) == 3

        day, hour, unit = shift_identifier
        assert day in days
        assert hour in hours
        assert unit in units

        assert isinstance(employee_list, list)
        for employee in employee_list:
            assert employee in employees


if __name__ == '__main__':
    test_roster_output()
