#caricare camere non compatibili come set con id numerici
#trasformare direttamente l'age group in numero: age_num=self.h.age_groups[self.h.occupants[id_occ]["age_group"]] #set initial room ages
#mettere in working shift come id il numero e non la stringa come codice infermiere
import numpy as np
import json

# Leggere il file JSON
with open('toy.json', 'r') as file:
    data = json.load(file)

n_days=data["days"]
skill_levels=data["skill_levels"]
### da modificare un attimo
shift_types=data["shift_types"]
age_groups=data["age_groups"]

n_nurses=len(data["nurses"])
nurses_skill_levels=[0]*n_nurses
for nurse in range(0,n_nurses):
    id_nurse=data["nurses"][nurse]["id"]
    pos=int(id_nurse[1:])
    nurses_skill_levels[pos]=data["nurses"][nurse]["skill_level"]

print(nurses_skill_levels )

'''
working_shifts=data["working_shifts"]
n_surgeons=len(data["surgeons"])
#surgeons_availability=data["surgeons_availability"]
n_op_theaters=len(data["operating_theaters"])
#op_theaters_availability=data["op_theaters_availability"]
n_rooms=len(data["rooms"])
#rooms_capacity=data["rooms_capacity"]
n_occupants=len(data["occupants"])
occupants=data["occupants"]
n_patients=len(data["patients"])
patients=data["patients"]
weights=data["weights"]
'''