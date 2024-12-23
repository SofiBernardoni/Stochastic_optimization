import random
import numpy as np


class Ga_Solver():

    def __init__(self, solver_setting,hospital): #solver_setting=json (with solver paramenters), hospital=Hospital (class)
        self.n_individual = solver_setting['n_individual']
        self.init_feasible_perc = solver_setting['initial_feasible_percentage']
        self.init_best_perc = solver_setting['initial_best_percentage']
        self.n_different_CN = solver_setting['n_different_CN']
        self.multinomial_select_perc = solver_setting['multinomial_selection_percentage']
        self.cross_point_perc = solver_setting['crossover_point_percentage']
        self.mutation_prob = solver_setting['mutation_prob']
        self.feasible_perc = solver_setting['feasible_percentage']
        self.good_fitness_perc = solver_setting['good_function_fitness_percentage']
        self.max_generation = solver_setting['max_generation']
        self.max_time = solver_setting['max_time']
        self.frac_generation_no_improv = solver_setting['fraction_generation_no_improv']
        self.h=hospital

    # INITIALIZATION FUNCTION: to generate the initial population
    def initialization(self):
        n=0 #counter of solutions in the initial population
        room_set=set(range(0,self.h.n_rooms)) #set containing all room numbers

        while n<self.n_individual:
            # pr generation (rooms for patients)
            pr=[0]*self.h.n_patients #pos=id patient, el: room assigned
            for p in range(0,self.h.n_patients):
                compatible_rooms=list(room_set-self.h.patients[p]["incompatible_room_ids"]) #### H2 compatible rooms ####
                pr[p] = random.choice(compatible_rooms)

            # ad generation (admission date for patients)
            # If it's not compatible (due to H3) a new ad is generated
            ad_generated=False
            while not ad_generated:
                ad=[0]*self.h.n_patients #pos=id_patient, el: admission date= 0...D, ad=D if postponed
                for p in range(0,self.h.n_patients):
                    if self.h.patients[p]["mandatory"]: #mandatory patient
                        compatible_dates=list(range(self.h.patients[p]["surgery_release_day"],self.h.patients[p]["surgery_due_day"]+1)) #### H5, H6 ####
                        ad[p]=random.choice(compatible_dates)
                    else: #optional patient
                        compatible_dates=list(range(self.h.patients[p]["surgery_release_day"],self.h.n_days+1)) #### H6 #### (optional patient has no due date and can be postponed i.e. ad=n_days)
                        ad[p]=random.choice(compatible_dates)

                # Checking if ad is compatible with H3: surgeons availability constraint.
                feasible=True
                d=0
                while feasible and d<self.h.n_days:
                    new_patients={p for p in range(0, self.h.n_patients) if ad[p]==d} #set of incoming patients of day d
                    surgeon_daily_work=[0]*self.h.n_surgeons #position=id_surgeon, el: total_work_surgeon in a day
                    for p in new_patients:
                        doc_id=self.h.patients[p]["surgeon_id"]
                        surgeon_daily_work[doc_id] += self.h.patients[p]["surgery_duration"] #adding surgery duration to total working hours of doc
                    s=0
                    while feasible and s < self.h.n_surgeons:
                        if surgeon_daily_work[s] > self.h.surgeons_availability[d,s]: #### H3 ####
                            feasible = False
                        s +=1
                    d +=1
                    if feasible: #we can stop generating ad because this choice is a valid one
                        ad_generated=True

            # CN generation (nurse for room-shift couple)
            CN=np.array([[0]*self.h.n_rooms]*(self.h.n_shifts*self.h.n_days)) #[CN]ij, i=id_room, j=shift 0...D*3-1, el: id_nurse
            for s in range(0, self.h.n_shifts*self.h_n_days):
                nurses_available=list(self.h.working_shifts[s].keys()) #working_shifts=list of dictionaries(one for shift) with key= nurse_id, value=max_load
                CN[:,s]= random.choices(nurses_available, k=self.h.n_rooms) #choosing 1 available nurse for each room in shift s

            # op generation (operating theaters for patients)
            # If it's not compatible (due to H4) a new op is generated
            op_theaters_list=list(range(0,self.h.n_op_theaters)) #list of operating theaters
            op_generated=False
            while not op_generated:
                op=[random.choice(op_theaters_list) for p in range(0,self.h.n_patients)] #pos=id patient, el: room assigned
                # Checking if op is compatible with H4: op_theaters availability constraint.
                feasible=True
                #################################### INSERT H4 checking ###################################
                if feasible: #we can stop generating op because this choice is a valid one
                        op_generated=True











    def solve(self):
        pass


