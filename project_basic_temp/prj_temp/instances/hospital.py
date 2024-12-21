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
    n_age=3

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


    def __init__(self, n_days,skill_levels, shift_types, age_groups, n_nurses, nurses_skill_levels, working_shifts, n_surgeons, surgeons_availability,
                 n_op_theaters, op_theaters_availability, n_rooms,rooms_capacity,n_occupants,occupants,n_patients,patients):
        self.n_days = n_days
        self.skill_levels =skill_levels
        self.shift_types = shift_types
        self.n_shifts = len(self.shift_types)
        self.age_groups =age_groups
        self.n_age=len(self.age_groups)
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
    hospital=Hospital()

    #decision variables
    pr=[0]*hospital.n_patients
    ad=[0]*hospital.n_patients
    op=[0]*hospital.n_patients
    CN=np.array([[0]*hospital.n_rooms]*(hospital.n_shifts*hospital.n_days))


    new_patients =[set()]*(hospital.n_days) # id= day, element: set of incoming patients
    exit_patients=[set()]*(hospital.n_days) #id=day, el: set of exiting patients

    room_to_patient=[[set(), set()]]*hospital.n_rooms # id=n_room, set1= patients in the room, set2=occupants in the room


    # constraints PSA
    room_gender=[None]*hospital.n_rooms

    room_age = [set()] * hospital.n_rooms  # id=n_room, el: set of ages in the room
    room_age_counter = [[0] * hospital.n_age] * hospital.n_rooms  # id=n_room, el: list with ith-element= number of people with age level i in the room

    # constraints NRA
    room_skill_level=[0]*hospital.n_rooms #maximum skill level for shift, position=id_room
    room_workload=[0]*hospital.n_rooms #total workload for shift, position=id_room
    nurse_to_patient = [set()] * hospital.n_patients #position=id_patient , el: set of nurses
    nurse_to_occupant = [set()] * hospital.n_occupants #position=id_occupant, el: set of nurses

    # constraints SCP
    surgeon_daily_work=[0]*hospital.n_surgeons #position=id_surgeon, el: total_work_surgeon in a day
    op_theater_daily_occupancy=[0]*hospital.n_op_theaters #position=id_op_th, el: total_occupancy in a day
    room_to_surgeon=[set()]*hospital.n_surgeons #pos= id_surgeon, el: set of op_theater_used_in a day

    # global constraints
    delays=[0]*hospital.n_patients #pos=id_patients, el:delay
    unscheduled_patients=set() #set of unscheduled patients



    def __init__(self):