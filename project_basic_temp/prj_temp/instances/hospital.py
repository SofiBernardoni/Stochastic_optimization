import math
import numpy as np

class Hospital():

    n_days= 7
    skill_levels=3
    shift_types={
        "early":0,
        "late":1,
        "night":2
    }
    n_shifts=3
    age_groups={
        "infant":0,
        "adult":1,
        "elderly":2
    }

    # nurses (id="n00")
    n_nurses=0
    nurses_skill_levels=[0]*n_nurses #position=id , info = skill_level
    working_shifts=[{}]*(n_days*n_shifts) #list of dictionaries(one for shift) with key= nurse_id, value=max_load

    # surgeons (id="s00")
    n_surgeons=0
    surgeons_availability=np.array([[[0]*n_surgeons]*n_days]) # matrix number_days x n_surgeons with max surgery time

    # op_theaters (id="t00")
    n_op_theaters=0
    op_theaters_availability=np.array([[[0]*n_op_theaters]*n_days]) # matrix number_days x n_op_theaters with op_theatres_availability

    # rooms (id="r00")
    n_rooms=0
    rooms_capacity=[0]*n_rooms #positions=id with room capacity

    # occupants (id="a00")
    n_occupants=0
    occupants=[{}]*n_occupants #list of dictionaries of occupants position=id

    # patients (id="p00")
    n_patients=0
    patients=[{}]*n_patients #list of dictionaries of patients position=id

    ##############


    def __init__(self, n_days,skill_levels, shift_types, n_shifts, age_groups, n_nurses, nurses_skill_levels, working_shifts, n_surgeons, surgeons_availability,
                 n_op_theaters, op_theaters_availability, n_rooms,rooms_capacity,n_occupants,occupants,n_patients,patients):
        self.n_days = n_days
        self.skill_levels =skill_levels
        self.shift_types = shift_types
        self.n_shifts = n_shifts
        self.age_groups =age_groups
        self.n_nurses = n_nurses
        self.nurses_skill_levels =nurses_skill_levels
        self.working_shifts = working_shifts
        self.n_surgeons = n_surgeons
        self.surgeons_availability = surgeons_availability
        self.n_op_theaters = n_op_theaters
        self.op_theaters_availability = op_theaters_availability
        self.n_rooms = n_rooms
        self.rooms_capacity = rooms_capacity
        self.n_occupants = n_occupants
        self.occupants = occupants
        self.n_patients = n_patients
        self.patients = patients


'''
    def add_patient(self, idx_room):
        self.occupation[idx_room] += 1

    def remove_patient(self, idx_room):
        self.occupation[idx_room] -= 1

    def fitness(self):
        return math.abs(sum(self.occupation) - 2 * self.n_rooms) 
'''

class Scheduling():
