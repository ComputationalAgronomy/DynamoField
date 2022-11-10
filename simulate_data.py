import string
import random
import itertools
import numpy
import pandas as pd

import csv
import pandas


ALPHABETS = list(string.ascii_uppercase)
# ALPHABETS.insert(0, 0)

trial_id_list = ["crop_yr1_t01", "crop_yr1_t02", "crop_yr1_t03", "crop_yr1_t04", 
                 "crop_yr2_t01", "crop_yr2_t02", "crop_yr2_t03", "crop_yr2_t04"]
trial_id_list = ["trial_2B", "trial_3C", "trial_4D"]

NROW = NTRT = 6  
NCOL = NBLOCK = 4  

"""
trial_id = trial_id_list[0]
nrow, ncol, ntrt, nblock = NROW, NCOL, NTRT, NBLOCK
"""


# def shuffled(l):
#     random.shuffle(l)
#     return l


def generate_design_rcbd(ntrt, nblock):
    row_list = [t + 1 for t in range(ntrt) for _ in range(nblock)]
    trt_list = [f"T{t}" for t in row_list]
    blocks = list(range(1, nblock + 1, 1))
    block_list = list()
    for _ in range(ntrt):
        random.shuffle(blocks)
        block_list.extend(blocks)
    design = pd.DataFrame({"treatment": trt_list,
                           "block": block_list,
                           "row": row_list,
                           "column": block_list})
    return design

def generate_design_cbd(ntrt, nrow, ncol):
    # TODO(SW): Implement this later
    nrep = int(nrow * ncol / ntrt)
    row_list = [t + 1 for t in range(ntrt) for _ in range(nrep)]
    trt_list = [f"T{t}" for t in row_list]
    design = itertools.product(range(1, nrow+1, 1), range(1, ncol+1, 1))
    column_list = []    
    random.shuffle(trt_list)
    design = pd.DataFrame({"treatment": trt_list,
                           "row": row_list,
                           "column": column_list})
    return design

# def generate_design_crd(trial_id, nrow, ncol, ntrt):



def simulate_one_trial(trial_id, nrow, ncol, ntrt):
    nrep = int(nrow * ncol / ntrt)
    trt_list =  ["T"+str(trt) for trt in range(1, ntrt+1, 1) for _ in range(nrep)]
    random.shuffle(trt_list)
    design = itertools.product(range(1, nrow+1, 1), range(1, ncol+1, 1))
    sim_data = [f"{trial_id},{d[0]},{d[1]},{t},{random.uniform(50, 100):.2f},{random.uniform(1, 10):.1f}\n" for d, t in zip(design, trt_list)]
    return sim_data


def simulate_yield_data_old(trial_id_list, nrow, ncol, ntrt, file_name):
    # list(itertools.product(range(1, 7, 1), range(1, 5, 1)))
    with open(file_name, "w") as f:
        sim_title = "trial_id,row,column,treatment,yields,meta\n"
        f.write(sim_title)
        for trial in trial_id_list:
            sim_data = simulate_one_trial(trial, nrow, ncol, ntrt)
            f.writelines(sim_data)



def simulate_yield_data(trial_id_list, ntrt, nblock, file_name):
    sim_data = dict() #pd.DataFrame()
    for trial_id in trial_id_list:
        design = generate_design_rcbd(ntrt, nblock)
        size = design.shape[0]
        design["trial_id"] = trial_id    
        results = pd.DataFrame({
            "yields": [round(random.uniform(50, 100),2) for _ in range(size)],
            "meta": [round(random.uniform(1, 10)) for _ in range(size)]
        })
        # design[['yields', 'meta']] = results
        sim_data[trial_id] = design.join(results)
        # sim_data = sim_data.concat(design)
    output = pd.concat(sim_data, ignore_index=True)
    output.to_csv(file_name)
    # design.assign(a=[random.uniform(50, 100) for _ in range(design.shape[0])], b=123)
    # design.apply(round, 1, "yields")

    # # list(itertools.product(range(1, 7, 1), range(1, 5, 1)))
    # with open(file_name, "w") as f:
    #     sim_title = "trial_id,row,column,treatment,yields,meta\n"
    #     f.write(sim_title)
    #     for trial in trial_id_list:
    #         sim_data = simulate_one_trial(trial, nrow, ncol, ntrt)
    #         f.writelines(sim_data)



def simulate_trt_data(trial_id_list, ntrt, file_name):
    sim_data = dict() #pd.DataFrame()
    trt_range = range(1, ntrt+1, 1)
    for trial_id in trial_id_list:
        info = pd.DataFrame({
            "treatment": [f"T{t}" for t in trt_range],
            "treatment_name": [f"trt_name_{ALPHABETS[t]}" for t in range(ntrt)],
        })
        info["trial_id"] = trial_id    
        info["seed_type"] = "seed_type_A"
        sim_data[trial_id] = info
    output = pd.concat(sim_data, ignore_index=True)
    output.to_csv(file_name)


def simulate_trial_field_data(trial_id_list, file_name):
    # sim_data = dict() #pd.DataFrame()
    # trt_range = range(1, ntrt+1, 1)
    info = pd.DataFrame({
        "trial_id": trial_id_list,
        "pH": [round(random.uniform(5, 9), 1) for _ in trial_id_list],
        "Location": [f"Loc_{ALPHABETS[t]}" for t, _ in enumerate(trial_id_list)],
        "irrigation": [True if t % 2 == 0 else False for t, _ in enumerate(trial_id_list)]
    })
    # info["soil_type"] = "sandy"
    #     info["seed_type"] = "seed_type_A"
    #     sim_data[trial_id] = info
    # output = pd.concat(sim_data, ignore_index=True)
    info.to_csv(file_name)

    # with open(file_name, "w") as f:
    #     sim_title = "trial_id,location,soil_type,soil_ph,irrigation\n"
    #     f.write(sim_title)
    #     for index, trial in enumerate(trial_id_list):
    #         sim_data = f"{trial},Loc_{index},sandy,{random.uniform(5, 9):.1f},Yes\n"
    #         f.writelines(sim_data)


def simulate_management_data(trial_id_list, file_name):
    info = pd.DataFrame({
        "trial_id": trial_id_list,
        "pH": [round(random.uniform(5, 9), 1) for _ in trial_id_list],
        "Location": [f"Loc_{ALPHABETS[t]}" for t, _ in enumerate(trial_id_list)],
        "irrigation": [True if t % 2 == 0 else False for t, _ in enumerate(trial_id_list)]
    })
    with open(file_name, "w") as f:
        sim_title = "trial_id,fertilizer,type,amount,solid_or_powder\n"
        f.write(sim_title)
        sim_data = [None]*4
        for index, trial in enumerate(trial_id_list):
            sim_data[0] = f"{trial},N,NPK_1,{random.uniform(10, 50):.1f},solid\n"
            sim_data[1] = f"{trial},N,NPK_2,{random.uniform(10, 50):.1f},powder\n"
            sim_data[2] = f"{trial},P,,{random.uniform(10, 50):.1f},solid\n"
            sim_data[3] = f"{trial},P,,{random.uniform(10, 50):.1f},solid\n"
            f.writelines(sim_data)



def generate_random_phone():
    return f"{random.uniform(100, 900):.0f}-{random.uniform(100, 900):.0f}-{random.uniform(100, 900):.0f}"


def simulate_trial_contact(trial_id_list, file_name):
    info = pd.DataFrame({
        "trial_id": trial_id_list,
        "person": ["John" if t % 2 == 0 else "Jane" for t, _ in enumerate(trial_id_list)],
        "phone": [generate_random_phone() for t, _ in enumerate(trial_id_list)]
    })
    with open(file_name, "w") as f:
        sim_title = "trial_id,person,phone\n"
        f.write(sim_title)
        for index, trial in enumerate(trial_id_list):
            phone = 
            sim_data = f"{trial},John,{phone}\n"
            f.writelines(sim_data)



# file_name = f"temp_yield.csv"

# simulate_yield_data_old(trial_id_list, NROW, NCOL, NTRT, file_name="temp_plot.csv")

simulate_yield_data(trial_id_list, NTRT, NBLOCK, file_name="temp_plot.csv")
simulate_trt_data(trial_id_list, NTRT, file_name="temp_trt.csv")

simulate_trial_field_data(trial_id_list, file_name="temp_trial_meta.csv")
simulate_trial_contact(trial_id_list, file_name="temp_trial_contact.csv")

simulate_management_data(trial_id_list, file_name="temp_trial_management.csv")
