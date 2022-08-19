import random
import itertools


def simulate_yield_data(nrow, ncol, file_name):
    # list(itertools.product(range(1, 7, 1), range(1, 5, 1)))
    design = itertools.product(range(1, nrow+1, 1), range(1, ncol+1, 1))
    sim_data = [f"{d[0]},{d[1]},{random.uniform(50, 100):.2f}\n" for d in design]
    sim_title = "row,column,yield\n"

    with open(file_name, "w") as f:
        f.write(sim_title)
        # for l in sim_data:
        f.writelines(sim_data)



with open(file_name, "r") as f:
    title = f.readline().strip().split(",")
    print(title)
    for l in f.readlines():
        print(l.strip())
        



trial_id = "trial_2B"
file_name = f"example_{trial_id}_yield.csv"
nrow = 6
ncol = 4

simulate_yield_data(nrow, ncol, file_name)
