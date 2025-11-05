import streamlit as st
import pandas as pd
import csv
from jobspy import scrape_jobs
from io import StringIO

st.set_page_config(page_title="JobSpy Scraper", page_icon="💼", layout="wide")

st.title("💼 JobSpy Multi-Site Job Scraper")
st.caption("Scrape jobs from LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter, and more — all in one place.")

# --- Sidebar Configuration ---
st.sidebar.header("🔧 Search Configuration")

# Search inputs
search_term = st.sidebar.text_input("Search Term", "Software Engineer")
google_search_term = st.sidebar.text_input("Google Search Term (for Google Jobs)", 
                                           "software engineer jobs near San Francisco, CA since yesterday")
location = st.sidebar.text_input("Location", "San Francisco, CA")
country_indeed = st.sidebar.text_input("Country (for Indeed/Glassdoor)", "USA")

# Numeric parameters
results_wanted = st.sidebar.number_input("Results Wanted", 1, 1000, 20)
hours_old = st.sidebar.number_input("Hours Old (filter by posting age)", 1, 168, 72)
distance = st.sidebar.number_input("Distance (miles)", 0, 200, 50)
offset = st.sidebar.number_input("Offset (start from nth result)", 0, 1000, 0)

# Job filters
job_type = st.sidebar.selectbox("Job Type", ["", "fulltime", "parttime", "internship", "contract"])
is_remote = st.sidebar.selectbox("Remote?", ["", True, False])
easy_apply = st.sidebar.selectbox("Easy Apply (LinkedIn/Indeed)", ["", True, False])

# Job boards
site_name = st.sidebar.multiselect(
    "Select Job Sites",
    ["indeed", "linkedin", "zip_recruiter", "google", "glassdoor", "bayt", "naukri", "bdjobs"],
    default=["indeed", "linkedin", "zip_recruiter", "google"]
)

# Other options
linkedin_fetch_description = st.sidebar.checkbox("Fetch full LinkedIn Descriptions (slower)", value=False)
enforce_annual_salary = st.sidebar.checkbox("Convert wages to annual salary", value=False)
verbose = st.sidebar.selectbox("Verbosity Level", [0, 1, 2], index=2)

# --- Action Button ---
if st.sidebar.button("🚀 Scrape Jobs Now"):
    with st.spinner("Scraping jobs across selected sites... ⏳"):
        try:
            # Prepare kwargs dynamically (only include non-empty values)
            params = {
                "site_name": site_name,
                "search_term": search_term,
                "google_search_term": google_search_term,
                "location": location,
                "country_indeed": country_indeed,
                "results_wanted": results_wanted,
                "hours_old": hours_old,
                "distance": distance,
                "offset": offset,
                "verbose": verbose,
                "enforce_annual_salary": enforce_annual_salary,
                "linkedin_fetch_description": linkedin_fetch_description,
            }
            # Optional filters
            if job_type:
                params["job_type"] = job_type
            if is_remote != "":
                params["is_remote"] = is_remote
            if easy_apply != "":
                params["easy_apply"] = easy_apply

            # Scrape jobs
            jobs = scrape_jobs(**params)

            if jobs.empty:
                st.warning("No jobs found. Try adjusting your filters.")
            else:
                st.success(f"✅ Found {len(jobs)} jobs!")
                st.dataframe(jobs, use_container_width=True)

                # CSV Download
                csv_buffer = StringIO()
                jobs.to_csv(csv_buffer, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name="jobspy_results.csv",
                    mime="text/csv"
                )

                # Summary stats
                with st.expander("📊 Summary Insights"):
                    st.write(f"**Unique Companies:** {jobs['company'].nunique()}")
                    st.write(f"**Top Locations:**")
                    st.write(jobs['city'].value_counts().head(10))

        except Exception as e:
            st.error(f" Error: {e}")
else:
    st.info(" Configure your job search on the left and click **Scrape Jobs Now** to begin!")

# --- Footer ---
st.markdown("---")
st.caption("Built with  using [Streamlit](https://streamlit.io) and [JobSpy](https://github.com/JacobBumgarner/JobSpy)")
