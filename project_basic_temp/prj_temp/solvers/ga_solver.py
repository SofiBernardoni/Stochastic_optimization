########## decide fitness_val_non_feasible##########à

import random
import numpy as np

#import sys
#import os
#sys.path.append(os.path.abspath("D:\Gaia\Politecnico\Magistrale\Numerical optimization\\assignment_Fadda\Stochastic_optimization\project_basic_temp\prj_temp\instances")) # Add instances path to solvers directory
#from instances import * # aggiustare NON LO VEDE #

from ..instances import * #importato ma attenzione che funge solo se usato come parte di un pacchetto...(importazione relativa)


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
        self.population=[0]*self.n_individual #population=list of decisional_variables()
        self.fitness=[0]*self.n_individual #list of fitness values (associated with individuals in population)
        n=0 #counter of solutions in the initial population
        not_feasible_individuals=0 # counter of not feasible solutions in the initial population

        room_set=set(range(0,self.h.n_rooms)) #set containing all room numbers

        while n<self.n_individual:
            ##################### SOLUTION GENERATION ######################
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
                CN[s,:]= random.choices(nurses_available, k=self.h.n_rooms) #choosing 1 available nurse for each room in shift s

            # op generation (operating theaters for patients)
            # If it's not compatible (due to H4) a new op is generated
            op_theaters_list=list(range(0,self.h.n_op_theaters)) #list of operating theaters
            op_generated=False
            while not op_generated:
                op=[random.choice(op_theaters_list) for p in range(0,self.h.n_patients)] #pos=id patient, el: room assigned
                # Checking if op is compatible with H4: op_theaters availability constraint.
                feasible=True
                d=0
                while feasible and d<self.h.n_days:
                    new_patients={p for p in range(0, self.h.n_patients) if ad[p]==d} #set of incoming patients of day d
                    op_theater_daily_occupancy=[0]*self.h.n_op_theaters #position=id_op_th, el: total_occupancy in day d
                    for p in new_patients:
                        op_ass=op[p]
                        op_theater_daily_occupancy[op_ass] +=self.h.patients[p]["surgery_duration"] #adding surgery duration to total working hours of op_theater
                    o=0
                    while feasible and o <self.h.n_op_theaters:
                        if op_theater_daily_occupancy[o] > self.h.op_theaters_availability[d,o]: #### H4 ####
                            feasible=False
                        o+=1
                    d+=1
                if feasible: #we can stop generating op because this choice is a valid one
                        op_generated=True

            dv= decisional_variables(pr,ad,op,CN) #proposed solution

            ########## FITNESS EVALUATION OF SOLUTION #############
            # Note that the proposed solution could still be NOT feasible due to H1 or H7 (we admit init_feasible_perc of the initial population not feasible )
            #feasible_sol=True
            sc = Scheduling(self.h, dv)
            sc.initial_condition() #setting initial conditions
            sc.global_constr_check() #H5,H6 (already checked we can remove them) #S7, S8
            sc.insert_new_exit() #exiting and entering patients
            sc.SCP_constr_check() #H3,H4 (already checked we can remove them) #S5, S6
            sc.PSA_NRA_constr_check() #H2 (already checked we can remove it) #H1,H7 #S1,S2,S3,S4
            fitness_value=sc.fitness() #computing fitness of the solution
            feasible_sol=sc.feasible

            # Saving the new individual if feasible or if not feasible but still acceptable
            if not feasible_sol:
                if not_feasible_individuals<self.n_individual*(1-self.init_feasible_perc): #we can still admit not feasible solutions in our initial population
                    self.population[n]=dv #saving the new individual
                    self.fitness[n]=fitness_val_non_feasible #saving fitness value ##################### CHOOSE BAD FITNESS VALUE TO USE (APPROX) ###########à
                    not_feasible_individuals+=1
                    n+=1
            else:
                self.population[n]=dv #saving the new individual
                self.fitness[n]=fitness_value #saving fitness value
                n+=1

        ############ BEST INDIVIDUALS SEARCH : trying new CN's proposal for them (saving the best one) ##################
        ordered_ind_indexs=sorted(range(self.n_individual), key=lambda x: self.fitness[x], reverse=False) #list of indexes ordered for increasing fitness value
        n_init_best=self.n_individual*self.init_best_perc # number of good solutions
        for i in range(0,n_init_best): #working on the n_init_best best solutions (lowest fitness)
            id=ordered_ind_indexs[i]
            sol=self.population[id] #individual
            fit_val= self.fitness[id] #original fitness value

            # Computing different CN's proposal for the solution
            for j in range(0,self.n_different_CN):
                # CN generation (nurse for room-shift couple)
                CN_new=np.array([[0]*self.h.n_rooms]*(self.h.n_shifts*self.h.n_days)) #[CN]ij, i=id_room, j=shift 0...D*3-1, el: id_nurse
                for s in range(0, self.h.n_shifts*self.h_n_days):
                    nurses_available=list(self.h.working_shifts[s].keys()) #working_shifts=list of dictionaries(one for shift) with key= nurse_id, value=max_load
                    CN_new[s,:]= random.choices(nurses_available, k=self.h.n_rooms) #choosing 1 available nurse for each room in shift s
                # Evaluating fitness of the solution with CN_new
                dv_new= decisional_variables(sol.pr,sol.ad,sol.op,CN_new) #new proposed solution
                #feasible_new=True
                sc_new = Scheduling(self.h, dv_new)
                sc_new.initial_condition() #setting initial conditions
                sc_new.global_constr_check() #H5,H6 (already checked we can remove them) #S7, S8
                sc_new.insert_new_exit() #exiting and entering patients
                sc_new.SCP_constr_check() #H3,H4 (already checked we can remove them) #S5, S6
                sc_new.PSA_NRA_constr_check() #H2 (already checked we can remove it) #H1,H7 #S1,S2,S3,S4
                fitness_new=sc_new.fitness() #computing fitness of the solution
                feasible_new=sc_new.feasible
                if feasible_new and fitness_new<fit_val: #the new solution has improved the original one (substitution)
                    self.population[id]=dv_new
                    self.fitness[id]=fitness_new
                    #Updating the 'golden standard'
                    sol=dv_new
                    fit_val=fitness_new
        ############# STORING BEST INDIVIDUAL #########
        best_id=min(range(self.n_individual), key=lambda x: self.fitness[x]) #index of smallest fitness
        self.best_sol=self.population[best_id] #best individual seen so far
        self.best_fit= self.fitness[best_id] #fitness of best individual

    # SELECTION FUNCTION: selection of a couple of parents
    def selection(self):

        pass
        #return (p1,p2)

    # CROSSOVER FUNCTION: generation of a couple of children with crossover from parents (p1,p2)
    def crossover(self,p1,p2):

        pass
        #return (c1,c2)

    # MUTATION FUNCTION: introduction of random mutations in the individual
    def mutation(self,ind):

        pass
        #return ind






    def solve(self):
        #initialization
        #new population generation
            #selection
            #crossover
            #mutation
            # STOPPING CRITERION


        pass


