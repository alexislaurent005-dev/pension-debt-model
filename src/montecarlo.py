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

if __name__ == "__main__":
    random.seed(42)  # Set a seed for reproducibility
    simulations = 1000
    average_inflation = params.INFLATION_RATE
    average_productivity = params.PRODUCTIVITY_GROWTH
    inflation_std_dev = 0.01
    productivity_std_dev = 0.01

    inflation_paths, productivity_paths = generate_random_paths(params.FIRST_YEAR, params.FINAL_YEAR, simulations, average_inflation, average_productivity, inflation_std_dev, productivity_std_dev)

    print(inflation_paths[0][:5])  # Print the first 5 values of the first generated inflation path
    print(productivity_paths[0][:5])  # Print the first 5 values of the first generated productivity path
    print(sum(inflation_paths[0]) / len(inflation_paths[0]))  # Print the average of the first generated inflation path
    print(sum(productivity_paths[0]) / len(productivity_paths[0]))  # Print the average of the first generated productivity path


    results = []
    results_mt = []

    for i in range(simulations):

        inflation_path = inflation_paths[i]
        productivity_path = productivity_paths[i]
        years, pension_shares, debts = debt_projection(inflation=inflation_path, productivity_growth=productivity_path, taper_rate=0)
        years_mt, pension_shares_mt, debts_mt = debt_projection(inflation=inflation_path, productivity_growth=productivity_path)
        results.append(debts[-1])  # Store the final debt to GDP ratio for this simulation
        results_mt.append(debts_mt[-1])  # Store the final debt to GDP ratio for this simulation with means testing
       
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
    
    plt.hist(sorted_results, bins=30, alpha=0.5, label='Triple Lock')
    plt.hist(sorted_results_mt, bins=30, alpha=0.5, label='Means Test')
    plt.title('Distribution of Final Debt to GDP Ratios')
    plt.xlabel('Final Debt to GDP Ratio')
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()

    print(len(results))
    print(len(results_mt))
    print("Average final debt to GDP ratio (Triple Lock):", sum(results) / len(results))
    print("Average final debt to GDP ratio (Means Test):", sum(results_mt) / len(results_mt))