# **Chat Bot Start**

# Libraries
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk
import re
import nltk
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')

import torch
import spacy
import subprocess
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import io
import base64

# Load SpaCy English language model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.call(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


# Load SpaCy English language model
nlp = spacy.load("en_core_web_sm")


# Import necessary files

df = pd.read_csv("Financial1.csv")
df_mp = pd.read_excel("qa.xlsx")
qa_data = ""

# pre Process the data

def preprocess_text(text):
    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc]
    lemmas_without_stopwords = [lemma for lemma in lemmas if lemma.lower() not in stopwords and lemma.isalpha()]

    return ' '.join(lemmas_without_stopwords)

# Loading the dataset

def load_database(numbers_to_text=True):
    
    #if numbers_to_text:
    #    df_mp['question'] = df_mp['question'].apply(transcribe_numbers)

    df_mp['processed_texts'] = df_mp['question'].apply(preprocess_text)    
    qa_data = qa_data['processed_texts'].tolist()

# Cosine Similarity

def Cosine_distance(user_question, numbers_to_text=True):
    
    df_mp['processed_texts'] = df_mp['question'].apply(preprocess_text)
    qa_data = df_mp['processed_texts'].tolist()
    
    if numbers_to_text:
        user_question = preprocess_text(user_question)
                                         
    user_text_processed = preprocess_text(user_question)
    vectorizer = TfidfVectorizer()
    bow_matrix = vectorizer.fit_transform(qa_data + [user_text_processed])

    cosine_distances = cosine_similarity(bow_matrix[-1], bow_matrix[:-1])
   
    max_distance_index = cosine_distances.argmax()
     
    df_mp['distances'] = cosine_distances.flatten().tolist()

    return df_mp['question'].iloc[max_distance_index], df_mp['location'].iloc[max_distance_index], df_mp['distances'].iloc[max_distance_index],  df_mp['intent'].iloc[max_distance_index]


# Fuunction calling to get a numerical data for company


def fun_detail(company_name, year_name, intent):
    # code if someone not provide Company name:
    if not company_name:
        return "Can you please provide your query with the company name?"    
    if not year_name:
        return "Can you please provide your query with the year?"
    
    # Filter the DataFrame based on the company name
    filtered_df = df[df['Company'].str.upper() == company_name[0]]
    #print(filtered_df)
    company_name_str = ', '.join([name.title() for name in company_name])
    # Check if the company name is in the dataset
    if filtered_df.empty:
        company_name_str = ', '.join([name.title() for name in company_name])
        return f"The {company_name_str} company is not available in our database. You have to select from our company list."
    
    # Check if year_name is a list
    if isinstance(year_name, list):
        # Check each year in the list
        result = []
        for year in year_name:
            if int(year) < df['Year'].min() or int(year) > df['Year'].max():
                result.append(f"The {company_name_str} company financial report is just available between {df['Year'].min()} to {df['Year'].max()} as the provided year {year} is not in our database.")
            else:
                filtered_df_year = filtered_df[filtered_df['Year'] == int(year)]
                if filtered_df_year.empty:
                    result.append(f"No data available for {company_name_str} in {year}.")
                else:
                    print("class", intent)
                    if intent in ["Revenue", "Gross Profit", "Market Cap", "Net Income", "EBITDA", "Share Holder Equity", "Cash Flow from Operating", "Cash Flow from Investing", "Cash Flow from Financial Activities"]:
                        value_detail = float(filtered_df_year[intent].iloc[0])  # Assuming 'intent' is the column name
                        result.append(str(value_detail) + " Millions USD")
                    elif intent in ["ROE", "ROA", "ROI", "Return on Tangible Equity", "Net Profit Margin"]:
                        value_detail = float(filtered_df_year[intent].iloc[0])  # Assuming 'intent' is the column name
                        result.append(str(value_detail) + " %")
                    elif intent in ["Free Cash Flow pe Share"]:
                        value_detail = float(filtered_df_year[intent].iloc[0])  # Assuming 'intent' is the column name
                        result.append(str(value_detail) + "US Dollers per share")
                    else:
                        value_detail = float(filtered_df_year[intent].iloc[0])  # Assuming 'intent' is the column name
                        result.append(str(value_detail))

        return result[0] if len(result) == 1 else result  # Return single result or list of results
    
    else:
        # Check if any data is available after filtering
        
        if int(year_name) < df['Year'].min() or int(year_name) > df['Year'].max():
            return f"The {company_name_str} company financial report is just available between {df['Year'].min()} to {df['Year'].max()} as the provided year {year_name} is not in our database."
        
        filtered_df_year = filtered_df[filtered_df['Year'] == int(year_name)]
        if filtered_df_year.empty:
            return f"No data available for {company_name_str} in {year_name}."
        # Extract the revenue value
        value_detail = float(filtered_df_year[intent].iloc[0])  # Assuming 'Revenue' is the column name
        return str(value_detail)  # Convert value_detail to string

    
    
# Linear Function to Predict the Future Values
def linear_regression_and_plot(intent, company_name):
    
    # Filter the DataFrame based on the company name
    filtered_df = df[df['Company'].str.upper() == company_name[0]]
    # Check if filtered dataframe is empty
    if filtered_df.empty:
        return ValueError(f"No data available for company '{company_name}'")
    # Extract data for the specific financial term and company
    X = filtered_df["Year"].values
    y = filtered_df[intent].values

    # Train linear regression model
    model = LinearRegression()
    model.fit(X.reshape(-1, 1), y)

    # Predict values for the next 5 years
    future_years = np.arange(X.max() + 1, X.max() + 6).reshape(-1, 1)
    predicted_values = model.predict(future_years)

    # Plot the linear regression
    plt.figure(figsize=(10, 6))
    plt.scatter(filtered_df["Year"], filtered_df[intent], color='blue', label='Actual Data')
    plt.plot(future_years, predicted_values, color='red', label='Linear Regression')
    plt.xlabel('Year')
    plt.ylabel(intent)
    plt.title(f'prediction for {intent} {company_name[0]}')
    plt.legend()
    plt.show()

    # Convert the plot to an image
    fig, ax = plt.subplots()
    ax.scatter(filtered_df["Year"], filtered_df[intent], color='blue', label='Actual Data')
    ax.plot(future_years, predicted_values, color='red', label='Linear Regression')
    #ax.plot(future_years, predicted_values)
    ax.set_xlabel('Year')
    ax.set_ylabel(intent)
    ax.set_title(f'Prediction for {intent} {company_name[0]}')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    # Encode the image as a base64 string
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return future_years, predicted_values, image_base64

# Compare the companies with specific details

def comparative_analysis(company_name, intent):
    # Initialize lists to store data for each company
    company_years = {}
    company_values = {}

    # Fetch data for each company and financial term
    for company in company_name:
        # Filter data for the specific company and financial term
        company_data = df[df['Company'].str.upper() == company.upper()]
        # Check if filtered dataframe is empty
        # Check if filtered dataframe is empty
        # Check if filtered dataframe is empty
        if company_data.empty:
            return f"The company '{company}' is not available in our dataset."
        else:
            company_years[company] = company_data['Year'].values
            company_values[company] = company_data[intent].values

    # Plot the comparative analysis
    plt.figure(figsize=(10, 6))
    for company in company_name:
        plt.plot(company_years[company], company_values[company], label=company)

    # Add labels and title
    plt.xlabel('Year')
    plt.ylabel(intent)
    plt.title(f'Comparative Analysis of {intent} across Companies')

    # Add legend
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.tight_layout()  # Adjust layout
    plt.show()

    # Convert the plot to an image
    fig, ax = plt.subplots(figsize=(10, 6))
    for company in company_name:
        ax.plot(company_years[company], company_values[company], label=company)
    ax.set_xlabel('Year')
    ax.set_ylabel(intent)
    ax.set_title(f'Comparative Analysis of {intent} across Companies')
    ax.legend()
    ax.grid(True)  # Add grid
    plt.tight_layout()  # Adjust layout
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    # Encode the image as a base64 string
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    
    return image_base64
  
# srock evaluaiton:
def stock_valuation(company_name, year_name):
    # code if someone not provide Company name:
    if not company_name:
        return "Can you please provide your query with the company name?"    
    if not year_name:
        return "Can you please provide your query with the year?"
    
    # Filter the DataFrame based on the company name
    filtered_df = df[df['Company'].str.upper() == company_name[0]]
    
    company_name_str = ', '.join([name.title() for name in company_name])
    # Check if the company name is in the dataset
    if filtered_df.empty:
        return f"The {company_name_str} company is not available in our database. You have to select from our company list."
    
    # Check if year_name is a list
    if isinstance(year_name, list):
        # Check each year in the list
        result = []
        for year in year_name:
            if int(year) < df['Year'].min() or int(year) > df['Year'].max():
                result.append(f"The {company_name_str} company financial report is just available between {df['Year'].min()} to {df['Year'].max()} as the provided year {year} is not in our database.")
            else:
                filtered_df_year = filtered_df[filtered_df['Year'] == int(year)]
                if filtered_df_year.empty:
                    result.append(f"No data available for {company_name_str} in {year}.")
                else:
                    # Filter data for the specified company and year
                    company_data = df[(df['Company'].str.upper() == company_name[0]) & (df['Year'] == int(year_name[0]))].copy()
    
                    # Calculate P/E ratio
                    company_data.loc[:, 'PE_ratio'] = company_data['Market Cap'] / company_data['Earning Per Share']

                    # Calculate stock price based on P/E ratio
                    company_data.loc[:, 'Stock Price PE'] = company_data['Earning Per Share'] * company_data['PE_ratio']

                    # Calculate stock price based on FCF per Share (assuming a growth rate of 5%)
                    growth_rate = 0.05
                    company_data.loc[:, 'Stock Price FCF'] = company_data['Free Cash Flow per Share'] * (1 + growth_rate)

                    # Explanation for P/E Ratio
                    pe_ratio_explanation = f"The Price-to-Earnings (P/E) ratio of {company_name[0]} for the year {year_name[0]} is {company_data['PE_ratio'].values[0]}. This means that investors are willing to pay a certain multiple of the company's earnings per share, which indicates their expectation for future earnings growth. A higher P/E ratio suggests that investors are more optimistic about the company's future prospects."

                    # Explanation for FCF per Share
                    fcf_per_share_explanation = f"The Free Cash Flow (FCF) per Share of {company_name[0]} for the year {year_name[0]} is {company_data['Free Cash Flow per Share'].values[0]}. This represents the amount of cash generated by the company for each share of common stock outstanding. A higher FCF per share indicates that the company has more cash available for potential investments, debt reduction, or distributions to shareholders."
                    result.extend([pe_ratio_explanation, fcf_per_share_explanation])
        return "\n".join(result)  # Return single result or list of results

    else:
        # Check if any data is available after filtering
        if int(year_name) < df['Year'].min() or int(year_name) > df['Year'].max():
            return f"The {company_name_str} company financial report is just available between {df['Year'].min()} to {df['Year'].max()} as the provided year {year_name} is not in our database."
        
        filtered_df_year = filtered_df[filtered_df['Year'] == int(year_name)]
        if filtered_df_year.empty:
            return f"No data available for {company_name_str} in {year_name}."
        # Extract the revenue value
        company_data = df[(df['Company'].str.upper() == company_name[0]) & (df['Year'] == int(year_name))].copy()
    
        # Calculate P/E ratio
        company_data.loc[:, 'PE_ratio'] = company_data['Market Cap'] / company_data['Earning Per Share']

        # Calculate stock price based on P/E ratio
        company_data.loc[:, 'Stock Price PE'] = company_data['Earning Per Share'] * company_data['PE_ratio']

        # Calculate stock price based on FCF per Share (assuming a growth rate of 5%)
        growth_rate = 0.05
        company_data.loc[:, 'Stock Price FCF'] = company_data['Free Cash Flow per Share'] * (1 + growth_rate)

        # Explanation for P/E Ratio
        pe_ratio_explanation = f"The Price-to-Earnings (P/E) ratio of {company_name[0]} for the year {year_name[0]} is {company_data['PE_ratio'].values[0]}. This means that investors are willing to pay a certain multiple of the company's earnings per share, which indicates their expectation for future earnings growth. A higher P/E ratio suggests that investors are more optimistic about the company's future prospects."

        # Explanation for FCF per Share
        fcf_per_share_explanation = f"The Free Cash Flow (FCF) per Share of {company_name[0]} for the year {year_name[0]} is {company_data['Free Cash Flow per Share'].values[0]}. This represents the amount of cash generated by the company for each share of common stock outstanding. A higher FCF per share indicates that the company has more cash available for potential investments, debt reduction, or distributions to shareholders."
        
        return "\n".join([pe_ratio_explanation, fcf_per_share_explanation])


# Risk Analyst:
def financial_risk_assessment(company_name, year_name):
    # code if someone not provide Company name:
    if not company_name:
        return "Can you please provide your query with the company name?"    
    if not year_name:
        return "Can you please provide your query with the year?"
    
    # Filter the DataFrame based on the company name
    filtered_df = df[df['Company'].str.upper() == company_name[0]]
    
    company_name_str = ', '.join([name.title() for name in company_name])
    # Check if the company name is in the dataset
    if filtered_df.empty:
        return f"The {company_name_str} company is not available in our database. You have to select from our company list."
    
    # Check if year_name is a list
    if isinstance(year_name, list):
        # Check each year in the list
        result = []
        for year in year_name:
            if int(year) < df['Year'].min() or int(year) > df['Year'].max():
                result.append(f"The {company_name_str} company financial report is just available between {df['Year'].min()} to {df['Year'].max()} as the provided year {year} is not in our database.")
            else:
                filtered_df_year = filtered_df[filtered_df['Year'] == int(year)]
                if filtered_df_year.empty:
                    result.append(f"No data available for {company_name_str} in {year}.")
                else:
                    # Filter data for the specified company and year
                    # Filter data for the specified company and year
                    company_data = df[(df['Company'].str.upper() == company_name[0]) & (df['Year'] == int(year_name[0]))].copy()
                    # Calculate Net Profit Margin
                    net_profit_margin = company_data['Net Profit Margin'].values[0]

                    # Calculate Debtor Equity Ratio
                    debtor_equity_ratio = company_data['Debtor Equity Ratio'].values[0]

                    # Calculate Return on Tangible Equity
                    rote = company_data['Return on Tangible Equity'].values[0]

                    # Explanation for Net Profit Margin
                    net_profit_margin_explanation = f" Net Profit Margin: The Net Profit Margin of {company_name_str} for the year {year_name[0]} is {net_profit_margin:.2f}%. This metric indicates the percentage of revenue that remains as net income after all expenses have been deducted. A higher net profit margin suggests better profitability and financial health."

                    # Explanation for Debtor Equity Ratio
                    debtor_equity_ratio_explanation = f"Debtor Equity Ratio: The Debtor Equity Ratio of {company_name_str} for the year {year_name[0]} is {debtor_equity_ratio:.2f}. This ratio measures the relationship between a company's total debt and its shareholder equity. A higher debtor equity ratio indicates higher financial leverage, which can increase financial risk."

                    # Explanation for Return on Tangible Equity
                    rote_explanation = f" Return on Tangible Equity:The Return on Tangible Equity (ROTE) of {company_name_str} for the year {year_name[0]} is {rote:.2f}%. This metric assesses a company's profitability relative to its tangible equity capital. A higher ROTE indicates better efficiency in generating returns for shareholders."

                    # Combine all explanations into a single formatted string
                    
                    result.extend(["Financial Risk Assessment Results:",net_profit_margin_explanation, debtor_equity_ratio_explanation, rote_explanation])
        return "\n".join(result)  # Return single result or list of results

    else:
        # Check if any data is available after filtering
        if int(year_name) < df['Year'].min() or int(year_name) > df['Year'].max():
            return f"The {company_name_str} company financial report is just available between {df['Year'].min()} to {df['Year'].max()} as the provided year {year_name} is not in our database."
        
        filtered_df_year = filtered_df[filtered_df['Year'] == int(year_name)]
        if filtered_df_year.empty:
            return f"No data available for {company_name_str} in {year_name}."
        # Extract the revenue value
        company_data = df[(df['Company'].str.upper() == company_name[0]) & (df['Year'] == int(year_name))].copy()
        # Calculate Net Profit Margin
        net_profit_margin = company_data['Net Profit Margin'].values[0]

        # Calculate Debtor Equity Ratio
        debtor_equity_ratio = company_data['Debtor Equity Ratio'].values[0]

        # Calculate Return on Tangible Equity
        rote = company_data['Return on Tangible Equity'].values[0]

        # Explanation for Net Profit Margin
        net_profit_margin_explanation = f" Net Profit Margin: The Net Profit Margin of {company_name_str} for the year {year_name[0]} is {net_profit_margin:.2f}%. This metric indicates the percentage of revenue that remains as net income after all expenses have been deducted. A higher net profit margin suggests better profitability and financial health."

        # Explanation for Debtor Equity Ratio
        debtor_equity_ratio_explanation = f"Debtor Equity Ratio: The Debtor Equity Ratio of {company_name_str} for the year {year_name[0]} is {debtor_equity_ratio:.2f}. This ratio measures the relationship between a company's total debt and its shareholder equity. A higher debtor equity ratio indicates higher financial leverage, which can increase financial risk."

        # Explanation for Return on Tangible Equity
        pr_rote_explanation = f" Return on Tangible Equity:The Return on Tangible Equity (ROTE) of {company_name_str} for the year {year_name[0]} is {rote:.2f}%. This metric assesses a company's profitability relative to its tangible equity capital. A higher ROTE indicates better efficiency in generating returns for shareholders."

        # Combine all explanations into a single formatted string
        result = "\n".join(["Financial Risk Assessment Results:",net_profit_margin_explanation, debtor_equity_ratio_explanation, rote_explanation])
        
        return "\n".join(["Stock Valuation Results:",net_profit_margin_explanation, debtor_equity_ratio_explanation,rote_explanation])

    

# Capital budgeting
# Function to perform capital budgeting analysis
def perform_capital_budgeting_analysis(company_name, year_names):
    discount_rate = 0.08  # Replace with the appropriate discount rate

    # Function to calculate NPV
    def calculate_npv(cash_flows, discount_rate):
        npv = 0
        for t, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** (t + 1))
        return npv

    # Function to calculate IRR
    def calculate_irr(cash_flows, iterations=1000):
        investment = cash_flows[0]
        for r in range(1, iterations):
            irr = (1 + r / 100.0)
            npv = 0
            for t, cash_flow in enumerate(cash_flows):
                npv += cash_flow / (irr ** (t + 1))
            if npv - investment <= 0:
                return round(irr - 1, 5)
        return None
    result = []
    # Filter data for the specified company and year
    company_name_str = ', '.join([name.title() for name in company_name])
    for year_name in year_names:
        company_data = df[(df['Company'].str.upper() == company_name[0]) & (df['Year'] == int(year_name))].copy()
        
        # Check if the company exists in the dataset for the specified year
        if company_data.empty:
            result.append(f"Data not found for {company_name_str} in {year_name}.")
        else:
            # Calculate Free Cash Flow (FCF) for the current company and year
            company_data['FCF'] = company_data['Cash Flow from Operating'] - company_data['Cash Flow from Investing']

            # Calculate Net Present Value (NPV)
            cash_flows = [company_data['Cash Flow from Operating'].iloc[0], 
                          -company_data['Cash Flow from Investing'].iloc[0], 
                          -company_data['Cash Flow from Financial Activities'].iloc[0]]
            npv_value = calculate_npv(cash_flows, discount_rate)

            # Calculate Internal Rate of Return (IRR)
            irr_value = calculate_irr(cash_flows)

            # Calculate Payback Period
            cumulative_cash_flows = np.cumsum(cash_flows)
            payback_period = np.argmax(cumulative_cash_flows >= 0) + 1

            # Add the results to the result list
            result.append(f"\nResults of Capital Budgeting Analysis for {company_name_str} in year {year_name[0]}:\n"
                          f"NPV: {npv_value}\nIRR: {irr_value if irr_value is not None else 'IRR not found'}\n"
                          f"Payback Period: {payback_period} year")
    return "\n".join(result)

# SHould I Invest

# Define a function to determine if investing in a company is advisable based on certain criteria

def should_invest(company_name):
    # Initialize reasons for the decision
    reasons = []
    company_data = df[df['Company'].str.upper() == company_name[0].upper()]
    company_name_str = ', '.join([name.title() for name in company_name])
    if company_data.empty:
        reasons.append(f"Data not found for the {company_name_str} company in our dataset. Please provide a correct company name.")
        return "\n".join(reasons)
    
    row = company_data.iloc[0]

    if row['ROE'] > 0:
        reasons.append("Positive ROE")
    else:
        reasons.append("Negative ROE")

    if row['ROA'] > 0:
        reasons.append("Positive ROA")
    else:
        reasons.append("Negative ROA")

    if row['Net Profit Margin'] > 0.1:
        reasons.append("Net Profit Margin > 10%")
    else:
        reasons.append("Net Profit Margin <= 10%")

    if row['Current Ratio'] > 1.5:
        reasons.append("Current Ratio > 1.5")
    else:
        reasons.append("Current Ratio <= 1.5")

    if row['Free Cash Flow per Share'] > 0:
        reasons.append("Positive Free Cash Flow per Share")
    else:
        reasons.append("Negative Free Cash Flow per Share")

    positive_criteria = sum([1 for x in [row['ROE'], row['ROA'], row['Net Profit Margin'], row['Current Ratio'], row['Free Cash Flow per Share']] if x > 0])

    if positive_criteria >= 3:
        decision = "It is advisable to invest in " + row['Company'] + "\nReasons:\n" + "\n".join(reasons)
    else:
        decision = "It is not advisable to invest in " + row['Company'] + "\nReasons:\n" + "\n".join(reasons)
    
    return decision        

# Function to extract company name and year explicitly from the user question
import string
def extract_company_and_year(sentence):
    # Process the sentence using SpaCy
    doc = nlp(sentence)
    # Extract company name
    #companies = [ent.text.upper() for ent in doc.ents if ent.label_ == "ORG" or "GPE"]
    companies = [ent.text.upper() for ent in doc.ents if ent.label_ in ["ORG", "GPE","NORP"] and ent.label_ != "DATE"]
    for ent in doc.ents:
        print("text",ent.text)
        print("label",ent.label_)
    return companies

# Function to extract company name and year explicitly from the user question
def extract_and_year(sentence):
    # Process the sentence using SpaCy
    doc = nlp(sentence)
    # Extract year and int(token.text) in available_details['Year']
    years = [token.text for token in doc if token.text.isdigit()]
    return  years
'''
def extract_sector(sentence):
    # Process the sentence using SpaCy
    doc = nlp(sentence)
    # Extract the term
    for token in doc:
        if token.text in ['IT', 'FOOD', 'FinTech','Bank','Manufacturing','Finance','ELEC','LOGI','Automobile','Telecommunication','Retail','E-Commerce','Technology','Energy']:
            return token.text.lower().replace(' ', '_')
    return None
'''
import time
def simulate_typing(answer):
    for char in answer:
        print(char, end='', flush=True)
        time.sleep(0.08)  # Adjust the delay (in seconds) as needed
    print()  # Move to the next line after the full answer is printed


def fun_bot(user_question):
#while True:
    response_text =""
    # Get a question from the user
    #user_question = input("USER: ")
    question, location, distance, intent  = Cosine_distance(user_question)

    # Check if the user wants to exit
    if user_question.lower() == "bye":
        print("Goodbye!")
        
      
    else:   
        # Extract company name from question
        company_name = extract_company_and_year(user_question)
        # Extract year from question
        year_name = extract_and_year(user_question)
        #term = extract_term(user_question)
        # calling the fun_details function to extrect the information from dataset
        
        if location == "fun_detail":
            result = fun_detail(company_name, year_name, intent)
            return result
        
        # calling fun-the linear_predict
        elif location == "fun_predict":
            
            future_years, predicted_values, image_base64 = linear_regression_and_plot(intent, company_name)
            fu_year = [item for sublist in future_years for item in sublist]
            response = f"Predicted {intent} for the next 5 years: {fu_year[0]} = {predicted_values[0]}, {fu_year[1]} = {predicted_values[1]}, {fu_year[2]} = {predicted_values[2]}, {fu_year[3]} = {predicted_values[3]}, {fu_year[4]} = {predicted_values[4]}."
            st.image(f"data:image/png;base64,{image_base64}")
            return response            
            
        elif location == "fun_comparative":
            image_base64  =  comparative_analysis(company_name, intent)
            # Check if the result is a message (indicating company not found)
            result = comparative_analysis(company_name, intent)
                # If it's an image, display it and return a response indicating the comparison graph is shown
            image_base64 = result
            st.image(f"data:image/png;base64,{image_base64}")
            return "Above graph shows the comparison between the entered companies."
        
        # calling stock_valuation function
        elif location == "fun_stock":
            response = stock_valuation(company_name, year_name)
            return response
        
        # calling risk
        elif location == "fun_risk":
            response = financial_risk_assessment(company_name, year_name)
            return response
        
        # Calling Capital Budgeting
        elif location == "fun_capital":
            response = perform_capital_budgeting_analysis(company_name, year_name)
            return response
        
        # Calling Should I Invest
        elif location == "fun_invest":
            response = should_invest(company_name)
            return response
        
        else:
            return str(location)
            '''for char in str(location):
                print(char, end='', flush=True)
                time.sleep(0.05)
            print()'''


# Example usage
