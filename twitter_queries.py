import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import csv 
import numpy as np
from neo4j import GraphDatabase

class Query:
    def __init__(self, uri, user, password) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()
    
    def query_01(self, lb, ub, word):
        with self.driver.session() as session:
            query = "match (t: TWEET)-[CREATED_AT]->(d:DATE)\n" + \
                "where \"" + lb + "\" <= d.name <= \"" + ub + "\"\n" + \
                "MATCH (w:WORD{value:\"" + word + "\"})<-[r:CONTAINS]-(t)\n" + \
                "return count(r)\n"
            result = session.run(query)
            values = []
            # recover the results
            for record in result:
                values.append(record.values())
            # return the results
            print("The word \"{}\" appeared {} times.".format(word, values[0][0]))
        
    def query_02(self, lb, ub):
        with self.driver.session() as session:
            query = "match (t: TWEET)-[CREATED_AT]->(d:DATE)\n" + \
                    "where \"" + lb + "\" <= d.name <= \"" + ub + "\"\n" + \
                    "MATCH (w:WORD)<-[r:CONTAINS]-(t)\n" + \
                    "with w.value as word, count(r) as countIncoming\n" + \
                    "order by countIncoming Desc\n" + \
                    "return word, countIncoming\n"
            result = session.run(query)
            values = []
            # recover the results
            for record in result:
                values.append(record.values())
            # save the results
            csv_file = "csv/q2_{}_{}.csv".format(lb, ub)
            with open(csv_file, "w", newline="", encoding='utf8') as file:
                writer = csv.writer(file)
                writer.writerow(["word", "counter"])
                writer.writerows(values)

    def query_03(self):
        with self.driver.session() as session:
            query = "match (t:TWEET{sponsored:FALSE})\n" +\
                    "match (s:TWEET{sponsored:TRUE})\n" +\
                    "match (s)-[sd:CREATED_AT]->(d:DATE)\n" +\
                    "match (t)-[td:CREATED_AT]->(d:DATE)\n" +\
                    "where sd.topic = td.topic\n" +\
                    "with d.name as date, sd.topic as topic, t.id as tweet_id, t.text as tweet_text\n" +\
                    "order by date asc\n" +\
                    "return date, topic, tweet_id, tweet_text\n"
            result = session.run(query)
            values = []
            # recover the results
            for record in result:
                values.append(record.values())
            # save the results
            csv_file = "csv/q3.csv"
            with open(csv_file, "w", newline="", encoding='utf8') as file:
                writer = csv.writer(file)
                writer.writerow(["date", "topic", "tweet_id", "tweet_text"])
                writer.writerows(values)

    def query_and_build_graph(self, q:int):
        values = {}
        hate_speech_words_by_group = {
            "Racial slurs": ["chink", "slant-eye", "spic", "wetback", "kike", "hebe"],
            "Misogynistic language": ["bitch", "slut", "whore"],
            "Homophobic and transphobic language": ["fag", "dyke", "tranny", "shemale"],
            "Ableist language":  ["retard", "cripple", "invalid"],
            "Fat and Skinny-shaming language" : ["fatso", "lardass", "stick", "beanpole"],
            "Violent language": ["kill", "die", "harm", "hurt", "lazy", "weak"] 
        }
        for group in hate_speech_words_by_group:
            # select the words that will be searched
            hate_speech_words = hate_speech_words_by_group[group]
            hate_speech_words_to_str = "["
            for w in hate_speech_words:
                hate_speech_words_to_str += "\"" + w + "\","
            hate_speech_words_to_str = hate_speech_words_to_str[0:-1] + "]"
            with self.driver.session() as session:
                # build the query
                if q == 4:
                    query = "match (t:TWEET)-[:CREATED_AT]->(d:DATE)\n" + \
                                    "match (w:WORD)<-[r:CONTAINS]-(t)\n" + \
                                    "where w.value in " + hate_speech_words_to_str + "\n" + \
                                    "with d.name as date, count(r) as countIncoming\n" + \
                                    "order by date Asc, countIncoming Asc\n" + \
                                    "return date, countIncoming"
                elif q == 5:
                    query = "match (t:TWEET{sponsored:FALSE})" + "\n" + \
                                    "match (s:TWEET{sponsored:TRUE})" + "\n" + \
                                    "match (s)-[sd:CREATED_AT]->(d:DATE)" + "\n" + \
                                    "match (t)-[td:CREATED_AT]->(d:DATE)" + "\n" + \
                                    "where sd.topic = td.topic" + "\n" + \
                                    "match (w:WORD)<-[r:CONTAINS]-(t)" + "\n" + \
                                    "where w.value in " + hate_speech_words_to_str + "\n" + \
                                    "with d.name as date, count(r) as countIncoming\n" + \
                                    "order by date Asc, countIncoming Asc" + "\n" + \
                                    "return date, countIncoming"
                else:
                    query = "match (n)\nreturn n\n"
                # run the query
                result = session.run(query)
                values[group] = []
                # recover the results
                for record in result:
                    values[group].append(record.values())
        
        # save the results
        csv_file = "csv/q{}.csv".format(q)
        ds = []
        with open(csv_file, "w", newline="", encoding='utf8') as file:
            writer = csv.writer(file)
            writer.writerow(["date", "group", "counter"])
            dates = {}
            for group in values:
                for date, inc in values[group]:
                    if not date in dates:
                        dates[date] = {gp : 0 for gp in values}
                    dates[date][group] += inc
                csv_data = []
                for date in dates:
                    ds.append(date)
                    for group in dates[date]:
                        csv_data.append([date, group, dates[date][group]])
                writer.writerows(csv_data)
    
        # plot the graph
        df = pd.read_csv(csv_file)
        plt.clf()
        plt.figure(figsize=(16, 9))
        ax = sns.lineplot(data=df, x="date", y="counter", hue="group")
        plt.xticks([])
        # sns.move_legend(ax, "upper left", bbox_to_anchor=(1,1))
        plt.title(label="Hate Speech Analysis")
        plt.savefig(csv_file.replace("csv", "png"))

    def query_them_all(self):
        with self.driver.session() as session:
            query = "match (n)\nreturn n\n"
            result = session.run(query)
            values = []
            for record in result:
                values.append(record.values())
            return values

def menu(q:Query):
    while True:
        print("\n##################")
        print("CHOOSE YOUR QUERY:")
        print("##################")
        print("#1 - Count the occurrences of a word between two dates.")
        print("#2 - List all words and their frequencies within a specified date range.")
        print("#3 - Retrieve tweets surrounding sponsored content.")
        print("#4 - Find and visualize the occurrences of a word in a graph.")
        print("#5 - Search for instances of a word in tweets surrounding sponsored content and create a usage graph.")
        print("#6 - Exit.\n")
        option = input()
        if option.isdigit():
            option = int(option)
        else:
            option = -1
        if option == 1:
            print("Please provide the start date in the format YYYY_MM_DD.")
            sd = input()
            print("Please provide the end date in the format YYYY_MM_DD.")
            ed = input()
            print("Please enter the word you want to search for.")
            word = input()
            q.query_01(sd, ed, word)  

        elif option ==  2:
            print("Please provide the start date in the format YYYY_MM_DD.")
            sd = input()
            print("Please provide the end date in the format YYYY_MM_DD.")
            ed = input()
            q.query_02(sd, ed)
       
        elif option ==  3:
            q.query_03()

        elif option ==  4:
            q.query_and_build_graph(option)   

        elif option ==  5:
            q.query_and_build_graph(option)          

        elif option ==  6:
            return
        
        else:
            print("Wrong input!")

if __name__ == "__main__":
    pwd = "abcd1234" #TODO: insert you db passowrd here
    print("Openning connection to the database...")
    q = Query("bolt://localhost:7689", "neo4j", password=pwd)
    menu(q)
    q.close()