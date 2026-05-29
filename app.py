import os
import re
import base64
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from scraper import scrape_from_url


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Ecommerce Competitor Intelligence Dashboard",
    layout="wide"
)

CSV_FILE = "products.csv"


# ============================================================
# FONT + DESIGN FUNCTIONS
# ============================================================

def load_font_base64(font_path):
    """Load a local font file and convert it to base64 for CSS."""
    path = Path(font_path)

    if path.exists():
        with open(path, "rb") as font_file:
            return base64.b64encode(font_file.read()).decode()

    return None


def inject_custom_css():
    """
    Required local font files:
    assets/ArchimotoV01.ttf
    assets/GoogleSans-Regular.ttf
    """

    archimoto_font = load_font_base64("assets/ArchimotoV01.ttf")
    google_sans_font = load_font_base64("assets/GoogleSans-Regular.ttf")

    archimoto_css = ""
    google_sans_css = ""

    if archimoto_font:
        archimoto_css = f"""
        @font-face {{
            font-family: 'ArchimotoV01';
            src: url(data:font/truetype;charset=utf-8;base64,{archimoto_font}) format('truetype');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}
        """

    if google_sans_font:
        google_sans_css = f"""
        @font-face {{
            font-family: 'GoogleSansCustom';
            src: url(data:font/truetype;charset=utf-8;base64,{google_sans_font}) format('truetype');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}
        """

    st.markdown(
        f"""
        <style>
        {archimoto_css}
        {google_sans_css}

        :root {{
            --bg-main: #050816;
            --bg-panel: rgba(15, 23, 42, 0.88);
            --border-soft: rgba(148, 163, 184, 0.20);
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --accent-cyan: #22D3EE;
            --accent-blue: #3B82F6;
            --accent-violet: #8B5CF6;
            --accent-green: #10B981;
        }}

        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(34, 211, 238, 0.12), transparent 32%),
                radial-gradient(circle at top right, rgba(139, 92, 246, 0.15), transparent 32%),
                linear-gradient(135deg, #050816 0%, #0B1120 45%, #020617 100%);
            color: var(--text-main);
        }}

        .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 3rem;
            max-width: 1450px;
            font-family: 'GoogleSansCustom', 'Inter', 'Segoe UI', Arial, sans-serif;
        }}

        section[data-testid="stSidebar"] {{
            min-width: 340px !important;
            max-width: 340px !important;
            width: 340px !important;
            background:
                linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 0.98));
            border-right: 1px solid var(--border-soft);
        }}

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea {{
            font-family: 'GoogleSansCustom', 'Inter', 'Segoe UI', Arial, sans-serif !important;
        }}

        div[role="radiogroup"] label {{
            white-space: nowrap !important;
        }}

        span[data-testid="stIconMaterial"],
        .material-icons,
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-symbols-sharp {{
            font-family: "Material Symbols Rounded", "Material Icons" !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 20px !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-feature-settings: "liga" !important;
            font-feature-settings: "liga" !important;
            -webkit-font-smoothing: antialiased !important;
        }}

        .hero-title-wrap {{
            position: relative;
            padding: 32px 36px;
            margin-bottom: 28px;
            border: 1px solid rgba(34, 211, 238, 0.25);
            border-radius: 26px;
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.58)),
                radial-gradient(circle at top right, rgba(34, 211, 238, 0.16), transparent 36%),
                radial-gradient(circle at bottom left, rgba(139, 92, 246, 0.16), transparent 32%);
            box-shadow:
                0 28px 85px rgba(0, 0, 0, 0.38),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            overflow: hidden;
            animation: heroReveal 900ms ease-out both;
        }}

        .hero-title-wrap::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                120deg,
                transparent 0%,
                rgba(255, 255, 255, 0.10) 18%,
                transparent 36%
            );
            transform: translateX(-120%);
            animation: shineSweep 4s ease-in-out infinite;
        }}

        .hero-kicker {{
            position: relative;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            color: var(--accent-cyan);
            font-size: 0.82rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            font-weight: 800;
            font-family: 'GoogleSansCustom', 'Inter', 'Segoe UI', Arial, sans-serif !important;
        }}

        .hero-kicker::before {{
            content: "";
            width: 9px;
            height: 9px;
            border-radius: 999px;
            background: var(--accent-green);
            box-shadow: 0 0 18px rgba(16, 185, 129, 0.9);
        }}

        .hero-title {{
            position: relative;
            font-family: 'ArchimotoV01', sans-serif !important;
            font-size: clamp(2.4rem, 5vw, 5.1rem);
            line-height: 0.98;
            letter-spacing: 0.015em;
            margin: 0;
            background: linear-gradient(
                90deg,
                #FFFFFF 0%,
                #67E8F9 26%,
                #A78BFA 56%,
                #FFFFFF 88%
            );
            background-size: 240% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation:
                gradientFlow 5.5s linear infinite,
                titleLift 800ms ease-out both;
            text-shadow: 0 0 42px rgba(34, 211, 238, 0.20);
        }}

        .hero-subtitle {{
            position: relative;
            max-width: 960px;
            margin-top: 18px;
            color: #CBD5E1;
            font-size: 1.03rem;
            line-height: 1.75;
            font-family: 'GoogleSansCustom', 'Inter', 'Segoe UI', Arial, sans-serif !important;
        }}

        @keyframes heroReveal {{
            from {{
                opacity: 0;
                transform: translateY(18px) scale(0.985);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        @keyframes titleLift {{
            from {{
                opacity: 0;
                transform: translateY(18px);
                filter: blur(8px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
                filter: blur(0);
            }}
        }}

        @keyframes gradientFlow {{
            0% {{
                background-position: 0% center;
            }}
            100% {{
                background-position: 240% center;
            }}
        }}

        @keyframes shineSweep {{
            0% {{
                transform: translateX(-130%);
            }}
            45% {{
                transform: translateX(130%);
            }}
            100% {{
                transform: translateX(130%);
            }}
        }}

        h1:not(.hero-title), h2, h3,
        [data-testid="stMarkdownContainer"] {{
            font-family: 'GoogleSansCustom', 'Inter', 'Segoe UI', Arial, sans-serif;
        }}

        h1:not(.hero-title), h2, h3 {{
            color: var(--text-main) !important;
            letter-spacing: -0.02em;
        }}

        div[data-testid="stMetric"] {{
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(30, 41, 59, 0.68));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow:
                0 14px 40px rgba(0, 0, 0, 0.24),
                inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }}

        div[data-testid="stMetric"] label {{
            color: #94A3B8 !important;
            font-size: 0.80rem !important;
            letter-spacing: 0.04em;
        }}

        div[data-testid="stMetricValue"] {{
            color: #F8FAFC !important;
            font-weight: 900;
        }}

        .stButton > button,
        .stDownloadButton > button {{
            border: 1px solid rgba(34, 211, 238, 0.38);
            border-radius: 14px;
            background:
                linear-gradient(135deg, rgba(34, 211, 238, 0.18), rgba(59, 130, 246, 0.22));
            color: #F8FAFC;
            font-weight: 800;
            transition: all 180ms ease;
            box-shadow: 0 10px 28px rgba(34, 211, 238, 0.10);
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            transform: translateY(-2px);
            border-color: rgba(34, 211, 238, 0.75);
            box-shadow: 0 16px 36px rgba(34, 211, 238, 0.20);
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background-color: rgba(15, 23, 42, 0.92) !important;
            border-color: rgba(148, 163, 184, 0.24) !important;
            border-radius: 12px !important;
        }}

        button[data-baseweb="tab"] {{
            background: rgba(15, 23, 42, 0.72);
            border-radius: 999px;
            padding: 10px 18px;
            margin-right: 8px;
            border: 1px solid rgba(148, 163, 184, 0.16);
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            background:
                linear-gradient(135deg, rgba(34, 211, 238, 0.24), rgba(139, 92, 246, 0.22));
            border-color: rgba(34, 211, 238, 0.48);
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 14px 42px rgba(0, 0, 0, 0.25);
        }}

        div[data-testid="stAlert"] {{
            border-radius: 16px;
            border: 1px solid rgba(34, 211, 238, 0.18);
            background: rgba(15, 23, 42, 0.78);
        }}

        div[data-testid="stPlotlyChart"] {{
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.76), rgba(15, 23, 42, 0.42));
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 20px;
            padding: 12px;
            box-shadow: 0 16px 44px rgba(0, 0, 0, 0.24);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_hero_title():
    st.markdown(
        """
        <div class="hero-title-wrap">
            <div class="hero-kicker">Live Ecommerce Intelligence</div>
            <h1 class="hero-title">Ecommerce Competitor Intelligence Dashboard</h1>
            <div class="hero-subtitle">
                Scrape real ecommerce product data, clean duplicate records, analyze pricing behavior,
                inspect product-level trends, and export clean datasets for business decisions.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


inject_custom_css()
render_hero_title()


# ============================================================
# DATA HELPER FUNCTIONS
# ============================================================

def clean_column_names(dataframe):
    dataframe.columns = (
        dataframe.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    return dataframe


def clean_numeric_text(series):
    return (
        series
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace("₱", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )


def prepare_numeric_columns(dataframe):
    numeric_columns = [
        "price",
        "price_raw",
        "original_price",
        "discount_percentage",
        "rating",
        "review_count",
        "sales_estimate"
    ]

    if "price" in dataframe.columns:
        dataframe["price"] = clean_numeric_text(dataframe["price"])
        dataframe["price"] = pd.to_numeric(dataframe["price"], errors="coerce")

    elif "price_raw" in dataframe.columns:
        dataframe["price"] = clean_numeric_text(dataframe["price_raw"])
        dataframe["price"] = pd.to_numeric(dataframe["price"], errors="coerce")

    for column in numeric_columns:
        if column in dataframe.columns and column not in ["price", "price_raw"]:
            dataframe[column] = clean_numeric_text(dataframe[column])
            dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    return dataframe


def prepare_date_columns(dataframe):
    possible_date_columns = [
        "scrape_date",
        "date_checked",
        "created_at",
        "updated_at"
    ]

    for column in possible_date_columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_datetime(dataframe[column], errors="coerce")

    return dataframe


def find_product_name_column(dataframe):
    possible_columns = [
        "product_name",
        "name",
        "title",
        "product",
        "item_name"
    ]

    for column in possible_columns:
        if column in dataframe.columns:
            return column

    return None


def find_date_column(dataframe):
    possible_date_columns = [
        "date_checked",
        "scrape_date",
        "created_at",
        "updated_at"
    ]

    for column in possible_date_columns:
        if column in dataframe.columns:
            return column

    return None


def normalize_text(value):
    if pd.isna(value):
        return ""

    value = str(value).lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^a-z0-9 ]", "", value)

    return value


def remove_duplicate_products(dataframe, product_name_column):
    original_count = len(dataframe)
    df_clean = dataframe.copy()

    df_clean = df_clean.drop_duplicates()

    duplicate_rule_used = "Exact row duplicates only"
    duplicate_rows = pd.DataFrame()

    if product_name_column:
        df_clean["_normalized_product_name"] = df_clean[product_name_column].apply(normalize_text)

        duplicate_key = ["_normalized_product_name"]

        if "price" in df_clean.columns:
            duplicate_key.append("price")

        if "source_url" in df_clean.columns:
            duplicate_key.append("source_url")
            duplicate_rule_used = "Product name + price + source URL"

        elif "price" in df_clean.columns:
            duplicate_rule_used = "Product name + price"

        else:
            duplicate_rule_used = "Product name only"

        duplicate_rows = df_clean[df_clean.duplicated(subset=duplicate_key, keep="first")]
        df_clean = df_clean.drop_duplicates(subset=duplicate_key, keep="first")

        df_clean = df_clean.drop(columns=["_normalized_product_name"], errors="ignore")
        duplicate_rows = duplicate_rows.drop(columns=["_normalized_product_name"], errors="ignore")

    cleaned_count = len(df_clean)
    duplicates_removed = original_count - cleaned_count

    return df_clean, duplicate_rows, duplicates_removed, duplicate_rule_used


def format_currency(value):
    if pd.isna(value):
        return "N/A"

    return f"${value:,.2f}"


def format_number(value):
    if pd.isna(value):
        return "N/A"

    return f"{int(value):,}"


def display_kpi_cards(dataframe, duplicates_removed):
    total_products = len(dataframe)

    average_price = None
    highest_price = None
    lowest_price = None

    if "price" in dataframe.columns and dataframe["price"].notna().any():
        average_price = dataframe["price"].mean()
        highest_price = dataframe["price"].max()
        lowest_price = dataframe["price"].min()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Products", total_products)
    col2.metric("Average Price", format_currency(average_price) if average_price is not None else "N/A")
    col3.metric("Highest Price", format_currency(highest_price) if highest_price is not None else "N/A")
    col4.metric("Lowest Price", format_currency(lowest_price) if lowest_price is not None else "N/A")
    col5.metric("Duplicates Removed", duplicates_removed)

    col6, col7, col8, col9, col10 = st.columns(5)

    if "rating" in dataframe.columns and dataframe["rating"].notna().any():
        col6.metric("Average Rating", f"{dataframe['rating'].mean():.2f}")
    else:
        col6.metric("Average Rating", "N/A")

    if "review_count" in dataframe.columns and dataframe["review_count"].notna().any():
        col7.metric("Total Reviews", format_number(dataframe["review_count"].sum()))
    else:
        col7.metric("Total Reviews", "N/A")

    if "sales_estimate" in dataframe.columns and dataframe["sales_estimate"].notna().any():
        col8.metric("Estimated Sales", format_number(dataframe["sales_estimate"].sum()))
    else:
        col8.metric("Estimated Sales", "N/A")

    if "discount_percentage" in dataframe.columns and dataframe["discount_percentage"].notna().any():
        discounted_products = len(dataframe[dataframe["discount_percentage"] > 0])
        col9.metric("Discounted Products", discounted_products)
    else:
        col9.metric("Discounted Products", "N/A")

    col10.metric("Rows After Filters", len(dataframe))


def apply_filters(dataframe, product_name_column, date_column):
    st.sidebar.header("Dashboard Filters")

    filtered_df = dataframe.copy()

    if product_name_column:
        search_text = st.sidebar.text_input("Search Product Name")

        if search_text:
            filtered_df = filtered_df[
                filtered_df[product_name_column]
                .astype(str)
                .str.contains(search_text, case=False, na=False)
            ]

    categorical_filter_columns = [
        "source_url",
        "category",
        "competitor_name",
        "platform",
        "availability",
        "promotion_type"
    ]

    for column in categorical_filter_columns:
        if column in filtered_df.columns:
            options = sorted(filtered_df[column].dropna().astype(str).unique())

            if len(options) > 0 and len(options) <= 200:
                selected_options = st.sidebar.multiselect(
                    label=f"Filter by {column.replace('_', ' ').title()}",
                    options=options,
                    default=options
                )

                filtered_df = filtered_df[
                    filtered_df[column].astype(str).isin(selected_options)
                ]

    numeric_filter_columns = [
        "price",
        "rating",
        "discount_percentage",
        "review_count",
        "sales_estimate"
    ]

    for column in numeric_filter_columns:
        if column in filtered_df.columns and filtered_df[column].notna().any():
            min_value = float(filtered_df[column].min())
            max_value = float(filtered_df[column].max())

            if min_value < max_value:
                selected_range = st.sidebar.slider(
                    f"{column.replace('_', ' ').title()} Range",
                    min_value=min_value,
                    max_value=max_value,
                    value=(min_value, max_value)
                )

                filtered_df = filtered_df[
                    (filtered_df[column] >= selected_range[0]) &
                    (filtered_df[column] <= selected_range[1])
                ]

    if date_column and filtered_df[date_column].notna().any():
        min_date = filtered_df[date_column].min().date()
        max_date = filtered_df[date_column].max().date()

        if min_date < max_date:
            selected_date_range = st.sidebar.date_input(
                "Date Range",
                value=(min_date, max_date)
            )

            if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
                start_date, end_date = selected_date_range

                filtered_df = filtered_df[
                    (filtered_df[date_column].dt.date >= start_date) &
                    (filtered_df[date_column].dt.date <= end_date)
                ]

    return filtered_df


def make_price_bands(dataframe):
    if "price" not in dataframe.columns or not dataframe["price"].notna().any():
        return None

    df_temp = dataframe.copy()

    if df_temp["price"].min() == df_temp["price"].max():
        return None

    df_temp["price_band"] = pd.cut(
        df_temp["price"],
        bins=4,
        labels=[
            "Low Price",
            "Mid-Low Price",
            "Mid-High Price",
            "High Price"
        ]
    )

    return df_temp


def style_plotly_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="GoogleSansCustom, Inter, Segoe UI, Arial",
            color="#E5E7EB"
        ),
        title_font=dict(
            size=18,
            color="#F8FAFC"
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    fig.update_xaxes(
        gridcolor="rgba(148, 163, 184, 0.12)",
        zerolinecolor="rgba(148, 163, 184, 0.16)"
    )

    fig.update_yaxes(
        gridcolor="rgba(148, 163, 184, 0.12)",
        zerolinecolor="rgba(148, 163, 184, 0.16)"
    )

    return fig


# ============================================================
# SIDEBAR: DATA SOURCE
# ============================================================

st.sidebar.header("Data Source")

data_source = st.sidebar.radio(
    "Choose how you want to load data:",
    [
        "Scrape Website",
        "Upload CSV",
        "Use Existing CSV"
    ]
)

remove_duplicates = st.sidebar.checkbox(
    "Automatically remove duplicate products",
    value=True
)

df = None


# ============================================================
# OPTION 1: SCRAPE WEBSITE
# ============================================================

if data_source == "Scrape Website":
    st.sidebar.subheader("Website Scraper")

    url = st.sidebar.text_input(
        "Website URL",
        value="https://webscraper.io/test-sites/e-commerce/allinone"
    )

    st.sidebar.caption(
        "CSS selectors are optional. Leave them blank if you want the app to auto-detect product data."
    )

    with st.sidebar.expander("Optional CSS Selectors"):
        card_selector = st.text_input(
            "Product card selector",
            value="",
            placeholder="Example: div.thumbnail"
        )

        name_selector = st.text_input(
            "Product name selector",
            value="",
            placeholder="Example: a.title"
        )

        price_selector = st.text_input(
            "Price selector",
            value="",
            placeholder="Example: h4.price"
        )

        description_selector = st.text_input(
            "Description selector",
            value="",
            placeholder="Example: p.description"
        )

    with st.sidebar.expander("Demo Website Selectors"):
        st.write("Use these only for testing the demo site:")
        st.code(
            """
Product card selector: div.thumbnail
Product name selector: a.title
Price selector: h4.price
Description selector: p.description
            """
        )

    if st.sidebar.button("Scrape Website"):
        with st.spinner("Scraping website data... please wait."):
            try:
                df = scrape_from_url(
                    url=url,
                    card_selector=card_selector.strip() or None,
                    name_selector=name_selector.strip() or None,
                    price_selector=price_selector.strip() or None,
                    description_selector=description_selector.strip() or None,
                    save_path=CSV_FILE
                )

                st.session_state["current_df"] = df
                st.success(f"Scraping completed successfully. {len(df)} products collected.")

            except Exception as error:
                st.error(f"Scraping failed: {error}")

    elif "current_df" in st.session_state:
        df = st.session_state["current_df"]

    elif os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)


# ============================================================
# OPTION 2: UPLOAD CSV
# ============================================================

elif data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload a CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state["current_df"] = df
        st.success("CSV uploaded successfully.")
    else:
        st.info("Upload a CSV file from the sidebar to begin.")


# ============================================================
# OPTION 3: USE EXISTING CSV
# ============================================================

elif data_source == "Use Existing CSV":
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.success("Existing products.csv loaded successfully.")
    else:
        st.warning("No products.csv file found yet. Scrape a website or upload a CSV first.")


# ============================================================
# STOP IF NO DATA
# ============================================================

if df is None:
    st.stop()

if df.empty:
    st.warning("The loaded dataset is empty.")
    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

df = clean_column_names(df)
df = prepare_numeric_columns(df)
df = prepare_date_columns(df)

product_name_column = find_product_name_column(df)
date_column = find_date_column(df)

duplicates_removed = 0
duplicate_rows = pd.DataFrame()
duplicate_rule_used = "Duplicate removal turned off"

if remove_duplicates:
    df, duplicate_rows, duplicates_removed, duplicate_rule_used = remove_duplicate_products(
        dataframe=df,
        product_name_column=product_name_column
    )

filtered_df = apply_filters(df, product_name_column, date_column)


# ============================================================
# QUICK EXPORT
# ============================================================

st.header("Quick Export")

quick_export_csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Cleaned and Filtered Data as CSV",
    data=quick_export_csv,
    file_name="cleaned_ecommerce_competitor_data.csv",
    mime="text/csv",
    key="quick_export_download_button"
)


# ============================================================
# DATA CLEANING SUMMARY
# ============================================================

st.header("Data Cleaning Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Cleaned Product Records", len(df))
col2.metric("Duplicates Removed", duplicates_removed)
col3.metric("Records After Filters", len(filtered_df))

st.caption(f"Duplicate rule used: {duplicate_rule_used}")

if remove_duplicates and duplicates_removed > 0:
    with st.expander("View Removed Duplicate Records"):
        st.dataframe(duplicate_rows, use_container_width=True)

elif remove_duplicates and duplicates_removed == 0:
    st.info("No duplicate products were detected.")

if filtered_df.empty:
    st.warning("No records match your current filters. Try adjusting the sidebar filters.")
    st.stop()


# ============================================================
# MAIN DASHBOARD TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Overview",
        "Price Analytics",
        "Additional Columns",
        "Data Quality",
        "Data Table"
    ]
)


# ============================================================
# TAB 1: OVERVIEW
# ============================================================

with tab1:
    st.header("Overview")

    display_kpi_cards(filtered_df, duplicates_removed)

    st.subheader("Product Data Preview")
    st.dataframe(filtered_df.head(20), use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if "price" in filtered_df.columns and filtered_df["price"].notna().any():
            st.subheader("Price Distribution")

            fig = px.histogram(
                filtered_df,
                x="price",
                nbins=20,
                title="Product Price Distribution"
            )

            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid price column found for price distribution.")

    with col2:
        price_band_df = make_price_bands(filtered_df)

        if price_band_df is not None:
            st.subheader("Product Share by Price Band")

            price_band_count = price_band_df["price_band"].value_counts().reset_index()
            price_band_count.columns = ["price_band", "count"]

            fig = px.pie(
                price_band_count,
                names="price_band",
                values="count",
                title="Product Share by Price Band",
                hole=0.42
            )

            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Price band pie chart needs varied price data.")

    if date_column and filtered_df[date_column].notna().any():
        st.subheader("Records Over Time")

        records_over_time = (
            filtered_df
            .dropna(subset=[date_column])
            .groupby(pd.Grouper(key=date_column, freq="D"))
            .size()
            .reset_index(name="record_count")
        )

        fig = px.line(
            records_over_time,
            x=date_column,
            y="record_count",
            title="Scraped Records Over Time",
            markers=True
        )

        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 2: PRICE ANALYTICS
# ============================================================

with tab2:
    st.header("Price Analytics")

    if "price" in filtered_df.columns and filtered_df["price"].notna().any():

        if product_name_column:
            highest_price_df = (
                filtered_df[[product_name_column, "price"]]
                .dropna()
                .sort_values("price", ascending=False)
                .head(20)
            )

            st.subheader("Top 20 Highest-Priced Products")

            fig = px.bar(
                highest_price_df,
                x=product_name_column,
                y="price",
                title="Top 20 Highest-Priced Products"
            )

            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)

            lowest_price_df = (
                filtered_df[[product_name_column, "price"]]
                .dropna()
                .sort_values("price", ascending=True)
                .head(20)
            )

            st.subheader("Top 20 Lowest-Priced Products")

            fig = px.bar(
                lowest_price_df,
                x=product_name_column,
                y="price",
                title="Top 20 Lowest-Priced Products"
            )

            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)

        if "original_price" in filtered_df.columns:
            st.subheader("Current Price vs Original Price")

            if product_name_column:
                comparison_df = (
                    filtered_df[[product_name_column, "price", "original_price"]]
                    .dropna()
                    .head(20)
                )

                fig = px.bar(
                    comparison_df,
                    x=product_name_column,
                    y=["price", "original_price"],
                    barmode="group",
                    title="Current Price vs Original Price"
                )

                fig = style_plotly_chart(fig)
                st.plotly_chart(fig, use_container_width=True)

        if "discount_percentage" in filtered_df.columns:
            st.subheader("Top Discounted Products")

            if product_name_column:
                discount_df = (
                    filtered_df[[product_name_column, "discount_percentage"]]
                    .dropna()
                    .sort_values("discount_percentage", ascending=False)
                    .head(20)
                )

                fig = px.bar(
                    discount_df,
                    x=product_name_column,
                    y="discount_percentage",
                    title="Top Products by Discount Percentage"
                )

                fig = style_plotly_chart(fig)
                st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No valid price data available.")


# ============================================================
# TAB 3: ADDITIONAL COLUMNS
# ============================================================

with tab3:
    st.header("Charts from Real Columns Only")

    st.write(
        "This section only creates charts for columns that actually exist in your scraped or uploaded data."
    )

    categorical_columns = filtered_df.select_dtypes(include=["object"]).columns.tolist()
    numeric_columns = filtered_df.select_dtypes(include=["number"]).columns.tolist()

    ignored_columns = ["description"]

    categorical_columns = [
        column for column in categorical_columns
        if column not in ignored_columns
    ]

    if categorical_columns:
        st.subheader("Categorical Column Breakdown")

        selected_category_column = st.selectbox(
            "Choose a categorical column",
            categorical_columns
        )

        category_count = (
            filtered_df[selected_category_column]
            .value_counts()
            .reset_index()
        )

        category_count.columns = [selected_category_column, "count"]

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                category_count,
                x=selected_category_column,
                y="count",
                title=f"Count by {selected_category_column}"
            )

            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                category_count,
                names=selected_category_column,
                values="count",
                title=f"Share by {selected_category_column}",
                hole=0.42
            )

            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)

    if len(numeric_columns) >= 2:
        st.subheader("Numeric Relationship Chart")

        x_axis = st.selectbox(
            "Choose X-axis",
            numeric_columns,
            index=0
        )

        y_axis = st.selectbox(
            "Choose Y-axis",
            numeric_columns,
            index=1
        )

        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            hover_name=product_name_column if product_name_column else None,
            title=f"{x_axis} vs {y_axis}"
        )

        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    elif len(numeric_columns) == 1:
        st.subheader("Numeric Distribution")

        selected_numeric_column = numeric_columns[0]

        fig = px.histogram(
            filtered_df,
            x=selected_numeric_column,
            nbins=20,
            title=f"Distribution of {selected_numeric_column}"
        )

        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No additional numeric columns found.")


# ============================================================
# TAB 4: DATA QUALITY
# ============================================================

with tab4:
    st.header("Data Quality Checks")

    missing_values = filtered_df.isna().sum().reset_index()
    missing_values.columns = ["column", "missing_values"]
    missing_values = missing_values[missing_values["missing_values"] > 0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rows", len(filtered_df))
    col2.metric("Total Columns", len(filtered_df.columns))
    col3.metric("Missing Values", int(filtered_df.isna().sum().sum()))

    if not missing_values.empty:
        st.subheader("Missing Values by Column")

        fig = px.bar(
            missing_values,
            x="column",
            y="missing_values",
            title="Missing Values by Column"
        )

        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(missing_values, use_container_width=True)

    else:
        st.success("No missing values found in the current filtered data.")

    st.subheader("Column Summary")

    column_summary = pd.DataFrame({
        "column": filtered_df.columns,
        "data_type": filtered_df.dtypes.astype(str).values,
        "non_null_count": filtered_df.notna().sum().values,
        "unique_values": filtered_df.nunique().values
    })

    st.dataframe(column_summary, use_container_width=True)


# ============================================================
# TAB 5: DATA TABLE
# ============================================================

with tab5:
    st.header("Full Product Data")

    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Export Data")

    full_export_csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Cleaned and Filtered Data as CSV",
        data=full_export_csv,
        file_name="cleaned_ecommerce_competitor_data.csv",
        mime="text/csv",
        key="data_table_download_button"
    )


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.header("Business Insights")

if "price" in filtered_df.columns and filtered_df["price"].notna().any():
    average_price = filtered_df["price"].mean()
    highest_price = filtered_df["price"].max()
    lowest_price = filtered_df["price"].min()

    st.write(f"The average product price in the current filtered dataset is **{format_currency(average_price)}**.")
    st.write(f"The highest product price found is **{format_currency(highest_price)}**.")
    st.write(f"The lowest product price found is **{format_currency(lowest_price)}**.")

    if product_name_column:
        most_expensive = filtered_df.loc[filtered_df["price"].idxmax()]
        cheapest = filtered_df.loc[filtered_df["price"].idxmin()]

        st.write(f"The most expensive product is **{most_expensive[product_name_column]}**.")
        st.write(f"The lowest-priced product is **{cheapest[product_name_column]}**.")

    if duplicates_removed > 0:
        st.write(
            f"The tool removed **{duplicates_removed} duplicate product records**, "
            "which improves the reliability of the analysis."
        )

    st.write(
        "This dashboard helps review real scraped ecommerce data, clean duplicates, inspect pricing, "
        "and export cleaned results for further analysis."
    )

else:
    st.write(
        "No valid price data found. Try uploading a CSV with a price column or scraping a page that contains product prices."
    )