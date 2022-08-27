import random
import itertools
import numpy

import csv
import pandas


trial_id_list = ["trial_2B", "trial_3C", "trial_4D"]
file_name = f"temp_yield.csv"
nrow = 6
ncol = 4
ntrt  = 6


def simulate_one_trial(trial_id, nrow, ncol, ntrt):
    nrep = int(nrow * ncol / ntrt )
    trt_list =  [ "T"+str(trt) for trt in range(1, ntrt+1, 1) for _ in range(nrep)]
    random.shuffle(trt_list)
    design = itertools.product(range(1, nrow+1, 1), range(1, ncol+1, 1))
    sim_data = [f"{trial_id},{d[0]},{d[1]},{t},{random.uniform(50, 100):.2f},{random.uniform(1, 10):.1f}\n" for d, t in zip(design, trt_list)]
    return(sim_data)


def simulate_yield_data(trial_id_list, nrow, ncol, ntrt, file_name):
    # list(itertools.product(range(1, 7, 1), range(1, 5, 1)))
    with open(file_name, "w") as f:
        sim_title = "trial_id,row,column,treatment,yield,meta\n"
        f.write(sim_title)
        for trial in trial_id_list:
            sim_data = simulate_one_trial(trial, nrow, ncol, ntrt)
            f.writelines(sim_data)


def simulate_trt_data(trial_id_list, ntrt, file_name):
    with open(file_name, "w") as f:
        sim_title = "trial_id,trt_number,treatment,seed\n"
        f.write(sim_title)
        for trial in trial_id_list:
            sim_data = [f"{trial},T{t},trt_{t}X,seed_type_A\n" for t in range(1, ntrt+1, 1)]
            f.writelines(sim_data)



def simulate_trial_field_data(trial_id_list, file_name):
    with open(file_name, "w") as f:
        sim_title = "trial_id,location,soil_type,soil_ph,irrigation\n"
        f.write(sim_title)
        for index, trial in enumerate(trial_id_list):
            sim_data = f"{trial},Loc_{index},sandy,{random.uniform(5, 9):.1f}Yes\n"
            f.writelines(sim_data)




def simulate_trial_contact(trial_id_list, file_name):
    with open(file_name, "w") as f:
        sim_title = "trial_id,person,phone\n"
        f.write(sim_title)
        for index, trial in enumerate(trial_id_list):
            phone = f"{int(random.uniform(100, 900))}-{int(random.uniform(100, 900))}-{int(random.uniform(100, 900))}"
            sim_data = f"{trial},John,{phone}\n"
            f.writelines(sim_data)




simulate_yield_data(trial_id_list, nrow, ncol, ntrt, file_name)
simulate_trt_data(trial_id_list, ntrt, "temp_trt.csv")

simulate_trial_field_data(trial_id_list, "temp_trial_meta.csv")
simulate_trial_contact(trial_id_list, "temp_trial_contact.csv")

