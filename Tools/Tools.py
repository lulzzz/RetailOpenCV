import os
import cv2
import numpy as np
import uuid


def generate_bg_file_unix(dir, filename):
    list_file = os.listdir(dir)
    for i,file in enumerate(list_file):
        line = "./{}/{}\n".format(os.path.basename(dir), file)
        if i%1000 == 0:
            print("{}/{}".format(i,len(list_file)))
        with open(filename, 'a') as f:
            f.write(line.encode("UTF-8"))

def generate_bg_file_win(dir, filename):
    list_file = os.listdir(dir)
    with open(filename, 'a') as f:
        for i,file in enumerate(list_file):
            line = ".\\{}\\{}\n".format(os.path.basename(dir), file)
            if i%1000 == 0:
                print("{}/{}".format(i,len(list_file)))
            f.write(line.encode("UTF-8"))
    
def generate_info_lst_file(dir):
    for i, file in enumerate(os.listdir(dir)):
        if i%1000 == 0:
            print("{}".format(i))
        if file.split(".")[1] == "png":
            img = cv2.imread(os.path.join(dir, file))
            line = "{} 1 0 0 {} {}".format(file, img.shape[1], img.shape[0])
            with open("info.lst", "a") as f:
                f.write(line)

def stat_shape(dir):
    tot = len(os.listdir(dir))
    avg_width = 0
    avg_height = 0
    min_width = 1000000
    min_height = 1000000
    max_width = 0
    max_height = 0
    for i,file in enumerate(os.listdir(dir)):
        path = os.path.join(dir, file)
        img = cv2.imread(path)
        current_width = img.shape[1]
        current_height = img.shape[0]
        avg_width += current_width
        avg_height += current_height

        if current_width > max_width:
            max_width = current_width

        if current_height > max_height:
            max_height = current_height

        if current_width < min_width:
            min_width = current_width

        if current_height < min_height:
            min_height = current_height


        print("{}/{}".format(i,tot))

    print("AVG WTH {} HGT {}".format(avg_width/tot, avg_height/tot))
    print("MIN WTH {} HGT {}".format(min_width, min_height))
    print("MAX WTH {} HGT {}".format(max_width, max_height))



def sort_pos(basedir, approved, rejected):

    for i,test in enumerate(os.listdir(basedir)):
        path = os.path.join(basedir, test)
        img = cv2.imread(path)
        img = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2))
        cv2.imshow("test", img)
        
        while True:
            print(test)

            k = cv2.waitKey(0)        
                
            if k==ord('a'):
                os.rename(os.path.join(basedir, test), os.path.join(approved, test))
                print("{} moved".format(test))
                
                break

            elif k==ord('r'):
                os.rename(os.path.join(basedir, test), os.path.join(rejected, test))
                break
            '''
            elif k==ord('r'):
                os.rename(path.join(basedir, test), path.join(rejected, test))
            '''
            


def convert_to_jpg(source, dest):
    for i,file in enumerate(os.listdir(source)):
        img = cv2.imread(os.path.join(source, file))
        file = file.split('.')[0] + ".jpg"
        cv2.imwrite(os.path.join(dest, file), img)
        if i%100 == 0:
            print(i)


def resize_neg(source, dest, size):
    for i,file in enumerate(os.listdir(source)):
        img = cv2.imread(os.path.join(source, file))
        img = cv2.resize(img, (size, size))
        cv2.imwrite(os.path.join(dest, file), img)
        if i%100 == 0:
            print(i)        


def rename(dir):
    for i,file in enumerate(os.listdir(dir)):
        os.rename(os.path.join(dir, file), os.path.join(dir,"neg_"+str(uuid.uuid4())+".png"))
        if i%1000 == 0:
            print(i)


            
            

def merge_lst_files(dir, dest):
    output = open("info.lst", "a")
    for i,d in enumerate(os.listdir(dir)):
        path = os.path.join(dir, d)
        for j,file in enumerate(os.listdir(path)):
        
            extension = file.split(".")[1]

            if extension == "lst":
                with open(file, "r") as f:
                    output.write(file.read())

            if extension == "png":
                os.rename(os.path.join(path, file), os.path.join(dest, file))



def generate_positve_samples(base_dir, bg_file, img_dir, temp_dir, output_dir, num=20):
    maxxangle = 0.8
    maxyangle = 0.8
    maxzangle = 0.8

    OUTPUT_LINES = []

    liste_img = os.listdir(img_dir)
    
    #mage = os.path.join(img_dir, liste_img[0])

    for image in os.listdir(img_dir):

        if image.split(".")[1] == "png":

            working_dir = os.path.join(temp_dir, image.split(".")[0])
            os.system(".\\bin\\opencv_createsamples.exe -img {} -bg {} -info {} -pngoutput {} -maxxangle {} -maxyangle {} -maxzangle {} -num {}".format(os.path.join(img_dir, image), bg_file, working_dir+'\info.lst', working_dir, maxxangle, maxyangle, maxzangle, num))

            with open(os.path.join(working_dir, "info.lst"), "r") as info_file:
                lines = info_file.readlines()
       
                for line in lines:
                    old_name = line.split(" ")[0]
                    new_name = str(uuid.uuid4())+".jpg"
                    line = line.replace(old_name, new_name)
                    os.rename(os.path.join(working_dir, old_name), os.path.join(output_dir, new_name))
                    OUTPUT_LINES.append(line)
            
    with open(os.path.join(output_dir, "info.lst"), "a") as f:
        for line in OUTPUT_LINES:
            f.write(line)

def sort(dir1, dir2, num):
    list = os.listdir(dir1)
    for i,file in enumerate(list):
        if i > num:
            break   
        if i%1000 == 0:
            print i
        if file.split('.')[1] == "jpg":
            os.rename(os.path.join(dir1, file), os.path.join(dir2, file))

print("Hello World")


#generate_positve_samples("..\\ml", "..\\ml\\bg.txt", "..\\ml\\info", "..\\ml\\temp", "..\\ml\\generation", num=50)
#generate_bg_file_unix("..\\Machine Learning large dataset\\neg", "bgLD.txt")    
#generate_bg_file_unix("..\\Machine Learning large dataset\\down", "bgLD.txt")    

#generate_bg_file("..\\ml\\neg")

sort("..\\Machine Learning large dataset\\down", "..\\Machine Learning large dataset\\down2", 400000)

#stat_shape("..\Machine Learning\car_pos")
#sort_pos("..\Machine Learning\exports", "..\Machine Learning\car_pos2", "..\Machine Learning\car_rej2")
#convert_to_jpg("neg", "neg_jpg")

#resize_neg("neg", "n
#eg_60_60", 60)

#rename("..\\Machine Learning\\neg")\
#generate_info_lst_file("..\\ml\\info")