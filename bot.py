# **Chat Bot Start**

# Libraries

from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk
import re
import nltk
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')
import torch
import spacy
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

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


# OUTPUT


def fun_detail(company_name, year_name, intent):
    # code if someone not provide Company name:
    if not company_name:
        return "Can you please provide the company name?"    
    if not year_name:
        return "Can you give me the company year"
    
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
                    value_detail = float(filtered_df_year[intent].iloc[0])  # Assuming 'Revenue' is the column name
                    result.append(str(value_detail))  # Convert value_detail to string
        return result[0] if len(result) == 1 else result  # Return single result or list of results
    
    else:
        # Check if any data is available after filtering
        print("OK")
        if int(year_name) < df['Year'].min() or int(year_name) > df['Year'].max():
            return f"The {company_name_str} company financial report is just available between {df['Year'].min()} to {df['Year'].max()} as the provided year {year_name} is not in our database."
        
        filtered_df_year = filtered_df[filtered_df['Year'] == int(year_name)]
        if filtered_df_year.empty:
            return f"No data available for {company_name_str} in {year_name}."
        
        # Extract the revenue value
        value_detail = float(filtered_df_year[intent].iloc[0])  # Assuming 'Revenue' is the column name
        return str(value_detail)  # Convert value_detail to string


# Function to extract company name and year explicitly from the user question
import string
def extract_company_and_year(sentence):
    # Process the sentence using SpaCy
    doc = nlp(sentence)
    # Extract company name
    companies = [ent.text.upper() for ent in doc.ents if ent.label_ == "ORG"]
    '''for ent in doc.ents:
      print("text",ent.text)
      print("label",ent.label_)
'''
    return companies

# Function to extract company name and year explicitly from the user question
def extract_and_year(sentence):
    # Process the sentence using SpaCy
    doc = nlp(sentence)
    # Extract year and int(token.text) in available_details['Year']
    years = [token.text for token in doc if token.text.isdigit()]
    return  years
import time
def simulate_typing(answer):
    for char in answer:
        print(char, end='', flush=True)
        time.sleep(0.08)  # Adjust the delay (in seconds) as needed
    print()  # Move to the next line after the full answer is printed




def fun_bot(user_question):
#def final(user_question):
#while True:
    response_text =""
    # Get a question from the user
    #user_question = input("USER: ")
    question, location, distance, intent  = Cosine_distance(user_question)

    # Check if the user wants to exit
    if user_question.lower() == "bye":
        return "Goodbye!"
        
      
    else:   
        # Extract company name based on intent
        company_name = extract_company_and_year(user_question)
        # Extract year based on intent
        year_name = extract_and_year(user_question)

        if location == "fun_detail":
            result = fun_detail(company_name, year_name, intent)
            return result
            '''for char in result:
                print(char, end='', flush=True)
                time.sleep(0.05)
            print()'''
        else:
            return str(location)
            '''for char in str(location):
                print(char, end='', flush=True)
                time.sleep(0.05)
            print()'''

# Example usage

