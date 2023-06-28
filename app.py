from operator import contains
import os
import pandas as pd
import openai
from flask import Flask, redirect, render_template, request, url_for
import pickle
from functools import lru_cache
import sys
import pandas as pd
import plotly.express as px

openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)

@lru_cache()
def query_chatgpt(prompt):
    print('queried openai api', file=sys.stderr)
    return openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.4,
        n=1,
        max_tokens=300
    )

class DataFrameFilterer:
    def __init__(self):
        #self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.df = pd.read_csv('consumer_insights_test_data.csv').fillna(0)
        #self.test_prompt = "Write a function to filter a pandas data frame. This function should be named filter_df, and only this function and required imports should be included in the response. These are the columns in the dataframe Creator/Property: string, Views: float, Views Growth: float, Relevance Score: float, Viewing Affinity: float, Audience Overlap: float, Market Share: float. Return the rows in the top 10% of Viewing Affinity where the Views Growth is positive."
        self.read_existing = False
        self.behavior = None
        self.module_name = 'local_module.py'
        self.prompt_base_filter = "Write a function to filter a pandas data frame. This function should be named func, and only this function and required imports should be included in the response. These are the columns in the dataframe Creator/Property: string, Views: float, Views Growth: float, Viewing Affinity: float, Audience Overlap: float, Market Share: float. "
        self.prompt_base_plot = "Write a function to return a two dimensional plotly express figure made from a pandas dataframe. The function should be named func and return the figure object. The response should have only this function and necessary imports, do not call func. The dataframe has these columns: Creator: string, Views: float, Views Growth: float, Viewing Affinity: float, Audience Overlap: float, Market Share: float. "


    def generate_prompt(self):
        """
            Creates a prompt based on what's currently in the text box
        """
        user_inputed_prompt = request.form["query"]
        #import pdb;pdb.set_trace()
        if "plot" in user_inputed_prompt or "Plot" in user_inputed_prompt:
            self.behavior = 'plot'
            #import pdb;pdb.set_trace()
            return self.prompt_base_plot + user_inputed_prompt
        else:
            self.behavior = 'filter'
            return self.prompt_base_filter + user_inputed_prompt

    def process_df(self):
        from local_module import func
        self.df = func(self.df)
        del func

    def make_plot(self):
        from local_module import func
        fig = func(self.df)
        fig.show()
        del func

    def save_query_results(self, response):
        with open('response.pckl', 'wb') as file:
            pickle.dump(response, file)
        file.close()

        generated_text = response.choices[0].text.strip()
        # TODO(ben) it would allow more testing flexiblity if the different funcs were saved to different spots
        f = open(self.module_name, "w")
        f.write(generated_text)
        f.close()

    def index(self):
        if request.method == "POST":
            #animal = request.form["animal"]
            #self.used_animals.append(animal)
            if not self.read_existing:
                # query_chatgpt is a pure function so can use lru_cache
                response = query_chatgpt(self.generate_prompt())
                self.save_query_results(response)
            print(f'the prompt is {self.generate_prompt()}')
            print(f'read_existing {self.read_existing}', file=sys.stderr)
            if self.behavior == 'filter':
                self.process_df()
                return redirect(url_for("index", tables=[self.df.to_html(classes='data')], titles=self.df.columns.values))
            else:
                #import pdb;pdb.set_trace()
                self.make_plot()
                return redirect(url_for("index", tables=[self.df.to_html(classes='data')], titles=self.df.columns.values))
        #result = request.args.get("result")
        #import pdb;pdb.set_trace()
        return render_template("index.html", tables=[self.df.to_html(classes='data')], titles=self.df.columns.values)


app = Flask(__name__)
app.config['DEBUG'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = False
pet_namer = DataFrameFilterer()

@app.route("/", methods=("GET", "POST"))
def index():
    return pet_namer.index()
