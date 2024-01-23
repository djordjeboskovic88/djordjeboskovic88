import time
import random
import threading
from flask import Flask



class RouletteWheelSimulation():
    def __init__(self, wheel_type, phase_duration, tick_duration):
        self.wheel_type_list = ["FrenchSingleZero", "EruopeanSingleZero", "AmericanDoubleZero"]
        self.wheel_type = wheel_type

        if self.wheel_type == "FrenchSingleZero" or "EruopeanSingleZero":
            self.hits_list = [0 for _ in range(37)]
            self.numbers = [f"Number_{i}" for i in range(0,37)]
        if self.wheel_type == "AmericanDoubleZero":
            self.hits_list = [0 for _ in range(38)]
            self.numbers = ["Number_0", "Number_1", "Number_2", "Number_3", "Number_4", "Number_5", "Number_6", "Number_7", "Number_8", "Number_9", "Number_10", "Number_11", "Number_12", "Number_13", "Number_14", "Number_15", "Number_16", "Number_17", "Number_18", "Number_19", "Number_20", "Number_21", "Number_22", "Number_23", "Number_24", "Number_25", "Number_26", "Number_27", "Number_28", "Number_29", "Number_30", "Number_31", "Number_32", "Number_33", "Number_34", "Number_35", "Number_36", "Number_00"]


        self.json_out = {"game_nmb":1,"game_duration":None,"phase_tick_count":0,"last_number_list":[],"status":"NoError","max_nr":len(self.numbers),"wheel_type":self.wheel_type,"statistics":{"hit_count":0,"hits":self.hits_list,"even_chance_count":0,"even_chances":{"black":0,"even":0,"high_number":0,"low_number":0,"odd":0,"red":0,"zero":0}},"colds":[{"number":None,"hits":0},{"number":None,"hits":0},{"number":None,"hits":0},{"number":None,"hits":0},{"number":None,"hits":0}],"hots":[{"number":None,"hits":0},{"number":None,"hits":0},{"number":None,"hits":0},{"number":None,"hits":0},{"number":None,"hits":0}]}

        self.win_nmbr_list = []

        self.phases = ["BeforeGame", "PlaceBets", "FinishBets", "NoMoreBets", "StartRun", "Running", "WinningNumber", "WinCelebration", "Finished"]
        self.phases_before_win_nmbr = ["BeforeGame", "PlaceBets", "FinishBets", "NoMoreBets", "StartRun", "Running"]
        self.phases_left = []

        self.black = [15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20, 31, 22, 29, 28, 35, 26]
        self.red   = [32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14, 9, 18, 7, 12, 3]
        self.even  = [i for i in range(1,37,2)]
        self.odd   = [i for i in range(2,37,2)]
        self.low   = [i for i in range(1,19)]
        self.high  = [i for i in range(19,37)]

        self.ticks = 0

        self.win_nmbr = random.choice(self.numbers)

        self.phase_duration = phase_duration  # ticks

        self.game_duration = self.phase_duration * len(self.phases)

        self.tick_duration = tick_duration  # milisekundi

        self.five_max_nmbr  = [0,0,0,0,0]
        self.five_min_nmbr  = [0,0,0,0,0]


    def wining_number_list(self):
        self.win_nmbr_list.insert(0,self.win_nmbr)
        if len(self.win_nmbr_list) > 10:
            self.win_nmbr_list.pop()


    def five_min_and_max_nmbr(self):
        self.index_value = list(enumerate(self.hits_list))
        self.index_value.sort(key=lambda x: x[1], reverse=True)
        self.index_five_max = [indeks for indeks, _ in self.index_value[:5]]
        self.index_five_min = [indeks for indeks, _ in self.index_value[-5:]]
        self.a = 0
        self.b = 0
        for i in self.index_five_max:
            self.five_max_nmbr[self.a] = {"number": self.numbers[i],"hits":self.hits_list[i]}
            self.a+=1
        for i in self.index_five_min:
            self.five_min_nmbr[self.b] = {"number":self.numbers[i],"hits":self.hits_list[i]}
            self.b+=1
        self.json_out["hots"] = self.five_max_nmbr
        self.json_out["colds"] = self.five_min_nmbr


    def hits_add(self, win_nmbr_str):
        win_nmbr_int = self.numbers.index(win_nmbr_str)
        self.hits_list[win_nmbr_int] +=1


    def even_add(self):
        if self.numbers.index(self.win_nmbr) in self.black:
            self.json_out["statistics"]["even_chances"]["black"] += 1
        if self.numbers.index(self.win_nmbr) in self.red:
            self.json_out["statistics"]["even_chances"]["red"] += 1
        if self.numbers.index(self.win_nmbr) in self.even:
            self.json_out["statistics"]["even_chances"]["even"] += 1
        if self.numbers.index(self.win_nmbr) in self.odd:
            self.json_out["statistics"]["even_chances"]["odd"] += 1
        if self.numbers.index(self.win_nmbr) in self.low:
            self.json_out["statistics"]["even_chances"]["low_number"] += 1
        if self.numbers.index(self.win_nmbr) in self.high:
            self.json_out["statistics"]["even_chances"]["high_number"] += 1
        if self.numbers.index(self.win_nmbr) == 0:
            self.json_out["statistics"]["even_chances"]["zero"] += 1
        if self.numbers.index(self.win_nmbr) == 37:
            if "doublezero" not in self.json_out["statistics"]["even_chances"]:
                self.json_out["statistics"]["even_chances"]["doublezero"] = 1
            else:
                self.json_out["statistics"]["even_chances"]["doublezero"] += 1
        self.json_out["statistics"]["even_chance_count"] += 1


    def end_phase_excution(self):
        self.json_out["game_nmb"] += 1
        self.hits_add(self.win_nmbr)
        self.json_out["statistics"]["hits"] = self.hits_list
        self.json_out["statistics"]["hit_count"] += 1
        self.even_add()
        self.wining_number_list()
        self.json_out["last_number_list"] = self.win_nmbr_list
        self.five_min_and_max_nmbr()


    def phase_excution(self):
        if self.ticks == 0:
            self.phases_left = self.phases
        if self.ticks % self.phase_duration == 0:
            self.phases_left = self.phases_left[1:]
            self.json_out["phase_tick_count"] = 0
            if len(self.phases_left) == 0:
                self.phases_left = self.phases
                self.end_phase_excution()
                self.win_nmbr = random.choice(self.numbers)

            self.json_out["phase"] = self.phases_left[0]

        self.json_out["game_duration"] = self.game_duration
        self.json_out["tick_duration"] = self.tick_duration
        self.json_out["phase_duration"] = self.phase_duration
        self.json_out["phase_tick_count"] += 1
        self.ticks+=1


    def winning_number(self):
        if self.json_out["phase"] in self.phases_before_win_nmbr:
            self.json_out["win_nr"] = "Unknown"
        if self.json_out["phase"] == "WinningNumber":
            self.json_out["win_nr"] = self.win_nmbr


    def tick_count(self):
        if "tick_count" not in self.json_out:
            self.json_out["tick_count"] = 1
        else:
            self.json_out["tick_count"] += 1


    #-------------------------------------------------------------------------------------------------------------------------------------------#
    def roll(self):
        self.phase_excution()
        self.winning_number()
        self.tick_count()
    #-------------------------------------------------------------------------------------------------------------------------------------------#
    def main(self):
        try:
            while True:
                self.roll()
                time.sleep(self.tick_duration * 0.001)
                # time.sleep(0)
                # print(self.json_out)
        except:
            self.json_out["status"] = "error"
            print(self.json_out)
    #-------------------------------------------------------------------------------------------------------------------------------------------#




#-----------------------------------------------------------------------------------------#

# PARAMETERS 
# 1. wheel_type     - "FrenchSingleZero", "EruopeanSingleZero", "AmericanDoubleZero"
# 2. phase_duration -  number of ticks in one phase
# 3. tick_duration  -  in miliseconds
roulette = RouletteWheelSimulation("AmericanDoubleZero", 5, 100)

#-----------------------------------------------------------------------------------------#

rsim = threading.Thread(target=roulette.main)

#-----------------------------------------------------------------------------------------#

# FLASK SERVER /rsim:
web_server = Flask("Roulette Wheel Simulation")

@web_server.route("/rsim")
def out():
    return roulette.json_out

#-----------------------------------------------------------------------------------------#


if __name__ == "__main__":
    rsim.start()
    web_server.run()




