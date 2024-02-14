
import pickle


data = { "faculty" : ("","") , "dev" : ("","") }
file = "locations_informations/system_data.ai"

with open(file , "wb") as pf:
    pickle.dump(data , pf)

