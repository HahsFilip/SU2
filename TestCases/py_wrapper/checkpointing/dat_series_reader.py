import glob
class DatSeriesReader:
    time_series = {}
    extension = ".dat"
    
    def __init__(self, series_name, t) -> None:
        self.name = series_name
        self.type = t
        self.list_of_files = glob.glob(series_name+"*"+self.extension)
        for name in self.list_of_files:
            with open(name, 'r') as file:
                if self.type == 1:
                    lines = file.readlines()
                    columns = lines[1].split(",")
                    values = lines[2].split(",")
                    
                    if len(columns) == len(values):                  
                        for i in range(len(columns)):
                            columns[i] = columns[i].replace("\"", "")
                            columns[i] = columns[i].replace(" ", "")
                            columns[i] = columns[i].replace("\n", "")
                            values[i] = values[i].replace(" ", "")
                            values[i] = values[i].replace("\n", "")
                            if  columns[i] not in self.time_series.keys():
                                self.time_series[columns[i]] = []
                            self.time_series[columns[i]].append(float(values[i])) 

        print(self.time_series)
        pass

def main():
    reader = DatSeriesReader("0_history",1)
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
            