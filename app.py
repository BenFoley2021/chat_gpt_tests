import os
import pandas as pd
import openai
from flask import Flask, redirect, render_template, request, url_for
import pickle
from functools import lru_cache
import sys

openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)

@lru_cache()
def query_chatgpt(prompt):
    print('queried openai api', file=sys.stderr)
    return openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        n=1,
        max_tokens=300
    )

class DataFrameFilterer:
    def __init__(self):
        #self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.df = pd.read_csv('consumer_insights_test_data.csv')
        self.used_animals = []
        self.test_prompt = "Write a function to filter a pandas data frame. This function should be named filter_df, and only this function and required imports should be included in the response. These are the columns in the dataframe Creator/Property: string, Views: float, Views Growth: float, Relevance Score: float, Viewing Affinity: float, Audience Overlap: float, Market Share: float. Return the rows in the top 10% of Viewing Affinity where the Views Growth is positive."
        self.read_existing = False
        self.prompt_base = "Write a function to filter a pandas data frame. This function should be named filter_df, and only this function and required imports should be included in the response. These are the columns in the dataframe Creator/Property: string, Views: float, Views Growth: float, Relevance Score: float, Viewing Affinity: float, Audience Overlap: float, Market Share: float. "

    def generate_prompt(self):
        """
            Creates a prompt based on what's currently in the text box
        """
        prompt = self.prompt_base + request.form["query"]
        return prompt

    def process_df(self):
        from filter_func import filter_df
        self.df = filter_df(self.df)

    def save_query_results(self, response):
        with open('response.pckl', 'wb') as file:
            pickle.dump(response, file)
        file.close()

        generated_text = response.choices[0].text.strip()
        f = open("filter_func.py", "w")
        f.write(generated_text)
        f.close()

    def index(self):
        if request.method == "POST":
            #animal = request.form["animal"]
            #self.used_animals.append(animal)
            if not self.read_existing:
                response = query_chatgpt(self.generate_prompt())
                self.save_query_results(response)
            print(f'the prompt is {self.generate_prompt()}')
            print(f'read_existing {self.read_existing}', file=sys.stderr)
            self.process_df()

            return redirect(url_for("index", tables=[self.df.to_html(classes='data')], titles=self.df.columns.values))

        #result = request.args.get("result")
        return render_template("index.html", tables=[self.df.to_html(classes='data')], titles=self.df.columns.values)


app = Flask(__name__)
pet_namer = DataFrameFilterer()

@app.route("/", methods=("GET", "POST"))
def index():
    return pet_namer.index()
