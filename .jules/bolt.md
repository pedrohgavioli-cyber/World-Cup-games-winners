## 2024-06-18 - Caching in Streamlit
**Learning:** Streamlit re-runs the entire script on every user interaction (like clicking a button or changing an input). This causes any external data fetching (like reading a large CSV or hitting an external API) to run repeatedly, blocking the main thread and slowing down the UI significantly.
**Action:** Always wrap data fetching functions (DB calls, API requests, CSV loading) in Streamlit apps with `@st.cache_data`. Use `ttl` for data that changes (like odds) and no ttl for static data (like historical results).
