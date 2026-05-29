Ecommerce Competitor Intelligence Dashboard

A business-focused Streamlit dashboard that scrapes real ecommerce product data, removes duplicate records, analyzes pricing patterns, checks data quality, and exports cleaned datasets.

## Project Overview

This project was built to support ecommerce competitor research and product data analysis. The dashboard allows users to scrape product listing data from a website, upload CSV files, clean duplicate product records, analyze price trends, and export cleaned data for further reporting.

## Business Problem

Ecommerce teams often need to monitor competitor products, pricing, and market activity. Manually collecting and cleaning this data can be time-consuming and prone to errors.

This tool helps simplify that workflow by turning scraped or uploaded product data into a clean, visual, and exportable dashboard.

## Features

- Scrape ecommerce product data from a website URL
- Upload and analyze CSV files
- Use existing scraped CSV data
- Automatically remove duplicate product records
- Search and filter product data
- Analyze price distribution and price bands
- View highest-priced and lowest-priced products
- Generate charts from real available columns
- Check missing values and column quality
- Export cleaned and filtered data as CSV

## Tools Used

- Python
- Streamlit
- Pandas
- Plotly
- Requests
- BeautifulSoup

## Files in This Project

```text
ecommerce-competitor-scraper/
├── app.py
├── scraper.py
├── products.csv
├── requirements.txt
├── README.md
└── assets/
