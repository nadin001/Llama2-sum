import streamlit as st
import pandas as pd
import ast


csv_file = 'C:/Users/readc/Documents/DEEPlom/resumedataparser/output_data.csv'
df = pd.read_csv(csv_file)

df = df.apply(lambda x: pd.Series(x.dropna().to_numpy()))

df1 = df[df['Skills'].notna()]
df1 = df1[df1['Context'].notna()]
df1 = df1[df1['Text'].notna()]


for str1 in df1["Context"]:
    if not isinstance(str1, str):
        print(str1)


print(df1["Text"])

df1.to_csv("clear.csv")
