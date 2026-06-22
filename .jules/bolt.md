## 2024-06-22 - Optimize Pandas groupby.apply()

**Learning:** `pandas.groupby().apply(lambda x: pd.Series(...))` is a significant performance bottleneck because it evaluates the lambda function iteratively for each group in pure Python.
**Action:** When performing aggregate calculations over pandas DataFrames, always prioritize vectorized operations (creating new columns before grouping) combined with `groupby().agg()` using named aggregations. This leverages optimized C code and drastically reduces execution time.
