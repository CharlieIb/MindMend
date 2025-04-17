
# Sample list of symptoms
# symptom_list = [('1','Symptom 1'),('2','Symptom 2'),('3','Symptom 3'),('4','Symptom 4'),('5','Symptom 5'),('6','Symptom 6'),('7','Symptom 7'),('8','Symptom 8'),('9','Symptom 9'),('10','Symptom 10')]
symptom_list = [('1','Excessive Worry/Anxiety'),('2','Panic Attack/Intense Fear'),('3','Fear/Intense Discomfort in Social Settings'),
                 ('4','Avoidance of Social Situations'),('5','Low Mood'),('6','No Enjoyment in Anything'),('7','Low Energy/Fatigue'),
                 ('8','Poor Concentration'),('9','Fluctuating Mood'),('10','Incredibly (unusually) Energetic'),
                 ('11','Intentional Weight Loss (Large Amount)'), ('12','Intense Fear of Weight Gain'), ('13','Very Negative Body Image'),
                 ('14','Trouble Quitting a Substance'), ('15','Physical Self Harm to Oneself')]

SYMPTOM_TO_CONDITION_MAP = {
     '1': [1],      # ex, Symptom #1 triggers Condition #4
     '2': [2],
     '3': [3],
     '4': [3],
     '5': [4,10,11], # Symptom #5 triggers Condition #4, #10, #11
     '6': [4,10,11],
     '7': [4,10,11],
     '8': [1,4,9],
     '9': [10,11],
     '10': [10,11],
     '11': [5,6,7],
     '12': [5,6,7],
     '13': [5,6,7],
     '14': [8],
     '15': [12]
 }


