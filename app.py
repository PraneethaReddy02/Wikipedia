# Uncomment and run these lines if the packages are not already installed:
!pip install wikipedia ipywidgets pandas matplotlib requests itables
!pip install itables

import wikipedia
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from urllib.parse import urlparse, unquote
import ipywidgets as widgets
from IPython.display import display, clear_output
from itables import show, init_notebook_mode

# Initialize itables for interactive tables in Colab
init_notebook_mode(all_interactive=True)

# --- Helper Functions ---

def extract_page_title(url):
    """
    Extracts the Wikipedia page title from a URL.
    Example: 'https://en.wikipedia.org/wiki/Python_(programming_language)'
    returns 'Python_(programming_language)'
    """
    parsed = urlparse(url)
    path = parsed.path  # e.g., "/wiki/Python_(programming_language)"
    if path.startswith("/wiki/"):
        title = path.split("/wiki/")[1]
        return unquote(title)
    else:
        return None

def fetch_pageviews(page_title, start_date, end_date):
    """
    Fetches daily pageview data from Wikimedia's REST API for a given page title.
    Dates must be datetime.date objects.
    Returns a DataFrame with columns 'date' and 'views'.
    """
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    api_url = (
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/all-agents/{page_title}/daily/{start_str}/{end_str}"
    )
    headers = {"User-Agent": "ColabApp/1.0 (example@example.com)"}
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data for {page_title}: HTTP {response.status_code}")
        return pd.DataFrame()
    
    data = response.json()
    records = []
    for item in data.get("items", []):
        # Extract date from timestamp (first 8 characters)
        date_str = item["timestamp"][:8]
        date_obj = datetime.strptime(date_str, "%Y%m%d").date()
        records.append({"date": date_obj, "views": item["views"]})
    return pd.DataFrame(records)

def analyze_wiki_pages(url1, url2, start_date, end_date):
    """
    Given two Wikipedia URLs and a date range, extracts page titles,
    fetches pageview data, simulates share counts, and returns a merged DataFrame.
    Also plots two time series charts for pageviews and shares.
    """
    page1_title = extract_page_title(url1)
    page2_title = extract_page_title(url2)
    
    if not page1_title or not page2_title:
        print("Error: Could not extract page title from one or both URLs.")
        return None
    
    print(f"\nFetching data for '{page1_title}' and '{page2_title}' ...")
    df1 = fetch_pageviews(page1_title, start_date, end_date)
    df2 = fetch_pageviews(page2_title, start_date, end_date)
    
    if df1.empty or df2.empty:
        print("No data available for one or both pages. Check your URLs or date range.")
        return None
    
    # Rename views columns to reflect each topic.
    df1 = df1.rename(columns={"views": f"views_{page1_title}"})
    df2 = df2.rename(columns={"views": f"views_{page2_title}"})
    
    # Merge the two DataFrames on the 'date' column.
    df_merged = pd.merge(df1, df2, on="date", how="outer").sort_values("date")
    
    # --- Simulate Share Counts ---
    # For demonstration, simulate share counts as 10% of pageviews plus some random noise.
    np.random.seed(42)  # For reproducibility
    df_merged[f"shares_{page1_title}"] = (df_merged[f"views_{page1_title}"] * 0.1 + 
                                          np.random.randint(0, 10, size=len(df_merged))).astype(int)
    df_merged[f"shares_{page2_title}"] = (df_merged[f"views_{page2_title}"] * 0.1 + 
                                          np.random.randint(0, 10, size=len(df_merged))).astype(int)
    
    # --- Plot Pageviews Chart ---
    plt.figure(figsize=(12, 6))
    plt.plot(df_merged["date"], df_merged[f"views_{page1_title}"], marker="o", label=page1_title)
    plt.plot(df_merged["date"], df_merged[f"views_{page2_title}"], marker="o", label=page2_title)
    plt.xlabel("Date")
    plt.ylabel("Pageviews")
    plt.title("Wikipedia Pageviews Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # --- Plot Shares Chart ---
    plt.figure(figsize=(12, 6))
    plt.plot(df_merged["date"], df_merged[f"shares_{page1_title}"], marker="o", label=f"Shares: {page1_title}")
    plt.plot(df_merged["date"], df_merged[f"shares_{page2_title}"], marker="o", label=f"Shares: {page2_title}")
    plt.xlabel("Date")
    plt.ylabel("Simulated Shares")
    plt.title("Simulated Share Counts Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    return df_merged

# --- Build the Interactive Widgets ---

url1_widget = widgets.Text(
    value="https://en.wikipedia.org/wiki/Python_(programming_language)",
    description="Wiki URL 1:",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='80%')
)
url2_widget = widgets.Text(
    value="https://en.wikipedia.org/wiki/Java_(programming_language)",
    description="Wiki URL 2:",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width='80%')
)
start_date_picker = widgets.DatePicker(
    description='Start Date:',
    value=datetime(2022, 1, 1).date(),
    disabled=False
)
end_date_picker = widgets.DatePicker(
    description='End Date:',
    value=datetime(2022, 1, 31).date(),
    disabled=False
)
run_button = widgets.Button(
    description="Run Analysis",
    button_style='success'
)
output_area = widgets.Output()

def on_run_button_clicked(b):
    with output_area:
        clear_output()
        # Retrieve widget values
        url1 = url1_widget.value.strip()
        url2 = url2_widget.value.strip()
        start_date = start_date_picker.value
        end_date = end_date_picker.value
        
        if not start_date or not end_date:
            print("Please select both start and end dates.")
            return
        
        print("Starting analysis...")
        df_result = analyze_wiki_pages(url1, url2, start_date, end_date)
        if df_result is not None:
            print("\nMerged DataFrame (Pageviews & Simulated Shares):")
            show(df_result)  # Display interactive DataFrame using itables

run_button.on_click(on_run_button_clicked)

# Display the interactive widgets.
display(url1_widget, url2_widget, start_date_picker, end_date_picker, run_button, output_area)
