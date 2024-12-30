#caricare tutti gli id come numeri (controllare che le funzioni in scheduling lavorino direttamente con il numero e non con la stringa come id)
import numpy as np
import json

def upload_data(file_name):
    # Read JSON (file_name= string)
    with open(file_name, 'r') as file:
        data = json.load(file)


    #general infos
    n_days=data["days"]
    skill_levels=data["skill_levels"]

    # dictionary of shifts
    shift=data["shift_types"]
    n_shifts=len(shift) #automatically computed by constructor
    shift_types={}
    i=0
    for k in shift:
        shift_types[k]=i
        i+=1

    # dictionary of age groups
    age=data["age_groups"]
    #n_age=len(age) #automatically computed by constructor
    age_groups={}
    j=0
    for k in age:
        age_groups[k]=j
        j+=1

    #nurses' info
    n_nurses=len(data["nurses"])
    nurses_skill_levels=[0]*n_nurses
    for nurse in range(0,n_nurses):
        id_nurse=data["nurses"][nurse]["id"]
        pos=int(id_nurse[1:])
        nurses_skill_levels[pos]=data["nurses"][nurse]["skill_level"]

    working_shifts=[{}]*(n_days*n_shifts)

    for t in data["nurses"]: #t è un dizionario, data["nurse"] è una lista di dizionari
        id_nurse=int(t["id"][1:])
        for p in t["working_shifts"]: #t["working_shifts"]:lista di dizionari
            day=p["day"]
            shift=p["shift"]
            m=shift_types[shift]
            max_load=p["max_load"]
            working_shifts[(n_shifts*day)+m][id_nurse]=max_load

    #print(working_shifts)

    #surgeons
    n_surgeons=len(data["surgeons"])
    surgeons_availability=np.zeros((n_days, n_surgeons), dtype=int)
    #surgeons_availability=np.array([[[0]*n_surgeons]*n_days])
    for su in data["surgeons"]:
        id_surgeon=int(su["id"][1:])
        surgeons_availability[:, id_surgeon]=su["max_surgery_time"]
    #print(surgeons_availability)


    #operating theater
    n_op_theaters=len(data["operating_theaters"])
    op_theaters_availability=np.zeros((n_days, n_op_theaters), dtype=int)
    for op in data["operating_theaters"]:
        id_op=int(op["id"][1:])
        op_theaters_availability[:, id_op]=op["availability"]
    #print(op_theaters_availability)

    #room
    n_rooms=len(data["rooms"])
    rooms_capacity=[0]*n_rooms
    for r in data["rooms"]:
        id=int(r["id"][1:])
        rooms_capacity[id]=data["rooms"][id]["capacity"]

    #occupants
    n_occupants=len(data["occupants"])
    occupants=data["occupants"]
    for i in range(0, n_occupants):
        del occupants[i]["id"]
        occupants[i]["room_id"] = int(occupants[i]["room_id"][1:])
    #patients
    n_patients=len(data["patients"])
    patients=data["patients"]

    #n_optional=0 ######### TOGLI SE METTI COSTO IN hospital ########
    for i in range(0, n_patients):
        del patients[i]["id"]
        patients[i]["surgeon_id"] = int(patients[i]["surgeon_id"][1:])
        patients[i]["age_group"]=age_groups[patients[i]["age_group"]] #storing it as a number
        incomp_rooms=set()
        for l in range(0, len(patients[i]["incompatible_room_ids"])):
            incomp_rooms.add(int(patients[i]["incompatible_room_ids"][l][1:]))
        patients[i]["incompatible_room_ids"]=incomp_rooms # set of room ids
        #if not patients[i]["mandatory"]: ######### TOGLI SE METTI COSTO IN hospital ########
            #n_optional+=1

    #weights
    weights=data["weights"]

    '''
    ######### TOGLI SE METTI COSTO IN hospital ########
    unfeasible_cost = n_days*(n_rooms*n_age*weights["room_mixed_age"]+ n_op_theaters* weights["open_operating_theater"]+n_patients*weights["patient_delay"]+ n_op_theaters*n_surgeons*weights["surgeon_transfer"]+
                            n_rooms*n_shifts*max(nurses_skill_levels)*weights["room_nurse_skill"] + n_nurses*weights["nurse_eccessive_workload"]) + n_patients*n_nurses*weights["continuity_of_care"] +n_optional*weights["unscheduled_optional"]
    print("unscheduled: " , n_optional*weights["unscheduled_optional"])
    print("unfeasible solution: ", unfeasible_cost)
    ######### TOGLI SE METTI COSTO IN hospital ########
    '''
    h_data={} #dictonary with hospital data stored correctly

    h_data["n_days"]=n_days
    h_data["skill_levels"]=skill_levels
    h_data["shift_types"]=shift_types
    h_data["age_groups"]=age_groups
    h_data["n_nurses"]=n_nurses
    h_data["nurses_skill_levels"]=nurses_skill_levels
    h_data["working_shifts"]=working_shifts
    h_data["n_surgeons"]=n_surgeons
    h_data["surgeons_availability"]=surgeons_availability
    h_data["n_op_theaters"]=n_op_theaters
    h_data["op_theaters_availability"]=op_theaters_availability
    h_data["n_rooms"]=n_rooms
    h_data["rooms_capacity"]=rooms_capacity
    h_data["n_occupants"]=n_occupants
    h_data["occupants"]=occupants
    h_data["n_patients"]=n_patients
    h_data["patients"]=patients
    h_data["weights"]=weights

    return h_data
