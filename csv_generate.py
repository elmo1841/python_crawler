import os

final_file_name = "complete_jobs.csv"
final_file_writer = open(final_file_name, 'w')

state_name = 'connecticut, '
city_name = ' '
job = ' '

def create_csv():

    scan = os.scandir(path="complete/Connecticut/")
    for folderName in scan:

        if(skipFolders(folderName.name)):

            length = len(folderName.name)
            city_name = folderName.name[0:length - 1]

            city_path = "complete/Connecticut/" + folderName.name +"/"

            city_scan = os.scandir(path=city_path)
            for jobName in city_scan:

                if(skipFolders(jobName.name)):

                    job_path = "" + city_path + jobName.name
                    job_reader = open(job_path, 'r', encoding='utf-8', errors='ignore')
                    job = job_reader.readlines()
                    job_str = ""
                    for line in job:
                        for i in range(0, len(line)):
                            x = line[i]
                            if(x != '\n' and x != '\r' and x != ','):
                                job_str += x

                    final_file_writer.write(state_name + city_name + ', ' + job_str + '\n')


def skipFolders(folderName):
    if(folderName == "._index.txt" or
    folderName == "index.txt" or
    folderName == "cities.txt" or
    folderName == "errors.txt" or
    folderName == "jobs.txt"):
        return False
    return True




    # for root, dir, files in os.walk("complete/Connecticut/"):
    #     for name in dir:
    #         city_name = name + ', '
    #         print(city_name)
    #         for fileName in files:
    #             print(fileName)
    #             # if fileName == "index.txt" or fileName == "._index.txt" or fileName == "cities.txt" or fileName == "errors.txt":
    #             #     nothing += 1
    #             # else:
    #             #     print(fileName)
    #     #         print(fileName + "-------------------")
    #     #
    #     # # print(dir)
    #     # print(files)


create_csv()
