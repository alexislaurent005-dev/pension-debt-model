import random
import matplotlib.pyplot as plt
from src import params
from src.simulation import debt_projection


def generate_random_paths(first_year, last_year, simulations, average_inflation, average_productivity, inflation_std_dev, productivity_std_dev):
    inflation_paths = []
    productivity_paths = []
    for _ in range(simulations):
        inflation_path = [random.gauss(average_inflation, inflation_std_dev) for _ in range(first_year, last_year + 1)]
        productivity_path = [random.gauss(average_productivity, productivity_std_dev) for _ in range(first_year, last_year + 1)]
        inflation_paths.append(inflation_path)
        productivity_paths.append(productivity_path)
    return inflation_paths, productivity_paths

def run_montecarlo (simulations, average_inflation, average_productivity, inflation_std_dev, productivity_std_dev,
                    uprating_rule="triple_lock", reform_year=None, threshold_uprating="pension"):
    random.seed(42)
    inflation_paths, productivity_paths = generate_random_paths(params.FIRST_YEAR, params.FINAL_YEAR, simulations, average_inflation, average_productivity, inflation_std_dev, productivity_std_dev)


    results = []
    results_mt = []

    for i in range(simulations):

        inflation_path = inflation_paths[i]
        productivity_path = productivity_paths[i]
        years, pension_shares, debts = debt_projection(inflation=inflation_path, productivity_growth=productivity_path, taper_rate=0,
                                                        uprating_rule=uprating_rule, reform_year=reform_year, threshold_uprating=threshold_uprating)
        years_mt, pension_shares_mt, debts_mt = debt_projection(inflation=inflation_path, productivity_growth=productivity_path,
                                                                 uprating_rule=uprating_rule, reform_year=reform_year, threshold_uprating=threshold_uprating)
        results.append(debts[-1])  # Store the final debt to GDP ratio for this simulation
        results_mt.append(debts_mt[-1])  # Store the final debt to GDP ratio for this simulation with means testing
    

    return results, results_mt

if __name__ == "__main__": 
    results, results_mt = run_montecarlo(1000, params.INFLATION_RATE, params.PRODUCTIVITY_GROWTH, params.INFLATION_STD_DEV, params.PRODUCTIVITY_STD_DEV)
    results_excl, results_mt_excl = run_montecarlo(1000, params.INFLATION_RATE, params.PRODUCTIVITY_GROWTH, params.INFLATION_STD_DEV_EXCL, params.PRODUCTIVITY_STD_DEV_EXCL)

    sorted_results = sorted(results)
    sorted_results_mt = sorted(results_mt)
    position_5th_percentile = int(0.05 * len(sorted_results))
    position_95th_percentile = int(0.95 * len(sorted_results))
    position_5th_percentile_mt = int(0.05 * len(sorted_results_mt))
    position_95th_percentile_mt = int(0.95 * len(sorted_results_mt))
    position_50th_percentile = int(0.5 * len(sorted_results))
    position_50th_percentile_mt = int(0.5 * len(sorted_results_mt))

    print("5th percentile (Triple Lock):", sorted_results[position_5th_percentile])
    print("95th percentile (Triple Lock):", sorted_results[position_95th_percentile])
    print("50th percentile (Triple Lock):", sorted_results[position_50th_percentile])
    print("5th percentile (Means Test):", sorted_results_mt[position_5th_percentile_mt])
    print("95th percentile (Means Test):", sorted_results_mt[position_95th_percentile_mt])
    print("50th percentile (Means Test):", sorted_results_mt[position_50th_percentile_mt]) 

    sorted_results_excl = sorted(results_excl)
    sorted_results_mt_excl = sorted(results_mt_excl)
 
    print("5th percentile (Triple Lock, excl. pandemic):", sorted_results_excl[position_5th_percentile])
    print("95th percentile (Triple Lock, excl. pandemic):", sorted_results_excl[position_95th_percentile])
    print("50th percentile (Triple Lock, excl. pandemic):", sorted_results_excl[position_50th_percentile])
    print("5th percentile (Means Test, excl. pandemic):", sorted_results_mt_excl[position_5th_percentile_mt])
    print("95th percentile (Means Test, excl. pandemic):", sorted_results_mt_excl[position_95th_percentile_mt])
    print("50th percentile (Means Test, excl. pandemic):", sorted_results_mt_excl[position_50th_percentile_mt]) 
    print("Average final debt to GDP ratio (Triple Lock, excl. pandemic):", sum(results_excl) / len(results_excl))
    print("Average final debt to GDP ratio (Means Test, excl. pandemic):", sum(results_mt_excl) / len(results_mt_excl))
    

    # Uprating reforms from April 2030 under the same 1,000 futures (findings section 6)
    for rule in ["smoothed_earnings", "earnings", "double_lock"]:
        results_r, results_mt_r = run_montecarlo(1000, params.INFLATION_RATE, params.PRODUCTIVITY_GROWTH, params.INFLATION_STD_DEV, params.PRODUCTIVITY_STD_DEV,
                                                 uprating_rule=rule, reform_year=2030)
        sorted_r = sorted(results_r)
        sorted_mt_r = sorted(results_mt_r)
        print(f"Median ({rule} from 2030, universal):", sorted_r[position_50th_percentile])
        print(f"Median ({rule} from 2030, means test):", sorted_mt_r[position_50th_percentile_mt])

    plt.hist(sorted_results, bins=30, alpha=0.5, label='Triple Lock')
    plt.hist(sorted_results_mt, bins=30, alpha=0.5, label='Means Test')
    plt.title('Distribution of Final Debt to GDP Ratios')
    plt.xlabel('Final Debt to GDP Ratio')
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()
