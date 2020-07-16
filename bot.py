#Chatbot Tutorial with Firebase
#Import Library
import json
import os
from flask import Flask
from flask import request
from flask import make_response

#----Additional from previous file----
from random import randint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("test-bot-xmqalp-firebase-adminsdk-lryb2-fd27e257e0.json")
firebase_admin.initialize_app(cred)
#-------------------------------------

# Flask
app = Flask(__name__)
@app.route('/', methods=['POST']) #Using post as a method

def MainFunction():

    #Getting intent from Dailogflow
    question_from_dailogflow_raw = request.get_json(silent=True, force=True)

    #Call generating_answer function to classify the question
    answer_from_bot = generating_answer(question_from_dailogflow_raw)
    
    #Make a respond back to Dailogflow
    r = make_response(answer_from_bot)
    r.headers['Content-Type'] = 'application/json' #Setting Content Type

    return r

def generating_answer(question_from_dailogflow_dict):

    #Print intent that recived from dialogflow.
    print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))

    #Getting intent name form intent that recived from dialogflow.
    intent_group_question_str = question_from_dailogflow_dict["queryResult"]["intent"]["displayName"] 

    #Select function for answering question
    if intent_group_question_str == 'กินอะไรดี':
        answer_str = menu_recormentation()
    elif intent_group_question_str == 'BMI - Confirmed W and H': 
        answer_str = BMI_calculation(question_from_dailogflow_dict)
    else: answer_str = "ผมไม่เข้าใจ คุณต้องการอะไร"

    #Build answer dict 
    answer_from_bot = {"fulfillmentText": answer_str}
    
    #Convert dict to JSON
    answer_from_bot = json.dumps(answer_from_bot, indent=4) 
    
    return answer_from_bot

def menu_recormentation(): #Function for recommending menu
    #----Additional from previous file----
    database_ref = firestore.client().document('Food/Menu_List')
    database_dict = database_ref.get().to_dict()
    database_list = list(database_dict.values())
    ran_menu = randint(0, len(database_list)-1)
    menu_name = database_list[ran_menu]
    #-------------------------------------
    answer_function = menu_name + ' สิ น่ากินนะ'
    return answer_function

def BMI_calculation(respond_dict): #Function for calculating BMI

    #Getting Weight and Height
    weight_kg = float(respond_dict["queryResult"]["outputContexts"][2]["parameters"]["Weight.original"])
    height_cm = float(respond_dict["queryResult"]["outputContexts"][2]["parameters"]["Height.original"])
    
    #Calculating BMI
    BMI = weight_kg/(height_cm/100)**2
    if BMI < 18.5 :
        answer_function = "คุณผอมเกินไปนะ"
    elif 18.5 <= BMI < 23.0:
        answer_function = "คุณมีนำ้หนักปกติ"
    elif 23.0 <= BMI < 25.0:
        answer_function = "คุณมีนำ้หนักเกิน"
    elif 25.0 <= BMI < 30:
        answer_function = "คุณอ้วน"
    else :
        answer_function = "คุณอ้วนมาก"
    return answer_function

#Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
