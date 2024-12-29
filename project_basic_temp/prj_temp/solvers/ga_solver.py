import random
import numpy as np
import time #to manage time limits and time measurements

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
        self.max_time = solver_setting['max_time'] # seconds
        self.frac_generation_no_improv = solver_setting['fraction_generation_no_improv']
        self.h=hospital

    # Other ATTRIBUTES in Ga_solver
    # self.population  # current population=list of decisional_variables()
    # self.fitness #list of fitness values (associated with individuals in population)
    # self.ordered_pop_indexs=sorted(range(self.n_individual), key=lambda x: self.fitness[x], reverse=False) #list of indexes ordered for increasing fitness value
    # self.best_sol=self.population[best_id] #best individual seen so far
    # self.best_fit= self.fitness[best_id] #fitness of best individual

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
                #CN[s,:]= random.choices(nurses_available, k=self.h.n_rooms) #choosing 1 available nurse for each room in shift s
                CN[s,:]= np.random.choice(nurses_available, size=self.h.n_rooms, replace=True) #choosing 1 available nurse for each room in shift s
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
                    self.fitness[n]=self.unfeasible_cost #saving fitness value REALLY BAD
                    not_feasible_individuals+=1
                    n+=1
            else:
                self.population[n]=dv #saving the new individual
                self.fitness[n]=fitness_value #saving fitness value
                n+=1

        ############ BEST INDIVIDUALS SEARCH : trying new CN's proposal for them (saving the best one) ##################
        self.ordered_pop_indexs=sorted(range(self.n_individual), key=lambda x: self.fitness[x], reverse=False) #list of indexes ordered for increasing fitness value
        n_init_best=self.n_individual*self.init_best_perc # number of good solutions
        for i in range(0,n_init_best): #working on the n_init_best best solutions (lowest fitness)
            id=self.ordered_pop_indexs[i]
            sol=self.population[id] #individual
            fit_val= self.fitness[id] #original fitness value

            # Computing different CN's proposal for the solution
            for j in range(0,self.n_different_CN):
                # CN generation (nurse for room-shift couple)
                CN_new=np.array([[0]*self.h.n_rooms]*(self.h.n_shifts*self.h.n_days)) #[CN]ij, i=id_room, j=shift 0...D*3-1, el: id_nurse
                for s in range(0, self.h.n_shifts*self.h_n_days):
                    nurses_available=list(self.h.working_shifts[s].keys()) #working_shifts=list of dictionaries(one for shift) with key= nurse_id, value=max_load
                    #CN_new[s,:]= random.choices(nurses_available, k=self.h.n_rooms) #choosing 1 available nurse for each room in shift s
                    CN_new[s,:]= np.random.choice(nurses_available, size=self.h.n_rooms, replace=True) #choosing 1 available nurse for each room in shift
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
        #Updating the order of the n_init_best best solutions
        new_order_best=sorted(self.ordered_pop_indexs[:n_init_best], key=lambda x: self.fitness[x], reverse=False)
        self.ordered_pop_indexs[:n_init_best]=new_order_best
        best_id=self.ordered_pop_indexs[0] #index of smallest fitness --> equivalent to best_id=min(range(self.n_individual), key=lambda x: self.fitness[x])
        self.best_sol=self.population[best_id] #best individual seen so far
        self.best_fit= self.fitness[best_id] #fitness of best individual

    # SELECTION FUNCTION: selection of a couple of parents
    def selection(self,prob, worst_sol):
        # prob= probability vector. el= probability to pick the corresponding individual as a parent (based on fitness)
        # worst_sol= bool. If True choose parents from the second half of the solutions (ordered by fitness= worst half).
        # Note: worst_sol inserted to grant the explorative part of the algorithm (not stopping in a local minima...)
        if not worst_sol:
            #Choosing parents with categorical distribution (probability=prob) depending on fitness values
            id_p1=np.random.choice(list(range(self.n_individual)), p=prob)
            id_p2=np.random.choice(list(range(self.n_individual)), p=prob)
            p1=self.population[id_p1]
            p2=self.population[id_p2]
        else: #choosing from bad solutions
            n_worst=round(0.5*self.n_individual) #half the population
            unif_prob=[1/n_worst]*n_worst # uniform probability distribution over the worst half of the population
            id_p1=np.random.choice(self.ordered_pop_indexs[-n_worst:], p=unif_prob) #self.ordered_pop_indexs[-n_worst:]= list of indexes of the worst half of the solutions
            id_p2=np.random.choice(self.ordered_pop_indexs[-n_worst:], p=unif_prob)
            p1=self.population[id_p1]
            p2=self.population[id_p2]

        return (p1,p2)

    # CROSSOVER FUNCTION: generation of a couple of children with crossover from parents (p1,p2)
    def crossover(self,p1,p2,cross_perc_pat, cross_perc_CN):
        pat_split=round(self.h.n_patients * cross_perc_pat) #round= to always have an integer
        # Generating two children with opposite parts of the parents
        pr1= p1.pr[:pat_split]+p2.pr[pat_split:]
        pr2= p2.pr[:pat_split]+p1.pr[pat_split:]
        ad1= p1.ad[:pat_split]+p2.ad[pat_split:]
        ad2= p2.ad[:pat_split]+p1.ad[pat_split:]
        op1= p1.op[:pat_split]+p2.op[pat_split:]
        op2= p2.op[:pat_split]+p1.op[pat_split:]

        CN_split=round(self.h.n_days*self.h.n_shifts * cross_perc_CN) #round to always have an integer # split over total shifts
        CN1= np.array([[0]*self.h.n_rooms]*(self.h.n_shifts*self.h.n_days))
        CN1[:CN_split,:]=p1.CN[:CN_split,:]
        CN1[CN_split:,:]=p2.CN[CN_split:,:]
        CN2= np.array([[0]*self.h.n_rooms]*(self.h.n_shifts*self.h.n_days))
        CN2[:CN_split,:]=p2.CN[:CN_split,:]
        CN2[CN_split:,:]=p1.CN[CN_split:,:]

        c1=decisional_variables(pr1,ad1,op1,CN1)
        c2=decisional_variables(pr2,ad2,op2,CN2)

        return [c1,c2]

    # MUTATION FUNCTION: introduction of random mutations in the individual
    def mutation(self,ind):
        #Note: different possibilities to choose the number of elements changed in the mutation process
        # a: every attribute of decision variable has a fixed percentage of elements changed (can be different or constant for every attribute)
        # b: decided with probability distribution: gamma?? uniform??
        # Note: here we are changing every solution's attribute but we could focus just on some of them

        # IMPLEMENTATION PRESENTED HERE: percentage of elements changed for each attribute is drawn from a gamma distribution with fixed parameters
        # Every attribute mutates.
        # Gamma parameters: Gamma(1.5,9) mean=0.143, std=0.1

        #Note: mutation is done bewaring hard constraints (as done for the initial solutions): H2, H5, H6, nurses availability in the shift
        a_beta=1.5
        b_beta=9

        # AD MUTATION (admission date for patients)
        ad_mut_perc= np.random.beta(a_beta, b_beta, 1) #percentage of ad el to change
        ad_mut_n=round(ad_mut_perc*self.h.n_patients) # number of ad el to change
        ad_mut_ids=random.sample(list(range(0,self.h.n_patients)), k=ad_mut_n)
        for p_id in ad_mut_ids:
            if self.h.patients[p_id]["mandatory"]: #mandatory patient
                compatible_dates=list(range(self.h.patients[p_id]["surgery_release_day"],self.h.patients[p_id]["surgery_due_day"]+1)) #### H5, H6 ####
                ind.ad[p_id]=random.choice(compatible_dates)
            else: #optional patient
                compatible_dates=list(range(self.h.patients[p_id]["surgery_release_day"],self.h.n_days+1)) #### H6 #### (optional patient has no due date and can be postponed i.e. ad=n_days)
                ind.ad[p_id]=random.choice(compatible_dates)

        # PR MUTATION (rooms for patients)
        pr_mut_perc= np.random.beta(a_beta, b_beta, 1) #percentage of pr el to change
        pr_mut_n=round(pr_mut_perc*self.h.n_patients) # number of pr el to change
        pr_mut_ids=random.sample(list(range(0,self.h.n_patients)), k=pr_mut_n)
        room_set=set(range(0,self.h.n_rooms)) # list of rooms
        for p_id in pr_mut_ids:
            compatible_rooms=list(room_set-self.h.patients[p_id]["incompatible_room_ids"]) #### H2 compatible rooms ####
            ind.pr[p_id] = random.choice(compatible_rooms)

        # OP MUTATION (operating theaters for patients)
        op_mut_perc= np.random.beta(a_beta, b_beta, 1) #percentage of op el to change
        op_mut_n=round(op_mut_perc*self.h.n_patients) # number of op el to change
        op_mut_ids=random.sample(list(range(0,self.h.n_patients)), k=op_mut_n)
        op_theaters_list=list(range(0,self.h.n_op_theaters)) #list of operating theaters
        for p_id in op_mut_ids:
            ind.op[p_id]=random.choice(op_theaters_list)

        # CN MUTATION
        CN_mut_perc= np.random.beta(a_beta, b_beta, 1) #percentage of CN el to change
        CN_mut_n=round(CN_mut_perc*self.h.n_rooms*self.h.n_days*self.h.n_shifts) # number of CN el to change
        CN_mut_ids=random.sample(list(range(0,self.h.n_rooms*self.h.n_days*self.h.n_shifts)), k=CN_mut_n) #sampling numbers from self.h.n_rooms*self.h.n_days*self.h.n_shifts
        for id in CN_mut_ids:
            s=id//self.h.n_rooms #shift id
            r=id%self.h.n_rooms # room id
            nurses_available=list(self.h.working_shifts[s].keys()) #working_shifts=list of dictionaries(one for shift) with key= nurse_id, value=max_load
            #CN[s,:]= random.choices(nurses_available, k=self.h.n_rooms) #choosing 1 available nurse for each room in shift s
            ind.CN[s,r]= random.sample(nurses_available, k=1)

        return ind



    def solve(self):
        #INITIALIZATION
        self.initialization()

        n_gen=0
        elapsed_tot_time=0
        n_gen_no_improv=0
        max_gen_no_improv=round(self.frac_generation_no_improv*self.max_generation) #maximum number of generations without fitness improvement

        # Useful parameters for new individuals generation
        fit_selection_indiv=round(self.multinomial_select_perc*self.n_individual) # number of individuals in each generation which parents selection depends on fitness values
        #Note: self.n_individual-fit_selection_indiv= number of individuals in each generation which parents selection is among the worst half of the population
        n_min_feas=round(self.feasible_perc*self.n_individual) #miniminum number of feasible solutions for each generation
        n_max_no_feas=self.n_individual-n_min_feas #maximum number of NOT feasible solutions for each generation
        n_best_sol=self.n_individual*self.good_fitness_perc # number of good solutions in the population (which we want to compute other CNs for)

        start_time = time.time() #starting time
        while n_gen<self.max_generation and elapsed_tot_time<self.max_time and n_gen_no_improv<max_gen_no_improv: #stopping criteria: num generations, time, num gen without improvement
            ### New population generation ###
            # Note: we substitute the entire population!!
            new_population=[0]*self.n_individual # list with children (new individuals)
            new_fitness=[0]*self.n_individual # list with children's fitness values
            n_new=0
            n_new_no_feas=0
            # Note: we use the fitness inverse for the selection probability as we're minimizing the fitness function (higher prob for lower fitness)
            fit_inv=list(map(lambda x: 1 / x, self.fitness)) #ok because we never have fitness=0
            select_prob=fit_inv/sum(fit_inv) #normalizing the prob vector
            while n_new<self.n_individual:
                # SELECTION
                if n_new<fit_selection_indiv: #still picking parents according to fitness
                    worst_sol=False
                else: # parents chosen from the worst half
                    worst_sol=True
                (p1,p2)=self.selection(select_prob,worst_sol)
                # CROSSOVER
                # Note: we're using the same crossover percentage for splitting patient variables (PR,AD,OP) and CN. # We could differentiate the percentages
                children=self.crossover(p1,p2,self.cross_point_perc, self.cross_point_perc)
                # MUTATION
                mutate= np.random.binomial(1, self.mutation_prob, 2) # 1= mutate ci, 0=NOT mutate ci
                for c in range(0,2):
                    if mutate[c]==1:
                       children[c]= self.mutation(children[c])

                    # CHILDREN EVALUATION
                    # Note: Crossover and mutation done respecting H2, H5, H6, nurses availability in the shift on new elements
                    ##################à ??????? sol_new= children[c] #new proposed solution
                    sc_new = Scheduling(self.h, children[c])
                    sc_new.initial_condition() #setting initial conditions
                    sc_new.global_constr_check() #H5,H6 (already checked we can remove them) #S7, S8
                    sc_new.insert_new_exit() #exiting and entering patients
                    sc_new.SCP_constr_check() #H3,H4 (already checked we can remove them) #S5, S6
                    sc_new.PSA_NRA_constr_check() #H2 (already checked we can remove it) #H1,H7 #S1,S2,S3,S4
                    if sc_new.feasible: #children feasible
                        new_population[n_new]= children[c] # saving the individual in the new population
                        new_fitness[n_new]=sc_new.fitness() # saving the corresponding fitness value
                        n_new +=1
                        if n_new==self.n_individual: # new population completed (if there's still 1 child to consider we can ignore it)
                            break
                    else: #children NOT feasible
                        if n_new_no_feas<n_max_no_feas: #we can still add not feasible sol
                            new_population[n_new]= children[c] # saving the individual in the new population
                            new_fitness[n_new]= self.unfeasible_cost #saving fitness value REALLY BAD
                            n_new +=1
                            n_new_no_feas+=1
                            if n_new==self.n_individual: # new population completed (if there's still 1 child to consider we can ignore it)
                                break

            ########## Updating population (new generation) ###########

            self.population=new_population #updating the population
            self.fitness=new_fitness #updating fitness

            # Best individuals search : trying new CN's proposal for them (saving the best one) #
            self.ordered_pop_indexs=sorted(range(self.n_individual), key=lambda x: self.fitness[x], reverse=False) #list of indexes ordered for increasing fitness value

            for i in range(0,n_best_sol): #working on the n_best_sol best solutions (lowest fitness)
                id=self.ordered_pop_indexs[i]
                sol=self.population[id] #individual
                fit_val= self.fitness[id] #original fitness value

                ### Computing different CN's proposal for the solution ###
                for j in range(0,self.n_different_CN):
                    # CN generation (nurse for room-shift couple)
                    CN_new=np.array([[0]*self.h.n_rooms]*(self.h.n_shifts*self.h.n_days)) #[CN]ij, i=id_room, j=shift 0...D*3-1, el: id_nurse
                    for s in range(0, self.h.n_shifts*self.h_n_days):
                        nurses_available=list(self.h.working_shifts[s].keys()) #working_shifts=list of dictionaries(one for shift) with key= nurse_id, value=max_load
                        #CN_new[s,:]= random.choices(nurses_available, k=self.h.n_rooms) #choosing 1 available nurse for each room in shift s
                        CN_new[s,:]= np.random.choice(nurses_available, size=self.h.n_rooms, replace=True) #choosing 1 available nurse for each room in shift
                    # Evaluating fitness of the solution with CN_new
                    dv_new= decisional_variables(sol.pr,sol.ad,sol.op,CN_new) #new proposed solution
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

            # Updating Best individual #
            #Updating the order of the n_init_best best solutions
            new_order_best=sorted(self.ordered_pop_indexs[:n_best_sol], key=lambda x: self.fitness[x], reverse=False)
            self.ordered_pop_indexs[:n_best_sol]=new_order_best
            best_id=self.ordered_pop_indexs[0] #index of smallest fitness in the generation --> equivalent to best_id=min(range(self.n_individual), key=lambda x: self.fitness[x])
            if self.fitness[best_id]<self.best_fit: # the best solution in the generation improves the current best solution
                # Update current best
                self.best_sol=self.population[best_id] #best individual seen so far
                self.best_fit= self.fitness[best_id] #fitness of best individual
                n_gen_no_improv=0 #used by the stopping criterion on the max num of generations without improvement
            else:
                n_gen_no_improv+=1 #used by the stopping criterion on the max num of generations without improvement


            n_gen +=1
            end_time = time.time()
            elapsed_tot_time= end_time-start_time #time from process beginning

        return {"Optimal solution":self.best_sol, "Optimal fitness":self.best_fit }


