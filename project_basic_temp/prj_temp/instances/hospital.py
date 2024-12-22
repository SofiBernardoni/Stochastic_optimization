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
    h=Hospital()

    #decision variables
    pr=[0]*h.n_patients #pos=id patient, el: room
    ad=[0]*h.n_patients #pos=id_patient, el: admission date= 0...D, ad=D if postponed
    op=[0]*h.n_patients #pos=id_patient , el: op_theater
    CN=np.array([[0]*h.n_rooms]*(h.n_shifts*h.n_days)) #[CN]ij, i=id_room, j=shift 0...D*3-1, el: id_nurse


    new_patients =[set()]*(h.n_days) # id= day, element: set of incoming patients
    exit_patients=[set()]*(h.n_days) #id=day, el: set of exiting patients

    exit_occupants=[set()]*(h.n_days) #id=day, el: set of exiting occupants

    room_to_patient=[[set(), set()]]*h.n_rooms # id=n_room, set1= patients in the room, set2=occupants in the room


    # constraints PSA
    room_gender=[None]*h.n_rooms

    room_age = [set()] * h.n_rooms  # id=n_room, el: set of ages in the room
    room_age_counter = [[0] * h.n_age] * h.n_rooms  # id=n_room, el: list with ith-element= number of people with age level i in the room

    # constraints NRA
    room_skill_level=[0]*h.n_rooms #maximum skill level for shift, position=id_room
    room_workload=[0]*h.n_rooms #total workload for shift, position=id_room
    nurse_to_patient = [set()] * h.n_patients #position=id_patient , el: set of nurses
    nurse_to_occupant = [set()] * h.n_occupants #position=id_occupant, el: set of nurses

    # constraints SCP
    surgeon_daily_work=[0]*h.n_surgeons #position=id_surgeon, el: total_work_surgeon in a day
    op_theater_daily_occupancy=[0]*h.n_op_theaters #position=id_op_th, el: total_occupancy in a day
    op_to_surgeon=[set()]*h.n_surgeons #pos= id_surgeon, el: set of op_theater_used_in a day

    # global constraints
    delays=[0]*h.n_patients #pos=id_patients, el:delay
    unscheduled_patients=set() #set of unscheduled patients

    #total surgeons_transfer
    tot_tranfer=0 #S6
    tot_op_theater_opened=0 #S5
    tot_diff_age=0 #S1


    def __init__(self, hospital,pr,ad,op,CN):
        '''
        new_patients, exit_patients, room_to_patient, room_gender, room_age, room_age_counter, room_skill_level,
        room_workload, nurse_to_patient, nurse_to_occupant, surgeon_daily_work, op_theater_daily_occupancy, room_to_surgeon, delays, unscheduled_patients
        '''
        self.h =hospital
        self.pr = pr
        self.ad = ad
        self.op = op
        self.CN =CN
        '''
        self.new_patients =new_patients
        self.exit_patients = exit_patients
        self.room_to_patient = room_to_patient
        self.room_gender = room_gender
        self.room_age = room_age
        self.room_age_counter = room_age_counter
        self.room_skill_level = room_skill_level
        self.room_workload = room_workload
        self.nurse_to_patient = nurse_to_patient
        self.nurse_to_occupant =nurse_to_occupant
        self.surgeon_daily_work = surgeon_daily_work
        self.op_theater_daily_occupancy = op_theater_daily_occupancy
        self.room_to_surgeon = room_to_surgeon
        self.delays = delays
        self.unscheduled_patients = unscheduled_patients
        '''

        #funzione condizione iniziale

    def initial_condition(self):
        for id_occ in range(0,self.h.n_occupants): #set initial conditions with occupants' infos
            r_id= self.h.occupants[id_occ]["room_id"] #room id of occupant i es: "r00"
            num_r=int(r_id[1:]) #remove the "r" and to_int
            self.room_to_patient[num_r][1].add(id_occ) #occupants in rooms
            if self.room_gender[num_r] is None: #set initial gender in the room
                self.room_gender[num_r]=self.h.occupants[id_occ]["gender"]
            age_num=self.h.occupants[id_occ]["age_group"] #set initial room ages
            self.room_age[num_r].add(age_num)
            self.room_age_counter[num_r][age_num]+=1
            day_ex=self.h.occupants[id_occ]["length_of_stay"] #vedi se convertire int
            self.exit_occupants[day_ex].add(id_occ) #exit days of occupants

    feasible=True

    def global_constr_check(self):
        #H5: check mandatory patients are admitted, H6: check admission date feasibility
        #H5 is automatically check supposing that self.h.patients[p]["surgery_due_day"] < n_days
        #S7 calculating delays
        #S8 calculating postponed patients
        p=0
        while self.feasible and p<self.h.n_patients:
            ad_date = self.ad[p]  # admission date
            if self.h.patients[p]["mandatory"]: #mandatory patient
                if ad_date < self.h.patients[p]["surgery_release_day"] or ad_date > self.h.patients[p]["surgery_due_day"]:
                    self.feasible=False #admission date out of range
                else:
                    self.delays[p]=ad_date - self.h.patients[p]["surgery_release_day"] # delay
            else: #optional patient
                if ad_date < self.h.patients[p]["surgery_release_day"]: #for optional patient no due date
                    self.feasible=False
                else:
                    if ad_date == self.h.n_days: #postponed
                        self.unscheduled_patients.add(p)
                    else: #admitted
                        self.delays[p]=ad_date - self.h.patients[p]["surgery_release_day"] # delay
            p+=1

    def insert_new_exit(self): #inserting values in new patients and exit patients
        for p in range(0, self.h.n_patients):
            ad_date = self.ad[p]
            ex_date= ad_date+ self.h.patients[p]["length_of_stay"]
            self.new_patients[ad_date].add(p)
            self.exit_patients[ex_date].add(p)


    def SCP_constr_check(self):
        #H3 max surgery time surgeons
        #H4 max surgery time op_theaters
        #S5 calculating op_the used per day
        #S6 calculating different op_the for surgoen in a day
        d=0
        while self.feasible and d<self.h.n_days:
            for p in self.new_patients[d]:
                surg_duration=self.h.patients[p]["surgery_duration"]
                doc=self.h.patients[p]["surgeon_id"]
                doc_id=int(doc[1:])
                op_ass=self.op[p]
                self.surgeon_daily_work[doc_id] += surg_duration #adding surgery duration to total working hours of doc
                self.op_theater_daily_occupancy[op_ass] +=surg_duration #adding surgery duration to total working hours of op_theater
                self.op_to_surgeon[doc_id].add(op_ass) #add op_the to set of op_the used by the surgeon in the day

            o=0
            while self.feasible and o <self.h.n_op_theaters:
                if self.op_theater_daily_occupancy[o] > self.h.op_theaters_availability[d,o]: #H4
                    self.feasible=False
                elif self.op_theater_daily_occupancy[o] !=0: #S5
                    self.tot_op_theater_opened +=1
                o+=1

            s=0
            while self.feasible  and s < self.h.n_surgeons:
                if self.surgeon_daily_work[s] > self.h.surgeons_availability[d,s]: #H3
                    self.feasible = False
                else:
                    self.tot_tranfer += len(self.op_to_surgeon[s])-1 #S6
                s+=1


            d+=1


    def PSA_NRA_constr_check(self):
        #H2 compatible rooms
        p=0
        while self.feasible and p<self.h.n_patients:
            room=self.pr[p]
            #dati caricati già come id stanze senza lettere
            if room in self.h.patients[p]["incompatible_room_ids"]:
                self.feasible=False
            p+=1

        #H1 homogeneus gender for room
        #H7 room capacity
        #S1 calulating age difference for room
        #S2 calculating minium skill level
        #S3 continuity of care
        #S4 calculating max_workload

        d=0
        while self.feasible and d < self.h.n_days:

            for np in self.new_patients[d]:
                room=self.pr[p]

                if self.room_gender[room] is not None and self.room_gender[room] != self.h.patients[p]["gender"]:
                    self.feasible=False #H1
                elif self.room_gender[room] is None:
                    self.room_gender[room] = self.h.patients[p]["gender"] #updating data about gender in the room

                self.room_to_patient[room][0].add(np) #adding new patient in the room

                #updating data about age in the room
                age_num = self.h.occupants[p]["age_group"]  # set initial room ages
                self.room_age[room].add(age_num)
                self.room_age_counter[room][age_num] += 1

            #S1 e H7
            r=0
            while self.feasible and r < self.h.n_rooms:
                self.tot_diff_age += (max(self.room_age[r])-min(self.room_age[r])) #S1: max difference between age levels
                tot_people=len(self.room_to_patient[r][0])+len(self.room_to_patient[r][1]) #total people in the room
                if tot_people > self.h.rooms_capacity[r]:
                    self.feasible =False #H7
                r+=1






            for np in self.exit_patients[d]:
                self.room_to_patient[self.pr[p]][0].remove(np)  # adding new patient in the room

                #da aggiungere eta e genere
                #
            # EXIT OCCUPANTS

            d+=1

















