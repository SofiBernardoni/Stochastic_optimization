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
        occupants[i]["age_group"]=age_groups[occupants[i]["age_group"]] #storing it as a number
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
    print(f"ci sono {n_occupants} occupants, {n_patients} pazienti, {n_rooms} stanze, {n_op_theaters} sale operatorie, {n_surgeons} chirurghi, {n_nurses} infermiere, {n_days} giorni")
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


    # Dictonary with hospital data stored correctly
    h_data={ 'n_days':n_days,
             'skill_levels': skill_levels,
             "shift_types": shift_types,
             "age_groups":age_groups,
             "n_nurses": n_nurses,
             "nurses_skill_levels": nurses_skill_levels,
             "working_shifts": working_shifts,
             "n_surgeons": n_surgeons,
             "surgeons_availability": surgeons_availability,
             "n_op_theaters": n_op_theaters,
             "op_theaters_availability": op_theaters_availability,
             "n_rooms": n_rooms,
             "rooms_capacity": rooms_capacity,
             "n_occupants": n_occupants,
             "occupants": occupants,
             "n_patients": n_patients,
             "patients": patients,
             "weights": weights }

    print(f' DATA UPLOADED')

    return h_data
