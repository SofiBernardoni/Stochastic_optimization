######################### remove already checked hard constraints #####################################

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

    #weights
    weights={
        "room_mixed_age": 0,
        "room_nurse_skill": 0,
        "continuity_of_care": 0,
        "nurse_eccessive_workload": 0,
        "open_operating_theater": 0,
        "surgeon_transfer": 0,
        "patient_delay": 0,
        "unscheduled_optional": 0
    }
    ##############


    def __init__(self, n_days,skill_levels, shift_types, age_groups, n_nurses, nurses_skill_levels, working_shifts, n_surgeons, surgeons_availability,
                 n_op_theaters, op_theaters_availability, n_rooms,rooms_capacity,n_occupants,occupants,n_patients,patients, weights):
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
        self.weights=weights



class decisional_variables():
    #h = Hospital()

    #decision variables
    #pr=[0]*h.n_patients #pos=id patient, el: room
    #ad=[0]*h.n_patients #pos=id_patient, el: admission date= 0...D, ad=D if postponed
    #op=[0]*h.n_patients #pos=id_patient , el: op_theater
    #CN=np.array([[0]*h.n_rooms]*(h.n_shifts*h.n_days)) #[CN]ij, i=id_room, j=shift 0...D*3-1, el: id_nurse

    def __init__(self,pr,ad,op,CN):
        #self.h=h
        self.pr = pr #pos=id patient, el: room
        self.ad = ad #pos=id_patient, el: admission date= 0...D, ad=D if postponed
        self.op = op #pos=id_patient , el: op_theater
        self.CN =CN #[CN]ij, i=id_room, j=shift 0...D*3-1, el: id_nurse
        n_pat=len(pr)
        if len(self.ad)!= n_pat or len(self.op)!= n_pat:
            print("ERROR: pr,ad and op need to have the same length")



class Scheduling():
    h=Hospital()
    dv=decisional_variables()

    new_patients =[set()]*(h.n_days) # id= day, element: set of incoming patients
    exit_patients=[set()]*(h.n_days) #id=day, el: set of exiting patients

    exit_occupants=[set()]*(h.n_days) #id=day, el: set of exiting occupants

    room_to_patient=[[set(), set()]]*h.n_rooms # id=n_room, set1= patients in the room, set2=occupants in the room

    room_occupants=[]*(h.n_occupants) #occupants' room

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
    delays=[0]*h.n_patients #pos=id_patients, el:delay #S7
    unscheduled_patients=set() #set of unscheduled patients #S8

    #total surgeons_transfer
    tot_tranfer=0 #S6
    tot_op_theater_opened=0 #S5
    tot_diff_age=0 #S1
    tot_skill_vio=0 #S2
    tot_eccessive_work=0 #S4
    tot_continuity_of_care=0 #S3

    def __init__(self, hospital, dv):
        self.h =hospital
        self.dv=dv
        if len(self.dv.pr) != self.h.n_patients:
            print("ERROR: decision variables' size not compatible with the number of patients in the hospital list")
        (nrow,ncol)=self.dv.CN.shape
        if nrow!= self.h.n_days*self.h.n_shifts:
            print("ERROR: CN's size not compatible with the number of scheduling days and hospital shifts")
        if ncol!= self.h.n_rooms:
            print("ERROR: CN's size not compatible with the number of hospital rooms")
        self.feasible=True

    # funzione condizione iniziale
    def initial_condition(self):
        for id_occ in range(0,self.h.n_occupants): #set initial conditions with occupants' infos
            r_id= self.h.occupants[id_occ]["room_id"] #room id of occupant i es: "r00"
            num_r=int(r_id[1:]) #remove the "r" and to_int
            self.room_to_patient[num_r][1].add(id_occ) #occupants in rooms
            self.room_occupants[id_occ]=num_r # save in occupants' room for exiting occupants
            if self.room_gender[num_r] is None: #set initial gender in the room
                self.room_gender[num_r]=self.h.occupants[id_occ]["gender"]
            age_num=self.h.occupants[id_occ]["age_group"] #set initial room ages
            self.room_age[num_r].add(age_num)
            self.room_age_counter[num_r][age_num]+=1
            day_ex=self.h.occupants[id_occ]["length_of_stay"] #vedi se convertire int
            self.exit_occupants[day_ex].add(id_occ) #exit days of occupants


    def global_constr_check(self):
        #H5: check mandatory patients are admitted, H6: check admission date feasibility
        #H5 is automatically check supposing that self.h.patients[p]["surgery_due_day"] < n_days
        #S7 calculating delays
        #S8 calculating postponed patients
        p=0
        while self.feasible and p<self.h.n_patients:
            ad_date = self.dv.ad[p]  # admission date
            if self.h.patients[p]["mandatory"]: #mandatory patient
                if ad_date < self.h.patients[p]["surgery_release_day"] or ad_date > self.h.patients[p]["surgery_due_day"]: ######################## ALREADY CHECKED ########
                    self.feasible=False #admission date out of range
                else:
                    self.delays[p]=ad_date - self.h.patients[p]["surgery_release_day"] # delay
            else: #optional patient
                if ad_date < self.h.patients[p]["surgery_release_day"]: #for optional patient no due date ######################## ALREADY CHECKED ########
                    self.feasible=False
                else:
                    if ad_date == self.h.n_days: #postponed
                        self.unscheduled_patients.add(p)
                    else: #admitted
                        self.delays[p]=ad_date - self.h.patients[p]["surgery_release_day"] # delay
            p+=1

    def insert_new_exit(self): #inserting values in new patients and exit patients
        for p in range(0, self.h.n_patients):
            ad_date = self.dv.ad[p]
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
                op_ass=self.dv.op[p]
                self.surgeon_daily_work[doc_id] += surg_duration #adding surgery duration to total working hours of doc
                self.op_theater_daily_occupancy[op_ass] +=surg_duration #adding surgery duration to total working hours of op_theater
                self.op_to_surgeon[doc_id].add(op_ass) #add op_the to set of op_the used by the surgeon in the day

            o=0
            while self.feasible and o <self.h.n_op_theaters:
                if self.op_theater_daily_occupancy[o] > self.h.op_theaters_availability[d,o]: #H4 ######################## ALREADY CHECKED ########
                    self.feasible=False
                elif self.op_theater_daily_occupancy[o] !=0: #S5
                    self.tot_op_theater_opened +=1
                o+=1

            s=0
            while self.feasible  and s < self.h.n_surgeons:
                if self.surgeon_daily_work[s] > self.h.surgeons_availability[d,s]: #H3 ######################## ALREADY CHECKED ########
                    self.feasible = False
                else:
                    self.tot_tranfer += len(self.op_to_surgeon[s])-1 #S6
                s+=1

            d+=1


    def PSA_NRA_constr_check(self):
        #H2 compatible rooms
        ################################ already checked #############################
        p=0
        while self.feasible and p<self.h.n_patients:
            room=self.dv.pr[p]
            #dati caricati già come id stanze senza lettere
            if room in self.h.patients[p]["incompatible_room_ids"]:
                self.feasible=False
            p+=1
        ##############################################################################

        #H1 homogeneus gender for room
        #H7 room capacity
        #S1 calulating age difference for room
        #S2 calculating minium skill level
        #S3 continuity of care
        #S4 calculating max_workload

        d=0
        while self.feasible and d < self.h.n_days:

            #PEOPLE ENTERING
            for np in self.new_patients[d]:
                room=self.dv.pr[np]

                if self.room_gender[room] is not None and self.room_gender[room] != self.h.patients[np]["gender"]:
                    self.feasible=False #H1
                elif self.room_gender[room] is None:
                    self.room_gender[room] = self.h.patients[np]["gender"] #updating data about gender in the room

                self.room_to_patient[room][0].add(np) #adding new patient in the room

                #updating data about age in the room
                age_num = self.h.occupants[np]["age_group"]  # set initial room ages
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


            work_nurses=[0]*self.h.n_nurses #total nurses workload in the day (every nurse does just one shift per day)

            #vediamo poi se si puo unnire

            for r in range(0,self.h.n_rooms):
                tot_work_room=[0]*self.h.n_shifts # tot workload in a room in every shift for a day
                max_skill_room=[0]*self.h.n_shifts  #max skill level required in a room for every shift in a day
                nurse_seen_day=[0]*self.h.n_shifts #nurses for the room for the day

                for shi in range(0, self.h.n_shifts):
                    s=(self.h.n_shifts * d) + shi
                    id_nurse=self.dv.CN[r, s]
                    if self.h.working_shifts[s].get(id_nurse) is None:   ######################à ALREADY CHECKED############### #check if the nurse is working in the shift
                        self.feasible=False
                    else:
                        nurse_seen_day[shi]=id_nurse

                if not self.feasible: #exiting because nurses not available
                    break

                for pa in self.room_to_patient[r][0]: #patients in the room
                    first_index=self.h.n_shifts*(d-self.dv.ad[pa])
                    for sh in range(0, self.h.n_shifts):
                        tot_work_room[sh] += self.h.patients[pa]["workload_produced"][first_index+sh] # adding workload requested in the shift
                        max_skill_room[sh] =max(max_skill_room[sh], self.h.patients[pa]["skill_level_required"][first_index+sh]) #updating skill level requested in the shift
                        self.nurse_to_patient[pa].add(nurse_seen_day[sh]) #adding the nurse seen by the patient

                for oc in self.room_to_patient[r][1]: #occupants in the room
                    first_index=self.h.n_shifts*d #admission date=0 for occupants
                    for sh in range(0, self.h.n_shifts):
                        tot_work_room[sh] += self.h.occupants[oc]["workload_produced"][first_index+sh] # adding workload requested in the shift
                        max_skill_room[sh] =max(max_skill_room[sh], self.h.occupants[oc]["skill_level_required"][first_index+sh]) #updating skill level requested in the shift
                        self.nurse_to_occupant[oc].add(nurse_seen_day[sh]) #adding the nurse seen by the patient

                for t in range(0,self.h.n_shifts):
                    self.tot_skill_vio += max(max_skill_room[t]-self.h.nurses_skill_levels[nurse_seen_day[t]],0) #S2 difference between skill levels of the nurse and required
                    work_nurses[nurse_seen_day[t]]+= tot_work_room[t] #adding workload to the nurse

            for k in range(0,self.h.n_shifts):
                total_shift=self.h.n_shifts*d+k
                for n in range(0,self.h.n_nurses):
                    self.tot_eccessive_work += max(0, work_nurses[n]-self.h.working_shifts[total_shift][n]) #S4


            #PEOPLE EXITING
            for ep in self.exit_patients[d]:
                room=self.dv.pr[ep]
                self.room_to_patient[room][0].remove(ep)  # removing patients
                if len(self.room_to_patient[room][0])+len(self.room_to_patient[room][1]) ==0:
                    self.room_gender[room] = None

                age=self.h.patients[ep]["age_group"]
                self.room_age_counter[room][age]-=1
                if self.room_age_counter[room][age]==0:
                    self.room_age[room].remove(age)

            for eo in self.exit_occupants[d]:
                room=self.room_occupants[eo]
                self.room_to_patient[room].remove(eo) #removing occupant
                if len(self.room_to_patient[room][0]) + len(self.room_to_patient[room][1]) == 0:
                    self.room_gender[room] = None

                age = self.h.occupants[eo]["age_group"]
                self.room_age_counter[room][age] -= 1
                if self.room_age_counter[room][age] == 0:
                    self.room_age[room].remove(age)

            d+=1
        for pp in range(0, self.h.n_patients):
            self.tot_continuity_of_care += len(self.nurse_to_patient[pp])

        for oo in range(0, self.h.n_occupants):
            self.tot_continuity_of_care += len(self.nurse_to_occupant[oo])


    def fitness(self):
        tot_delays =sum(self.delays)
        tot_unscheduled=len(self.unscheduled_patients)

        S6=self.tot_tranfer*self.h.weights["surgeon_transfer"]
        S5=self.tot_op_theater_opened*self.h.weights["open_operating_theater"]
        S1=self.tot_diff_age*self.h.weights["room_mixed_age"]
        S2=self.tot_skill_vio*self.h.weights["room_nurse_skill"]
        S4=self.tot_eccessive_work*self.h.weights["nurse_eccessive_workload"]
        S3=self.tot_continuity_of_care*self.h.weights["continuity_of_care"]
        S7=tot_delays*self.h.weights["patient_delay"]
        S8=tot_unscheduled*self.h.weights["unscheduled_optional"]


        return S1+S2+S3+S4+S5+S6+S7+S8












