import statistics

cpi = [
    0.031,   # 2011/12
    0.052,   # 2012/13
    0.022,   # 2013/14
    0.027,   # 2014/15
    0.012,   # 2015/16
    -0.001,  # 2016/17
    0.010,   # 2017/18
    0.030,   # 2018/19
    0.024,   # 2019/20
    0.017,   # 2020/21
    0.005,   # 2021/22
    0.031,   # 2022/23
    0.101,   # 2023/24
    0.067,   # 2024/25
    0.017,   # 2025/26
    0.038,   # 2026/27
]

earnings = [
    0.013,   # 2011/12
    0.028,   # 2012/13
    0.016,   # 2013/14
    0.012,   # 2014/15
    0.006,   # 2015/16
    0.029,   # 2016/17
    0.024,   # 2017/18
    0.022,   # 2018/19
    0.026,   # 2019/20
    0.039,   # 2020/21
    -0.009,  # 2021/22 (pandemic)
    0.084,   # 2022/23 (pandemic)
    0.054,   # 2023/24
    0.085,   # 2024/25
    0.041,   # 2025/26
    0.048,   # 2026/27
]

productivity_series = [earnings[i] - cpi[i] for i in range(len(cpi))]
productivity_std_dev = statistics.stdev(productivity_series)
inflation_std_dev = statistics.stdev(cpi)
print("Productivity Standard Deviation:", productivity_std_dev)
print("Inflation Standard Deviation:", inflation_std_dev)
print(statistics.correlation(cpi, productivity_series))

cpi_excl = cpi[:10] + cpi[12:]
productivity_excl = productivity_series[:10] + productivity_series[12:]
print("Productivity Standard Deviation (excluding pandemic):", statistics.stdev(productivity_excl))
print("Inflation Standard Deviation (excluding pandemic):", statistics.stdev(cpi_excl))
print("Correlation (excluding pandemic):", statistics.correlation(cpi_excl, productivity_excl))