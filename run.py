
from flask import Flask, render_template, redirect, send_file
from pymongo import MongoClient
from classes import *
import pandas as pd
import json
from matplotlib import pyplot as plt

# config system
app = Flask(__name__)
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('localhost:27017')
db = client.HeartFailure


def mongoimport(csv_path):
    """ Imports a csv file at path csv_name to a mongo collection
    returns: count of the documents in the new collection
    """
    coll = db.heart_data
    try:
        data = pd.read_csv(csv_path)

    except FileNotFoundError:
        return -1

    payload = json.loads(data.to_json(orient='records'))
    coll.delete_many({})
    coll.insert_many(payload)
    count = coll.count_documents({})
    db.settings.update_one({"name": 'd_id'}, {"$set": {'value': count}})
    print("settings updated")
    return count


if db.settings.count_documents({'name': 'd_id'}) <= 0:
    print("d_id Not found, creating....")
    count = mongoimport("heart.csv")
    db.settings.insert_one({'name': 'd_id', 'value': count})
else:
    count = db.heart_data.count_documents({})
    db.settings.update_one(
        {"name": 'd_id'}, {"$set": {'value': count}})


def updateID():
    count = db.heart_data.count_documents({})
    db.settings.update_one(
        {'name': 'd_id'},
        {'$set':
            {'value': count}
         })
    print("settings updated")


def createEntry(form):
    age = form.age.data
    sex = form.sex.data
    chestPain = form.chestPain.data
    restingBP = form.restingBP.data
    cholesterol = form.cholesterol.data
    maxHeartRate = form.maxHeartRate.data
    restingECG = form.restingECG.data
    exerciseAngina = form.exerciseAngina.data
    heartDisease = form.heartDisease.data

    d_id = db.settings.find_one({})['value']

    d_entry = {'d_id': d_id,
               'Age': age,
               'Sex': sex,
               'ChestPainType': chestPain,
               'RestingBP': restingBP,
               'Cholesterol': cholesterol,
               'MaxHR': maxHeartRate,
               'RestingECG': restingECG,
               'ExerciseAngina': exerciseAngina,
               'HeartDisease': heartDisease}

    db.heart_data.insert_one(d_entry)
    print("inserted heart data")
    updateID()
    return redirect('/')


def deleteEntry(form):
    # TODO Throw error for invalid key
    key = form.key.data
    db.heart_data.delete_one({'d_id': int(key)})

    return redirect('/')


def updateEntry(form):
    # TODO Throw error for invalid key
    key = int(form.key.data)
    if(key != ""):
        prev = db.heart_data.find_one({'d_id': key})
        if(prev == None):
            return redirect('/', code=204)

        u_dict = {}
        if (form["age"].data not in ["", None]):
            u_dict["Age"] = form["age"].data
        if (form["sex"].data not in ["", None]):
            u_dict['Sex'] = form["sex"].data
        if(form["chestPain"].data not in ["", None]):
            u_dict['ChestPainType'] = form["chestPain"].data
        if(form["restingBP"].data not in ["", None]):
            u_dict['RestingBP'] = form["restingBP"].data
        if(form["cholesterol"].data not in ["", None]):
            u_dict['Cholesterol'] = form["cholesterol"].data
        if(form["maxHeartRate"].data not in ["", None]):
            u_dict['MaxHR'] = form["maxHeartRate"].data
        if(form["restingECG"].data not in ["", None]):
            u_dict['RestingECG'] = form["restingECG"].data
        if(form["exerciseAngina"].data not in ["", None]):
            u_dict['ExerciseAngina'] = form["exerciseAngina"].data
        if(form["heartDisease"].data not in ["", None]):
            u_dict['HeartDisease'] = form["heartDisease"].data

        db.heart_data.update_one(
            {"d_id": key},
            {"$set":
                u_dict
             }
        )
        print(f'updated {key}')
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def main():
    cform = CreateEntry(prefix='cform')
    uform = UpdateEntry(prefix='uform')
    dform = DeleteEntry(prefix='dform')

    # response
    if cform.validate_on_submit() and cform.create.data:
        return createEntry(cform)
    if dform.validate_on_submit() and dform.delete.data:
        return deleteEntry(dform)
    if uform.is_submitted() and uform.update.data:  # not validated as non-compulsory fields exist
        return updateEntry(uform)

    # read all data

    docs = db.heart_data.find().sort('d_id', -1).limit(10)  # only the last ten

    data = [i for i in docs]

    return render_template('home.html', cform=cform, dform=dform, uform=uform,
                           data=data, plot1='plot1.png')

# Route for showing pie chart of the types of chest pains and the percentage of each


@app.route("/pie-plot.png")
def plot_png():
    chestpain = db.heart_data.distinct("ChestPainType")
    data = []
    for i in chestpain:
        data.append(db.heart_data.count_documents({"ChestPainType": i}))

    # Creating plot
    explode = (0.05, 0.05, 0.05, 0.05)
    fig = plt.figure(figsize=(6, 4))
    plt.pie(data, labels=chestpain, explode=explode, shadow=True, startangle=90,
            autopct='%1.0f%%', pctdistance=0.5, labeldistance=1.1, textprops={'fontsize': 8})

    # save plot
    plt.title("Types of chest pains")
    plt.savefig('assets/chestpainpie.png')

    return send_file('assets/chestpainpie.png', mimetype="image/png")

# Route to show the no. of people having heart disease categorizes by age


@app.route('/plot.png')
def plot():
    query = db.heart_data.aggregate([
        {"$match": {"HeartDisease": 1}},
        {"$bucket": {
            "groupBy": "$Age",
            "boundaries": [0, 30, 40, 50, 60, 70, 100],
            "default": -1,
            "output": {
                "count": {"$sum": 1}
            }
        }},
        {"$group": {
            "_id": "null",
            "documents": {"$push": {
                "interval": {"$let": {
                    "vars": {
                        "idx": {"$switch": {
                            "branches": [
                                {"case": {"$eq": ["$_id", -1]}, "then": 6},
                                {"case": {"$eq": ["$_id", 0]}, "then": 5},
                                {"case": {"$eq": ["$_id", 30]}, "then": 4},
                                {"case": {"$eq": ["$_id", 40]}, "then": 3},
                                {"case": {"$eq": ["$_id", 50]}, "then": 2},
                                {"case": {"$eq": ["$_id", 60]}, "then": 1},
                                {"case": {"$eq": ["$_id", 70]}, "then": 0},
                            ],
                            "default": 6
                        }}
                    },
                    "in": {"$arrayElemAt": [[">70", "60-70", "50-60", "40-50", "30-40", "<30", "0"], "$$idx"]}
                }},
                "count": "$count",
            }}
        }}
    ])
    x_points = []
    y_points = []
    for i in query:
        for j in i['documents']:
            x_points.append(j['interval'])
            y_points.append(j['count'])

    plt.figure(figsize=(10, 5))
    plt.bar(x_points, y_points, width=0.4)
    ind = range(len(y_points))
    print(ind)
    fig, ax = plt.subplots()
    ax.bar(ind, y_points)
    ax.set_xticks(ind)
    ax.set_xticklabels(x_points)
    ax.bar_label(ax.containers[0])

    plt.xlabel("Age")
    plt.ylabel("No. of people having heart disease")

    plt.title("People having heart Disease")
    plt.savefig("assets/bar.png")
    return send_file("assets/bar.png", mimetype="image/png")


if __name__ == '__main__':
    app.run(debug=True)
