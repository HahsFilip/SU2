import glob
import os
# import matplotlib.pyplot as plt
class DatSeriesReader:
    extension = ".dat"
    all_data = [] 
    def __init__(self, series_name, t) -> None:
        self.name = series_name
        self.type = t

    def update_files(self):
        time_series = {}
        self.list_of_files = glob.glob(self.name+"*"+self.extension)
        for name in self.list_of_files:
            with open(name, 'r') as file:
                if self.type == 1:
                    lines = file.readlines()
                    if len(lines) == 3:
                        columns = lines[1].split(",")
                        values =  lines[2].split(",")
                        
                        if len(columns) == len(values):                  
                            for i in range(len(columns)):
                                columns[i] = columns[i].replace("\"", "")
                                columns[i] = columns[i].replace(" ", "")
                                columns[i] = columns[i].replace("\n", "")
                                values[i] = values[i].replace(" ", "")
                                values[i] = values[i].replace("\n", "")
                                if  columns[i] not in time_series.keys():
                                    time_series[columns[i]] = []
                                time_series[columns[i]].append(float(values[i])) 
        self.all_data.append(time_series)
    def get_mean(self, field):
        print(len(self.all_data))
        values = []
        mean_value = 0
        for i in range(len(self.all_data)):
            mean_value = 0

            for j in range(len(self.all_data[i][field])):
                mean_value += self.all_data[i][field][j]
            values.append(mean_value/j)
        
        return values
    def remove_files(self):
        for file in self.list_of_files:
            os.remove(file)

def main():

    reader = DatSeriesReader("0_history",1)
    reader.update_files()
    # plt.savefig("matplotlib.png")  #savefig, don't show
    # fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    # ax.scatter(x=reader.all_data[0]["Time_Iter"], y=reader.all_data[0]["CD"])
    # fig.savefig('test.png')   # save the figure to file
    # plt.show(fig) 
    print(reader.get_mean("CD"))
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
            