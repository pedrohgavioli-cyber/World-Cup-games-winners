
## 2024-06-18 - Caching in Streamlit Applications
**Learning:** Streamlit re-runs the entire script from top to bottom every time an interaction occurs. This means expensive network calls and data processing, if left uncached, severely hinder application responsiveness.
**Action:** Always wrap heavy data loading functions (`pd.read_csv` or API calls via `requests`) using `@st.cache_data`. For APIs, remember to add a `ttl` to prevent stale data while avoiding API rate limits.
