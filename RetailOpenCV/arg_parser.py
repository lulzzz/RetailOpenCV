import argparse



def parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="optional file path to video source or webcam identifier")
    parser.add_argument("-c", "--config", help="choose the set of constants used to detect items on the frame")
    
    return parser.parse_args()
