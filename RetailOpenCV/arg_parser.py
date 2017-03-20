import argparse



def parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="optional file path to video source or webcam identifier")

    return parser.parse_args()
