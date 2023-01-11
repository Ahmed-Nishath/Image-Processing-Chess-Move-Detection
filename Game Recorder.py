import os
import sys
import math
import time
import cv2 as cv
import chess.svg
import webbrowser
import Functions as fun
from tkinter import Tk
from pathlib import Path
from tkinter.filedialog import askdirectory

peices = ['♜', '♘',  '♝', '♕', '♚', '♗', '♞', '♖', '♟', '♙', '♟', '♙', '♜', '♘', '♝', '♔', '♛', '♗', '♞', '♖' ]

board = [[ 'B-R',   'B-N',   'B-B',  'B-Q',   'B-K',  'B-B',  'B-N',  'B-R' ],
                [ 'B-P',   'B-P',   'B-P',   'B-P',   'B-P',   'B-P',  'B-P',  'B-P' ],
                [   'E',        'E',       'E',      'E',       'E',       'E',       'E',     'E'   ],
                [   'E',        'E',       'E',      'E',       'E',       'E',       'E',     'E'   ],
                [   'E',        'E',       'E',      'E',       'E',       'E',       'E',     'E'   ],
                [   'E',        'E',       'E',      'E',       'E',       'E',       'E',     'E'   ],
                [ 'W-P',  'W-P', 'W-P', 'W-P',  'W-P', 'W-P', 'W-P', 'W-P' ],
                [ 'W-R', 'W-N', 'W-B', 'W-Q', 'W-K', 'W-B', 'W-N', 'W-R' ]]

gui_board = chess.Board()
    
descriptive_text = ""
line_number = 0

root=Tk()
root.attributes('-topmost', True)
root.withdraw()

print("\n\n", "_"*40, "----------- CHESS GAMEPLAY RECORDING ----------", sep="\n")
for x in range(20):
    print(f"{peices[x]}", end="")

dis = input("\n\nPlease Select the Data-set container folder. \nPress Enter to Continue\tPress X to Exit  ")
if dis != 'x' and dis != 'X':
    try:
        dataset=askdirectory()
        paths = sorted(Path(dataset).iterdir(), key=os.path.getctime, reverse = True)
        newpath = str(dataset)+"/Chess_Output"
        if os.path.isdir(newpath):
            paths.pop(0)
    except:
        print("Incorrect Dataset!. Please try again with correct Dataset folder.")
        sys.exit()
else:
    print("Good Bye!")
    sys.exit()


if not os.path.exists(newpath):
    os.makedirs(newpath)
    
open(str(newpath)+'/Game_record.txt', 'w').close()
text_file = open(str(newpath)+'/Game_record.txt', 'a')
text_file.write("----------- CHESS GAMEPLAY RECORDING -----------\n")

board_config = cv.imread(str(dataset)+ "/" +str(os.path.basename(paths[0])), 1)
if board_config is None:
    print(f"Image of Empty Board does not exist. Please try again with correct Dataset")
    sys.exit()
coords, frame_config = fun.crop_board(board_config)
empty_boxes = fun.seperate_box(frame_config)
##fun.plot_tiles(empty_boxes)

img_now = cv.imread(str(dataset)+"/" +str(os.path.basename(paths[1])), 1)
if img_now is None:
    print("Image of Complete Board does not exist. Please try again with correct Dataset")
    sys.exit()
frame_now = fun.crop_board_with_coordinates(img_now, coords)

percent = 100/(len(paths)-1)
bar = 21/(len(paths)-1)

print("\nGame processing started...\nPlease wait till all images are being processed")

for i in range(2, len(paths)):
    block = math.ceil(i*bar)
    # print(f"\r [ {str(os.path.basename(paths[i]))} ]     ", u"\u2593"*block, u"\u2591"*(40-block), f"   { math.ceil(i*percent)}% completed\t", end="\t")

    print("\r", "\u2593" * block, u"\u2591" * (21 - block), f"   {math.ceil(i * percent)}% completed     [ {str(os.path.basename(paths[i]))} ]", end="")
    if i==len(paths)-1:
        time.sleep(1)
        print("\r", "\u2593" * block, u"\u2591" * (21 - block))
    frame_prev = frame_now
    isCaptured = False
    
    img_now = cv.imread(str(dataset)+"/" +str(os.path.basename(paths[i])), 1)
    if img_now is None:
        print(f"\nImage \"{str(os.path.basename(paths[i]))}\" does not exist.\nPlease re-check the images and try again.")
        text_file.close()
        sys.exit()
        
    frame_now = fun.crop_board_with_coordinates(img_now, coords)

    thresh = fun.apply_threshold(frame_prev, frame_now)
    boxes_thresh = fun.seperate_box(thresh)

    mv1, mv2 = fun.find_move_boxes(boxes_thresh)

    mv1_box_empty = empty_boxes[mv1[0]][mv1[1]]
    mv2_box_empty = empty_boxes[mv2[0]][mv2[1]]

    boxes_now = fun.seperate_box(frame_now)
    mv1_box_now = boxes_now[mv1[0]][mv1[1]]
    mv2_box_now = boxes_now[mv2[0]][mv2[1]]

    thresh_box_mv1 = fun.move_find_threshold(mv1_box_empty.image, mv1_box_now.image)
    thresh_box_mv2 = fun.move_find_threshold(mv2_box_empty.image, mv2_box_now.image )

    mv1_pixel_value = fun.get_box_pixel_value(thresh_box_mv1)
    mv2_pixel_value = fun.get_box_pixel_value(thresh_box_mv2)

    piece_captured = piece_last_was_at = ""
    if mv1_pixel_value > mv2_pixel_value:
    ##    Moved from mv2 to mv1
        frm = empty_boxes[mv2[0]][mv2[1]].name
        to = empty_boxes[mv1[0]][mv1[1]].name
        
        piece_captured = board[mv1[0]][mv1[1]]
        piece_moved = board[mv2[0]][mv2[1]]
        
        board[mv1[0]][mv1[1]] = board[mv2[0]][mv2[1]]
        board[mv2[0]][mv2[1]] = "E"
        
    else :
        ##    Moved from mv1 to mv2
        frm = empty_boxes[mv1[0]][mv1[1]].name
        to = empty_boxes[mv2[0]][mv2[1]].name
        
        piece_captured = board[mv2[0]][mv2[1]]
        piece_moved = board[mv1[0]][mv1[1]]
        
        board[mv2[0]][mv2[1]] = board[mv1[0]][mv1[1]]
        board[mv1[0]][mv1[1]] = "E"

    if piece_captured == "E":
        move_string = f"{piece_moved} moved from {frm} to {to}"
    else:
        move_string = f"{piece_moved} at {frm} captured {piece_captured}  at {to}"
        isCaptured = True
    try:
        move = chess.Move.from_uci(str(frm+to))
        gui_board.push(move)

    except:
        print(f"\nData set contains snapshot with Illegal move at image \"{str(os.path.basename(paths[i]))}\" \nPlease resolve it and try again.")
        text_file.write("\nIllegal Move Occured\n")
        text_file.close()
        sys.exit()

    if piece_moved[0] == 'W':
        line_number += 1
        text_file.write(fun.record_move(line_number, piece_moved, frm, to, isCaptured, gui_board.is_check()))
    else:
        text_file.write(fun.record_move(-1, piece_moved, frm, to, isCaptured, gui_board.is_check()))
        
    descriptive_text += move_string+"\n"

    if gui_board.is_checkmate():
        print("\n\n", " "*29,"THE GAME OVER")
        
        if i%2==0:
            print(" "*27, "----- White Won -----\n")
            descriptive_text += "--- White Won ---\n"
        else:
            print(" "*27, "----- Black Won -----\n")
            descriptive_text += "--- Black Won ---\n"
        descriptive_text += "--- The Game Finished ---"
        break
    if gui_board.is_stalemate():
        print("\n\n", " "*29, "THE GAME IS DRAW")
        descriptive_text += "--- The Game Finished With Draw ---"
        break
else:
    print("\n\nWarning!. Game not completed proprerly.\n")
    text_file.write("\nWarning!. Game not completed proprerly.\n")
    
board_data = chess.svg.board(gui_board)
output = open(str(newpath) + "/" + str('Game_board'+'.html'), "w")
output.write(board_data)
output.close()

print("All Moves have been recorded on Game_record.txt")
print(" Text file and board are saved at the Dataset folder \nyou have provided")
print("-"*24, "*"*9, "-"*24)

text_file.write("\n\n\n____Moves in understandable format____\n"+ descriptive_text)
text_file.close()
print("  ",end="")
for x in range(20):
    print(f"{peices[x]}", end="")
print("\n\n\n")
webbrowser.open(str(newpath) + '/Game_board.html')

