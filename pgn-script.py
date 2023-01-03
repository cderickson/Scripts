import pandas as pd
import os
import pickle
from datetime import datetime

piece_dict = {}
lines_list_info = []
lines_list_moves = []
full_table = []
pgn_file_list = []
type_dict = {}

def pgn_header():
	header = []
	header.extend([
		"Match_ID",
		"W_Name",
		"W_Elo",
		"B_Name",
		"B_Elo",
		"ECO",
		"Date",
		"Time",
		"W_Result",
		"B_Result",
		"Time_Control",
		"Location",
		"Event",
		"Round_Num"
	])
	header.extend([
		"Move_Num",
		"Turn_Num",
		"Move_Color",
		"Piece_Code",
		"PGN_Notation",
		"Piece_Type",
		"End_Square_x",
		"End_Square_y",
		"Ambig_ID",
		"Castle",
		"Castle_Long",
		"Capture",
		"In_Check",
		"Checkmate",
		"Promote",
		"Promote_Piece"
	])
	for i in piece_code_list():
		header.extend([f"{i}_White_x", f"{i}_White_y", f"{i}_White_isPinned", f"{i}_White_squaresControlled"])
	for i in piece_code_list():
		header.extend([f"{i}_Black_x", f"{i}_Black_y", f"{i}_Black_isPinned", f"{i}_Black_squaresControlled"])
	header.extend(["pieceValueWhite", "pieceValueBlack", "totalSquaresControlledWhite", "totalSquaresControlledBlack"])
	return header
def piece_code_list():
	return [
		"P1",
		"P2",
		"P3",
		"P4",
		"P5",
		"P6",
		"P7",
		"P8",
		"R1",
		"R2",
		"N1",
		"N2",
		"B1",
		"B2",
		"Q1",
		"K1",
		"X1",
		"X2",
		"X3",
		"X4",
		"X5",
		"X6",
		"X7",
		"X8",
	]
def char_to_int(char):
	x_dict = {
		"a" : 1,
		"b" : 2,
		"c" : 3,
		"d" : 4,
		"e" : 5,
		"f" : 6,
		"g" : 7,
		"h" : 8,
	}
	return x_dict[char]	
def convert_to_xy(char_int):
	x_dict = {
		"a" : 1,
		"b" : 2,
		"c" : 3,
		"d" : 4,
		"e" : 5,
		"f" : 6,
		"g" : 7,
		"h" : 8,
	}
	return (x_dict[char_int[0]], int(char_int[1]))
def piece_dict_init():
	w = {
		"P1" : {
			"piece_type" : "P",
			"square" : (1, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P2" : {
			"piece_type" : "P",
			"square" : (2, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P3" : {
			"piece_type" : "P",
			"square" : (3, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P4" : {
			"piece_type" : "P",
			"square" : (4, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P5" : {
			"piece_type" : "P",
			"square" : (5, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P6" : {
			"piece_type" : "P",
			"square" : (6, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P7" : {
			"piece_type" : "P",
			"square" : (7, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P8" : {
			"piece_type" : "P",
			"square" : (8, 2),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"R1" : {
			"piece_type" : "R",
			"square" : (1, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"N1" : {
			"piece_type" : "N",
			"square" : (2, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"B1" : {
			"piece_type" : "B",
			"square" : (3, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"Q1" : {
			"piece_type" : "Q",
			"square" : (4, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"K1" : {
			"piece_type" : "K",
			"square" : (5, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"B2" : {
			"piece_type" : "B",
			"square" : (6, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"N2" : {
			"piece_type" : "N",
			"square" : (7, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"R2" : {
			"piece_type" : "R",
			"square" : (8, 1),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "white",
			"is_promoted_piece" : False,
			"is_pinned" : False
		}
	}
	b = {
		"P1" : {
			"piece_type" : "P",
			"square" : (1, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P2" : {
			"piece_type" : "P",
			"square" : (2, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P3" : {
			"piece_type" : "P",
			"square" : (3, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P4" : {
			"piece_type" : "P",
			"square" : (4, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P5" : {
			"piece_type" : "P",
			"square" : (5, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P6" : {
			"piece_type" : "P",
			"square" : (6, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P7" : {
			"piece_type" : "P",
			"square" : (7, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"P8" : {
			"piece_type" : "P",
			"square" : (8, 7),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"R1" : {
			"piece_type" : "R",
			"square" : (1, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"N1" : {
			"piece_type" : "N",
			"square" : (2, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"B1" : {
			"piece_type" : "B",
			"square" : (3, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"Q1" : {
			"piece_type" : "Q",
			"square" : (4, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"K1" : {
			"piece_type" : "K",
			"square" : (5, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"B2" : {
			"piece_type" : "B",
			"square" : (6, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"N2" : {
			"piece_type" : "N",
			"square" : (7, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		},
		"R2" : {
			"piece_type" : "R",
			"square" : (8, 8),
			"legal_moves" : [],
			"legal_captures" : [],
			"color" : "black",
			"is_promoted_piece" : False,
			"is_pinned" : False
		}
	}
	return {
		"white" : w,
		"black" : b
	}
def split_pgn_file(filename):
	global lines_list_info
	global lines_list_moves

	with open(filename) as f:
		lines = f.read()

	lines = lines.split("\n\n")
	for index,i in enumerate(lines):
		if (index % 2) == 0:
			lines_list_info.append(i)
		else:
			lines_list_moves.append(i)
def get_move_lists_from_pgn(lines):
	#with open(filename) as f:
	#	lines = f.read()

	white_moves = []
	black_moves = []
	combined_moves = []
	move_string = ""

	white_player = "NA"
	black_player = "NA"
	white_elo = 0
	black_elo = 0
	eco = "NA"
	date = "NA"
	time = "NA"
	result_white = 0.0
	result_black = 0.0
	time_control = 0
	location = "NA"
	event = "NA"
	round_num = 0

	for i in lines.split("\n"):
		if len(i) > 0:
			if i[0] != "[":
				move_string += f" {i}"
			else:
				info_string = i.split("[")[1].split("]")[0]
				info_val = info_string.split("\"")[1]
				info_string = info_string.split("\"")[0].strip()
				#print(info_string + " " + info_val)

				if info_string == "White":
					white_player = info_val
				elif info_string == "Black":
					black_player = info_val
				elif info_string == "WhiteElo":
					white_elo = int(info_val)
				elif info_string == "BlackElo":
					black_elo = int(info_val)
				elif info_string == "Site":
					location = info_val
				elif info_string == "Event":
					event = info_val
				elif info_string == "Round":
					if (info_val != "?") and (info_val != "-"):
						round_num = info_val
				elif info_string == "Date":
					date = info_val.replace(".","-")
				elif info_string == "EndTime":
					time = info_val.split(" ")[0]
					if len(time) == 7:
						time = "0" + time
				elif info_string == "Result":
					if info_val == "1-0":
						result_white = 1.0
						result_black = 0.0
					elif info_val == "0-1":
						result_white = 0.0
						result_black = 1.0
					elif info_val == "1/2-1/2":
						result_white = 0.5
						result_black = 0.5
				elif info_string == "ECO":
					eco = info_val
				elif info_string == "TimeControl":
					time_control = int(info_val)

	turn = "white"
	for i in move_string.split(" "):
		if len(i) == 0:
			pass
		elif i.find(".") != -1:
			pass
		elif i == "1-0":
			# white wins
			pass
		elif i == "0-1":
			# black wins
			pass
		elif i == "1/2-1/2":
			# draw
			pass
		elif turn == "white":
			white_moves.append(i)
			combined_moves.append(i)
			turn = "black"
		elif turn == "black":
			black_moves.append(i)
			combined_moves.append(i)
			turn = "white"
	info_list = [
		f"{date}_{time}_{white_player}_{black_player}",
		white_player,
		white_elo,
		black_player,
		black_elo,
		eco,
		date,
		time,
		result_white,
		result_black,
		time_control,
		location,
		event,
		round_num
	] 

	return (combined_moves, info_list)
def is_white_occupied(square):
	for i in piece_dict["white"]:
		if piece_dict["white"][i]["square"] == square:
			return True
	return False
def is_black_occupied(square):
	for i in piece_dict["black"]:
		if piece_dict["black"][i]["square"] == square:
			return True
	return False
def is_enemy_occupied(square,ally_color):
	if ally_color == "white":
		if is_black_occupied(square):
			return True
	elif ally_color == "black":
		if is_white_occupied(square):
			return True
def is_ally_occupied(square,ally_color):
	if ally_color == "white":
		if is_white_occupied(square):
			return True
	elif ally_color == "black":
		if is_black_occupied(square):
			return True	
def legal_moves(piece,color,x,y):
	squares_list = []
	capture_list = []

	def evaluate_square(x,y,color):
		if is_enemy_occupied((x,y),color):
			capture_list.append((x,y))
			squares_list.append((x,y))
			return "break"
		elif is_ally_occupied((x,y),color):
			return "break"
		else:
			squares_list.append((x,y))
	def evaluate_pawn_capture_square(x,y,color):
		if is_enemy_occupied((x,y),color):
			capture_list.append((x,y))
	def evaluate_pawn_move_square(x,y,color):
		if is_enemy_occupied((x,y),color):
			pass
		elif is_ally_occupied((x,y),color):
			pass
		else:
			squares_list.append((x,y))
			return "check_next"
	def check_rook_moves():
		x_new = x
		while (x_new < 8):
			x_new += 1
			if evaluate_square(x_new,y,color) == "break":
				break
		x_new = x
		while (x_new > 1):
			x_new -= 1
			if evaluate_square(x_new,y,color) == "break":
				break
		y_new = y
		while (y_new < 8):
			y_new += 1
			if evaluate_square(x,y_new,color) == "break":
				break
		y_new = y
		while (y_new > 1):
			y_new -= 1
			if evaluate_square(x,y_new,color) == "break":
				break
	def check_knight_moves():
		x_new = x
		y_new = y
		if x < 7:
			x_new += 2
			if y < 8:
				y_new += 1
				evaluate_square(x_new,y_new,color)
				y_new = y
			if y > 1:
				y_new -= 1
				evaluate_square(x_new,y_new,color)
				y_new = y
			x_new = x
		if x > 2:
			x_new -= 2
			if y < 8:
				y_new += 1
				evaluate_square(x_new,y_new,color)
				y_new = y
			if y > 1:
				y_new -= 1
				evaluate_square(x_new,y_new,color)
				y_new = y
			x_new = x
		if y < 7:
			y_new += 2
			if x < 8:
				x_new += 1
				evaluate_square(x_new,y_new,color)
				x_new = x
			if x > 1:
				x_new -= 1
				evaluate_square(x_new,y_new,color)
				x_new = x
			y_new = y
		if y > 2:
			y_new -= 2
			if x < 8:
				x_new += 1
				evaluate_square(x_new,y_new,color)
				x_new = x
			if x > 1:
				x_new -= 1
				evaluate_square(x_new,y_new,color)
				x_new = x
	def check_bishop_moves():
		x_new = x
		y_new = y
		while (x_new < 8) and (y_new < 8):
			x_new += 1
			y_new += 1
			if evaluate_square(x_new,y_new,color) == "break":
				break
		x_new = x
		y_new = y
		while (x_new > 1) and (y_new < 8):
			x_new -= 1
			y_new += 1
			if evaluate_square(x_new,y_new,color) == "break":
				break
		x_new = x
		y_new = y
		while (x_new > 1) and (y_new > 1):
			x_new -= 1
			y_new -= 1
			if evaluate_square(x_new,y_new,color) == "break":
				break
		x_new = x
		y_new = y
		while (x_new < 8) and (y_new > 1):
			x_new += 1
			y_new -= 1
			if evaluate_square(x_new,y_new,color) == "break":
				break
	def check_king_moves():
		x_new = x
		y_new = y
		if x < 8:
			x_new += 1
			evaluate_square(x_new,y,color)
			if y < 8:
				y_new += 1
				evaluate_square(x_new,y_new,color)
				y_new = y
			if y > 1:
				y_new -= 1
				evaluate_square(x_new,y_new,color)
		x_new = x
		y_new = y
		if x > 1:
			x_new -= 1
			evaluate_square(x_new,y,color)
			if y < 8:
				y_new += 1
				evaluate_square(x_new,y_new,color)
				y_new = y
			if y > 1:
				y_new -= 1
				evaluate_square(x_new,y_new,color)
		x_new = x
		y_new = y
		if y < 8:
			y_new += 1
			evaluate_square(x,y_new,color)
			y_new = y
		if y > 1:
			y_new -= 1
			evaluate_square(x,y_new,color)
			y_new = y

	if piece == "R":
		check_rook_moves()
	elif piece == "N":
		check_knight_moves()
	elif piece == "B":
		check_bishop_moves()
	elif piece == "Q":
		check_rook_moves()
		check_bishop_moves()
	elif piece == "K":
		check_king_moves()
	elif piece == "P":
		if color == "white":
			if y == 2:
				if evaluate_pawn_move_square(x,3,color) == "check_next":
					evaluate_pawn_move_square(x,4,color)
			else:
				evaluate_pawn_move_square(x,y+1,color)
			if x > 1:
				evaluate_pawn_capture_square(x-1,y+1,color)
			if x < 8:
				evaluate_pawn_capture_square(x+1,y+1,color)
		elif color == "black":
			if y == 7:
				if evaluate_pawn_move_square(x,6,color) == "check_next":
					evaluate_pawn_move_square(x,5,color)
			else:
				evaluate_pawn_move_square(x,y-1,color)
			if x > 1:
				evaluate_pawn_capture_square(x-1,y-1,color)
			if x < 8:
				evaluate_pawn_capture_square(x+1,y-1,color)
	return (squares_list, capture_list)
def update_moves_captures(pd):
	p_dict = pd
	for i in piece_dict["white"]:
		x = legal_moves(p_dict["white"][i]["piece_type"],p_dict["white"][i]["color"],p_dict["white"][i]["square"][0],p_dict["white"][i]["square"][1])
		p_dict["white"][i]["legal_moves"] = x[0]
		p_dict["white"][i]["legal_captures"] = x[1]
	for i in piece_dict["black"]:
		x = legal_moves(p_dict["black"][i]["piece_type"],p_dict["black"][i]["color"],p_dict["black"][i]["square"][0],p_dict["black"][i]["square"][1])
		p_dict["black"][i]["legal_moves"] = x[0]
		p_dict["black"][i]["legal_captures"] = x[1]
	return p_dict
def update_pins(pd):
	p_dict = pd

	def check_linear(x,y):
		linear1 = []
		linear2 = []
		linear3 = []
		linear4 = []

		x_new = x
		while (x_new < 8):
			empty_square = True
			x_new += 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x_new,y):
					linear1.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x_new,y):
					linear1.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				linear1.append((x_new,y))
		x_new = x
		while (x_new > 1):
			empty_square = True
			x_new -= 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x_new,y):
					linear2.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x_new,y):
					linear2.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				linear2.append((x_new,y))
		y_new = y
		while (y_new < 8):
			empty_square = True
			y_new += 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x,y_new):
					linear3.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x,y_new):
					linear3.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				linear3.append((x,y_new))
		y_new = y
		while (y_new > 1):
			empty_square = True
			y_new -= 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x,y_new):
					linear4.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x,y_new):
					linear4.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				linear4.append((x,y_new))
		return [linear1,linear2,linear3,linear4]
	def check_diag(x,y):
		diag1 = []
		diag2 = []
		diag3 = []
		diag4 = []

		x_new = x
		y_new = y
		while (x_new < 8) and (y_new < 8):
			empty_square = True
			x_new += 1
			y_new += 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x_new,y_new):
					diag1.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x_new,y_new):
					diag1.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				diag1.append((x_new,y_new))
		x_new = x
		y_new = y
		while (x_new > 1) and (y_new < 8):
			empty_square = True
			x_new -= 1
			y_new += 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x_new,y_new):
					diag2.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x_new,y_new):
					diag2.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				diag2.append((x_new,y_new))
		x_new = x
		y_new = y
		while (x_new > 1) and (y_new > 1):
			empty_square = True
			x_new -= 1
			y_new -= 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x_new,y_new):
					diag3.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x_new,y_new):
					diag3.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				diag3.append((x_new,y_new))
		x_new = x
		y_new = y
		while (x_new < 8) and (y_new > 1):
			empty_square = True
			x_new += 1
			y_new -= 1
			for i in p_dict["white"]:
				if p_dict["white"][i]["square"] == (x_new,y_new):
					diag4.append(p_dict["white"][i])
					empty_square = False
					break
			for i in p_dict["black"]:
				if p_dict["black"][i]["square"] == (x_new,y_new):
					diag4.append(p_dict["black"][i])
					empty_square = False
					break
			if empty_square == True:
				diag4.append((x_new,y_new))
		return [diag1, diag2, diag3, diag4]
	def evaluate_linear_path(path_list,color):
		pinned_list = []
		pinned_path_list = []
		pinner_list = []

		for i in path_list:
			ally_blockers = 0
			enemy_blockers = 0
			pinner_found = 0
			path_to_pin = []
			for j in i:
				if isinstance(j,tuple):
					path_to_pin.append(j)
					continue
				if j["color"] == color:
					ally_blockers += 1
					pinned = j
				elif j["color"] != color:
					if (j["piece_type"] == "R") or (j["piece_type"] == "Q"):
						pinner_found += 1
						pinner = j["square"]
						break
					else:
						enemy_blockers += 1
						break
			if (ally_blockers == 1) and (enemy_blockers == 0) and (pinner_found == 1):
				pinned_list.append(pinned)
				pinned_path_list.append(path_to_pin)
				pinner_list.append(pinner)
		return (pinned_list, pinned_path_list, pinner_list)
	def evaluate_diag_path(path_list,color):
		pinned_list = []
		pinned_path_list = []
		pinner_list = []

		for i in path_list:
			ally_blockers = 0
			enemy_blockers = 0
			pinner_found = 0
			path_to_pin = []
			for j in i:
				if isinstance(j,tuple):
					path_to_pin.append(j)
					continue
				if j["color"] == color:
					ally_blockers += 1
					pinned = j
				elif j["color"] != color:
					if (j["piece_type"] == "B") or (j["piece_type"] == "Q"):
						pinner_found += 1
						pinner = j["square"]
						break
					else:
						enemy_blockers += 1
						break
			if (ally_blockers == 1) and (enemy_blockers == 0) and (pinner_found == 1):
				pinned_list.append(pinned)
				pinned_path_list.append(path_to_pin)
				pinner_list.append(pinner)
		return (pinned_list, pinned_path_list, pinner_list)
	def get_white_pins():
		a = evaluate_linear_path(check_linear(p_dict["white"]["K1"]["square"][0], p_dict["white"]["K1"]["square"][1]),"white")
		b = evaluate_diag_path(check_diag(p_dict["white"]["K1"]["square"][0], p_dict["white"]["K1"]["square"][1]),"white")
		return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
	def get_black_pins():
		a = evaluate_linear_path(check_linear(p_dict["black"]["K1"]["square"][0], p_dict["black"]["K1"]["square"][1]),"black")
		b = evaluate_diag_path(check_diag(p_dict["black"]["K1"]["square"][0], p_dict["black"]["K1"]["square"][1]),"black")
		return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

	white_pins = get_white_pins()
	black_pins = get_black_pins()

	for index,i in enumerate(white_pins[0]):
		for j in p_dict["white"]:
			if p_dict["white"][j]["square"] == i["square"]:
				p_dict["white"][j]["legal_moves"] = list(set(p_dict["white"][j]["legal_moves"]).intersection(set(white_pins[1][index])))
				p_dict["white"][j]["legal_captures"] = list(set(p_dict["white"][j]["legal_captures"]).intersection(set([white_pins[2][index]])))
				p_dict["white"][j]["is_pinned"] = True
			else:
				p_dict["white"][j]["is_pinned"] = False

	for index,i in enumerate(black_pins[0]):
		for j in p_dict["black"]:
			if p_dict["black"][j]["square"] == i["square"]:
				p_dict["black"][j]["legal_moves"] = list(set(p_dict["black"][j]["legal_moves"]).intersection(set(black_pins[1][index])))
				p_dict["black"][j]["legal_captures"] = list(set(p_dict["black"][j]["legal_captures"]).intersection(set([black_pins[2][index]])))
				p_dict["black"][j]["is_pinned"] = True
			else:
				p_dict["black"][j]["is_pinned"] = False

	return p_dict
def parse_move(string,color):
	x = string

	move_dict = {
		"piece_type" : "NA",
		"end_square" : (),
		"ambig_id" : "NA",
		"castle" : False,
		"castle_long" : False,
		"capture" : False,
		"check" : False,
		"checkmate" : False,
		"promote" : False,
		"promote_piece" : "NA",
		"pgn" : x
	}

	if x.find("+") != -1:
		move_dict["check"] = True
		x = x.replace("+","")
	if x.find("#") != -1:
		move_dict["checkmate"] = True
		x = x.replace("#","")
	if x.find("=") != -1:
		move_dict["promote"] = True
		move_dict["promote_piece"] = x.split("=")[1]
		x = x.split("=")[0]
	if x.find("x") != -1:
		move_dict["capture"] = True
		x = x.replace("x","")
	if x == "O-O":
		move_dict["castle"] = True
		x = x.replace("O-O","")
		if color == "white":
			pass
		elif color == "black":
			pass
	elif x == "O-O-O":
		move_dict["castle_long"] = True
		x = x.replace("O-O-O","")
		if color == "white":
			pass
		elif color == "black":
			pass
	elif x[0].isupper():
		move_dict["piece_type"] = x[0]
		x = x.replace(x[0],"")
		move_dict["end_square"] = convert_to_xy(x[-2:])
		x = x[:-2]
		move_dict["ambig_id"] = x
	elif x[0].islower():
		move_dict["piece_type"] = "P"
		move_dict["end_square"] = convert_to_xy(x[-2:])
		x = x[:-2]
		move_dict["ambig_id"] = x
	if move_dict["ambig_id"] == "":
		move_dict["ambig_id"] = "NA"
	return move_dict
def run_moveset(moveset):
	def get_list_of_poss_pieces(turn,move_dict):
		piece_list = []
		for i in piece_dict[turn]:
			if move_dict["piece_type"] == piece_dict[turn][i]["piece_type"]:
				if move_dict["capture"] == True:
					if move_dict["end_square"] in piece_dict[turn][i]["legal_captures"]:
						piece_list.append(i)
				else:
					if move_dict["end_square"] in piece_dict[turn][i]["legal_moves"]:
						piece_list.append(i)
		return piece_list
	def get_captured_piece(turn,move_dict):
		if turn == "white":
			for i in piece_dict["black"]:
				if piece_dict["black"][i]["square"] == move_dict["end_square"]:
					return i
			if (move_dict["piece_type"] == "P") and (move_dict["end_square"][1] == 6):
				for i in piece_dict["black"]:
					if (piece_dict["black"][i]["piece_type"] == "P") and (piece_dict["black"][i]["square"] == (move_dict["end_square"][0],5)):
						return i
		elif turn == "black":
			for i in piece_dict["white"]:
				if piece_dict["white"][i]["square"] == move_dict["end_square"]:
					return i
			if (move_dict["piece_type"] == "P") and (move_dict["end_square"][1] == 3):
				for i in piece_dict["white"]:
					if (piece_dict["white"][i]["piece_type"] == "P") and (piece_dict["white"][i]["square"] == (move_dict["end_square"][0],4)):
						return i
	def check_ambiguity(turn,piece_list,move_dict):
		ambig_id = move_dict["ambig_id"]
		if ambig_id == "NA":
			print("ambig_id == NA")
		elif (len(ambig_id) == 1) and (ambig_id.isnumeric()):
			ambig = int(ambig_id)
			for i in piece_list:
				if piece_dict[turn][i]["square"][1] == ambig:
					return i
		elif (len(ambig_id) == 1) and (ambig_id.isnumeric() == False):
			ambig = char_to_int(ambig_id)
			for i in piece_list:
				if piece_dict[turn][i]["square"][0] == ambig:
					return i
		elif len(ambig_id) == 2:
			ambig = convert_to_xy(ambig_id)
			for i in piece_list:
				if piece_dict[turn][i]["square"] == ambig:
					return i
	def append_castle(turn):
		if turn == "white":
			record.append([
				move_num,
				turn_num,
				turn, 
				"K1",
				move_dict["pgn"],
				piece_dict["white"]["K1"]["piece_type"],
				piece_dict["white"]["K1"]["square"][0],
				piece_dict["white"]["K1"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
			record.append([
				move_num + 1,
				turn_num,
				turn, 
				"R2",
				move_dict["pgn"],
				piece_dict["white"]["R2"]["piece_type"],
				piece_dict["white"]["R2"]["square"][0],
				piece_dict["white"]["R2"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
		elif turn == "black":
			record.append([
				move_num,
				turn_num,
				turn, 
				"K1",
				move_dict["pgn"],
				piece_dict["black"]["K1"]["piece_type"],
				piece_dict["black"]["K1"]["square"][0],
				piece_dict["black"]["K1"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
			record.append([
				move_num + 1,
				turn_num,
				turn, 
				"R2",
				move_dict["pgn"],
				piece_dict["black"]["R2"]["piece_type"],
				piece_dict["black"]["R2"]["square"][0],
				piece_dict["black"]["R2"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
	def append_castle_long(turn):
		if turn == "white":
			record.append([
				move_num,
				turn_num,
				turn, 
				"K1",
				move_dict["pgn"],
				piece_dict["white"]["K1"]["piece_type"],
				piece_dict["white"]["K1"]["square"][0],
				piece_dict["white"]["K1"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
			record.append([
				move_num + 1,
				turn_num,
				turn, 
				"R1",
				move_dict["pgn"],
				piece_dict["white"]["R1"]["piece_type"],
				piece_dict["white"]["R1"]["square"][0],
				piece_dict["white"]["R1"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
		elif turn == "black":
			record.append([
				move_num,
				turn_num,
				turn, 
				"K1",
				move_dict["pgn"],
				piece_dict["black"]["K1"]["piece_type"],
				piece_dict["black"]["K1"]["square"][0],
				piece_dict["black"]["K1"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
			record.append([
				move_num + 1,
				turn_num,
				turn, 
				"R1",
				move_dict["pgn"],
				piece_dict["black"]["R1"]["piece_type"],
				piece_dict["black"]["R1"]["square"][0],
				piece_dict["black"]["R1"]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])
	def check_if_doublemove(turn,original_square,end_square):
		if turn == "white":
			if (end_square[1] - original_square[1]) == 2:
				return True
		elif turn == "black":
			if (original_square[1] - end_square[1]) == 2:
				return True
		return False

	global piece_dict
	piece_dict = piece_dict_init()
	piece_dict = update_moves_captures(piece_dict)

	table = []

	double_move = False
	turn = "white"
	move_num = 0
	turn_num = 0
	promote_counts = {
		"white" : 0,
		"black" : 0
	}
	for i in moveset:
		record = []
		game_state = []
		move_num += 1
		if turn == "white":
			turn_num += 1

		move_dict = parse_move(i,turn)
		if move_dict["castle"] == True:
			if turn == "white":
				piece_dict["white"]["K1"]["square"] = convert_to_xy("g1")
				piece_dict["white"]["R2"]["square"] = convert_to_xy("f1")
			elif turn == "black":
				piece_dict["black"]["K1"]["square"] = convert_to_xy("g8")
				piece_dict["black"]["R2"]["square"] = convert_to_xy("f8")
			append_castle(turn)
			move_num += 1
		elif move_dict["castle_long"] == True:
			if turn == "white":
				piece_dict["white"]["K1"]["square"] = convert_to_xy("c1")
				piece_dict["white"]["R1"]["square"] = convert_to_xy("d1")
			elif turn == "black":
				piece_dict["black"]["K1"]["square"] = convert_to_xy("c8")
				piece_dict["black"]["R1"]["square"] = convert_to_xy("d8")
			append_castle_long(turn)
			move_num += 1
		
		piece_list = get_list_of_poss_pieces(turn,move_dict)

		if len(piece_list) == 1:
			piece = piece_list[0]
			original_square = piece_dict[turn][piece]["square"]
			if move_dict["piece_type"] == "P":
				double_move = check_if_doublemove(turn,original_square,move_dict["end_square"])
			piece_dict[turn][piece]["square"] = move_dict["end_square"]
		elif len(piece_list) > 1:
			piece = check_ambiguity(turn,piece_list,move_dict)
			original_square = piece_dict[turn][piece]["square"]
			if move_dict["piece_type"] == "P":
				double_move = check_if_doublemove(turn,original_square,move_dict["end_square"])
			piece_dict[turn][piece]["square"] = move_dict["end_square"]
		else:		
			pass
			#print("no possible pieces found (probably castled)")

		if len(piece_list) > 0:
			record.append([
				move_num,
				turn_num,
				turn,
				piece,
				move_dict["pgn"],
				piece_dict[turn][piece]["piece_type"],
				piece_dict[turn][piece]["square"][0],
				piece_dict[turn][piece]["square"][1],
				move_dict["ambig_id"],
				move_dict["castle"],
				move_dict["castle_long"],
				move_dict["capture"],
				move_dict["check"],
				move_dict["checkmate"],
				move_dict["promote"],
				move_dict["promote_piece"]
			])

		if move_dict["capture"] == True:
			if turn == "white":
				del piece_dict["black"][get_captured_piece(turn,move_dict)]
			elif turn == "black":
				del piece_dict["white"][get_captured_piece(turn,move_dict)]

		if move_dict["promote"] == True:
			promote_counts[turn] += 1
			del piece_dict[turn][piece]
			piece_dict[turn]["X" + piece[1]] = {
				"piece_type" : move_dict["promote_piece"],
				"square" : move_dict["end_square"],
				"legal_moves" : [],
				"legal_captures" : [],
				"color" : turn,
				"is_promoted_piece" : True,
				"is_pinned" : False
			}

		piece_dict = update_moves_captures(piece_dict)
		piece_dict = update_pins(piece_dict)

		if double_move == True:
			pawns_to_ep = []
			if move_dict["end_square"][0] > 1:
				pawns_to_ep.append((move_dict["end_square"][0] - 1, move_dict["end_square"][1]))
			if move_dict["end_square"][0] < 8:
				pawns_to_ep.append((move_dict["end_square"][0] + 1, move_dict["end_square"][1]))
			if turn == "white":
				ep_square = (move_dict["end_square"][0], move_dict["end_square"][1] - 1)
				for piece in piece_dict["black"]:
					if (piece_dict["black"][piece]["square"] in pawns_to_ep) and (piece_dict["black"][piece]["piece_type"] == "P"):
						piece_dict["black"][piece]["legal_captures"].extend([ep_square])
			elif turn == "black":
				ep_square = (move_dict["end_square"][0], move_dict["end_square"][1] + 1)
				for piece in piece_dict["white"]:
					if (piece_dict["white"][piece]["square"] in pawns_to_ep) and (piece_dict["white"][piece]["piece_type"] == "P"):
						piece_dict["white"][piece]["legal_captures"].extend([ep_square])
			double_move = False

		white_piece_value = 0
		black_piece_value = 0
		white_squares_controlled = 0
		black_squares_controlled = 0
		for piece in piece_code_list():
			try:
				game_state.extend([
					piece_dict["white"][piece]["square"][0],
					piece_dict["white"][piece]["square"][1],
					piece_dict["white"][piece]["is_pinned"],
					len(piece_dict["white"][piece]["legal_moves"]) + len(piece_dict["white"][piece]["legal_captures"])
				])
				if piece_dict["white"][piece]["piece_type"] == "P":
					white_piece_value += 1
				elif (piece_dict["white"][piece]["piece_type"] == "N") or (piece_dict["white"][piece]["piece_type"] == "B"):
					white_piece_value += 3
				elif piece_dict["white"][piece]["piece_type"] == "R":
					white_piece_value += 5
				elif piece_dict["white"][piece]["piece_type"] == "Q":
					white_piece_value += 9
				white_squares_controlled += (len(piece_dict["white"][piece]["legal_moves"]) + len(piece_dict["white"][piece]["legal_captures"]))
			except KeyError:
				game_state.extend([0,0,False,0])

		for piece in piece_code_list():
			try:
				game_state.extend([
					piece_dict["black"][piece]["square"][0],
					piece_dict["black"][piece]["square"][1],
					piece_dict["black"][piece]["is_pinned"],
					len(piece_dict["black"][piece]["legal_moves"]) + len(piece_dict["black"][piece]["legal_captures"])
				])
				if piece_dict["black"][piece]["piece_type"] == "P":
					black_piece_value += 1
				elif (piece_dict["black"][piece]["piece_type"] == "N") or (piece_dict["black"][piece]["piece_type"] == "B"):
					black_piece_value += 3
				elif piece_dict["black"][piece]["piece_type"] == "R":
					black_piece_value += 5
				elif piece_dict["black"][piece]["piece_type"] == "Q":
					black_piece_value += 9
				black_squares_controlled += (len(piece_dict["black"][piece]["legal_moves"]) + len(piece_dict["black"][piece]["legal_captures"]))
			except KeyError:
				game_state.extend([0,0,False,0])

		game_state.extend([white_piece_value, black_piece_value, white_squares_controlled, black_squares_controlled])

		for rec in record:
			rec.extend(game_state)

		table.extend(record)

		if turn == "white":
			turn = "black"
		else:
			turn = "white"
	return table
def add_info_cols(info_list,table):
	for index,i in enumerate(table):
		table[index] = info_list + i
	return table
def get_pgn_file_list():
	global pgn_file_list
	for i in os.listdir():
		if ".pgn" in i:
			pgn_file_list.append(i)
def split_all_pgn():
	for i in pgn_file_list:
		split_pgn_file(i)
def execute(pgn_path, output_path, start_date, save_cols):
	global full_table

	def to_datetime(x):
	    return datetime.strptime(x, "%Y-%m-%d")

	curr_path = os.getcwd()
	os.chdir(pgn_path)
	get_pgn_file_list()
	split_all_pgn()

	for index,i in enumerate(lines_list_info):
		moveset_all, info_list = get_move_lists_from_pgn(lines_list_info[index] + "\n" + lines_list_moves[index])

		table = run_moveset(moveset_all)
		table = add_info_cols(info_list,table)

		full_table.extend(table)
		print(len(full_table))

	os.chdir(output_path)
	df = pd.DataFrame(columns=pgn_header(), data=full_table)
	df['ECO'] = df['ECO'].fillna('NA')
	df['Location'] = df['Location'].fillna('NA')
	df['Event'] = df['Event'].fillna('NA')
	df['Ambig_ID'] = df['Ambig_ID'].fillna('NA')
	df['Promote_Piece'] = df['Promote_Piece'].fillna('NA')
	if start_date != 'All':
		df = df[df.Date.apply(to_datetime) >= start_date]
	df.drop(['Match_ID'], axis=1).to_csv("chesspgn_moves.csv", index=False)

	if save_cols == True:
		for index,i in enumerate(full_table[0]):
			chars = 0
			can_be_null = False
			if type(i) == str:
				if pgn_header()[index] in ['W_Name', 'B_Name', 'ECO', 'Date', 'Time', 'Location', 'Event']:
					chars = 40
				elif pgn_header()[index] == 'Match_ID':
					chars = 100
				else:
					chars = 10
			if pgn_header()[index] in ['ECO', 'Location', 'Event', 'Ambig_ID', 'Promote_Piece']:
				can_be_null = True
			type_dict[pgn_header()[index]] = (type(i), chars, can_be_null)
		pickle.dump(type_dict,open("pgn_col_types","wb"))

pgn_path = 'C:\\Users\\chris\\Documents\\Datasets\\Chess PGN\\pgn_files'
output_path = 'G:\\My Drive\\Datasets\\Chess PGN'
start_date = '2022-05-01'
start_date = datetime.strptime(start_date, "%Y-%m-%d")

execute(pgn_path=pgn_path, output_path=output_path, start_date='All', save_cols=False)