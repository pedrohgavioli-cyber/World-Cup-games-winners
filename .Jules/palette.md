## 2024-06-18 - Improve Loading State Feedback
**Learning:** Static `st.write()` messages used to indicate data fetching operations in Streamlit can feel unresponsive or stuck since they offer no active visual indication that work is being done.
**Action:** Use Streamlit's `st.spinner()` context manager to wrap long-running operations. This provides a clean, built-in animated spinner that signals to the user the app is actively processing data, improving the perceived performance and UX.
