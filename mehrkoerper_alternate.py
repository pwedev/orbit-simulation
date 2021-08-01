'''
#Desktop\Jens\2021\Softwareprojects\PerPlaneten\mehrkoerper.py
###simulation
planet depiction: fixed 0/0, schwerpunnkt, zoom, verschiebung,
center is center of cords
###interface
offer menu and buttons (start, random (x), add_dot(mass, vx, vy)(no vector), save_inital, clear, load_setup, time_step, framerate
each planet with it's data and a clear button
'''
#libraries
import pygame
import random
import tkinter
import re
import time

import mkp_leapfrog_calc as calc
import numpy as np


#preperations for pygame window
'''
use tkinter to get the size of the screen and set the window to 90% of that value
'''
pygame.init()

root = tkinter.Tk()
root.withdraw()
screen_width = int(root.winfo_screenwidth()*0.9)
screen_height = int(root.winfo_screenheight()*0.9)
screen = pygame.display.set_mode((screen_width, screen_height))

default_values = None

pygame.display.set_caption("Mehrkörpersimulator")
#window_icon = pygame.image.load("icon.png")
#pygame.display.set_icon(window_icon) #add icons fo the for the program hereS

###funtions
class Button:
	def __init__(self, y_pos, width, height, color, text_size, text):
		'''
		y_pos and hight depend on the number of buttons
		width depends on len longest text (calculated before)
		rest depends on the specific button
		'''
		self.y_pos = y_pos
		self.width = width
		self.height = height
		self.color = color
		self.text = text
		self.text_size = text_size

	def depict(self):
		#the box
		screen.fill(self.color, (0, self.y_pos, self.width, abs(self.y_pos-self.height)))
		pygame.draw.rect(screen, (255, 255, 255), (0, self.y_pos+1, self.width-1, abs(self.y_pos-self.height)-1), 3) #fuckery to make the edges fit

		#the text
		font = pygame.font.SysFont("arial", self.text_size)
		button_text = font.render(f"{self.text}", True, (0, 255, 0))
		screen.blit(button_text, (25, int(self.y_pos + int(abs(self.y_pos-self.height)*0.5) - font.size(self.text)[1]*0.5)))

class Planet_Blob:
	'''
	planet blobs will be the graphic layer of the planets
	they get their inital settings from the planet tiles list, later they get the next positions from Pers math
	they save an inital for later reruns, and save up to 300 prior positions for a trail
	each blob has a size (relative to its mass (use the radius mass relationship to get realistic proportions)), a vector (lin or log?), a trail of it prior positions
	'''
	def __init__(self, planet_data, planet_size, pos_scaling):
		#input data
		#planet_data is planet_tile.data (go through the tiles list one by one and convert)
		#planet_size is taken form the list the function generates, pass the right index over
		#the scaling factors are given by their respective functions

		self.designation = planet_data[0]
		self.size = planet_size
		self.pos_x = planet_data[4] * pos_scaling
		self.pos_y = planet_data[5] * pos_scaling
		#self.vel_x = None
		#self.vel_y = None
		self.trail = [[0, 0]] #this is the length of the trail

	def update(self, planet_data, pos_scaling):
		#take the updated data from Per; insert the old pos data into the trail, delete the last entry in the trail;
		#update the pos data

		self.trail.insert(0, [self.pos_x, self.pos_y])
		if len(self.trail) > 3000:
			self.trail = self.trail[:-1]

		self.pos_x = planet_data[4] * pos_scaling
		self.pos_y = planet_data[5] * pos_scaling

	def rescale_trail(self, pos_scaling_new, pos_scaling_old):
		#call this right after the nwe pos scaling has been calculated
		#value/old * new is the relevant formula

		for pos_pair in self.trail:
			pos_pair[0] = pos_pair[0]/pos_scaling_old * pos_scaling_new
			pos_pair[1] = pos_pair[1]/pos_scaling_old * pos_scaling_new

	def depict(self, screen_width, screen_height, menu_data, planet_button_box, planet_tiles):
		#depict trail as a fading line of dots
		#depict the planet blob appropriateley sized
		#subtract the coodinates form half the height and width of the screen

		width_without_menu = screen_width - screen_width+planet_button_box[0] - menu_data[0][0][2] #central spaces x dimension if one calculates out the menus
		#find the virtual (0/0)
		zero_x = int(menu_data[0][0][2] + width_without_menu/2)
		zero_y = int(screen_height/2)

		#trail
		for index, pos in enumerate(self.trail):
			#print(f"{(zero_x+int(pos[0]=)}"), f"{zero_y-int(pos[1])}"))
			#print(f"{zero_x+int(pos[0])=}", f"{zero_y-int(pos[1])=}")
			pygame.draw.line(screen, (255, 255, 255), (zero_x+int(pos[0]), zero_y-int(pos[1])), (zero_x+int(pos[0]), zero_y-int(pos[1])))
		#planet
		#print((self.pos_x, self.pos_y), (screen_width-int(self.pos_x), screen_height-int(self.pos_y)), int(10*self.size))
		pygame.draw.circle(screen, (255, 255, 255), (zero_x+int(self.pos_x), zero_y-int(self.pos_y)), int(50*self.size))

def scaled_planet_sizes(planet_tiles):
	#masses are scaled relative to the biggest and smallest mass involved
	#the biggest one is 100%, the smallest 10% of the max_blob_size
	#scaling is based on the order of magnitudes (convert to string and return len-1)
	planet_sizes = []

	for planet_tile in planet_tiles:
		planet_sizes.append(planet_tile.data[1]) #get the order of magnitudeof the mass

	min_val, max_val = min(planet_sizes), max(planet_sizes)

	#check if min = max and return 1 for all planets t avoid a zerodiv if this is true
	if min_val == max_val:
		for val in planet_sizes:
			val = 1
		return planet_sizes

	#use a linear formula to get percentage values for the rest of the masses
	else:

		#slope = (0.1 - 1) / (min_val - max_val)
		for index, mass in enumerate(planet_sizes):
			planet_sizes[index] = (mass)**(1/5)/(max_val)**(1/5) # 5th or 6th root is good value

		return planet_sizes #returns are 0.1 to 1 of whatever the blobs size is supposed to be

def pos_scaling_factor(screen_width, screen_height, menu_data, planet_button_box, planet_tiles):
	#find the center of the sreen betwenn the button boxes and the hid planet data
	#depict the highest pos value of any planet (x or y) at 0.9 times that diastance, show the others relative to that
		#(either swithch this off after the first round (static window), or leave it on (complete window))

	#menu_data[0][0][3] has the left edge of the screen; planet_button_box[0] has the right edge; 0 and screen_height offer the vertical bounderies

	###this converts blob into screen coordinates
	#see what pos is the maximum value
	max_x, max_y = 0, 0
	for planet in planet_tiles:

		if max_x < abs(planet.data[4]):
			max_x = abs(planet.data[4])
		if max_y < abs(planet.data[5]):
			max_y = abs(planet.data[5])

	##reform and return all the checked values relative to the maximum value as a screenposition
	width_without_menu = screen_width - screen_width+planet_button_box[0] - menu_data[0][0][2] #adjust for menu space

	#adjust the maximum values and see if x or y will determine the scaling (the highest value will always be at 0.9 times the hight of width of the screen)
	scaling_factor = (width_without_menu*0.5*0.75)/max_x #returns the cords as if there is a 0/0 in the screens center
	if (max_y * scaling_factor) > (screen_height*0.5*0.75):
		scaling_factor = (screen_height*0.5*0.75)/max_y
	#print(scaling_factor, screen_width, max_x, max_y)
	return scaling_factor #the scaling factor will only be used to transform the elements for depiction

class Planet_Tile:
	'''
	be the user ínput structure for the planets
	'''
	def __init__(self, instance, entries, text_size, x_start, y_start):
		self.instance = instance #form 1 onwards
		self.entries = entries
		self.text_size = text_size
		self.x_start = x_start
		self.y_start = y_start
		self.calc_object = None

		#vars
		self.font = pygame.font.SysFont("arial", self.text_size)
		self.height = 10 + (self.font.size(f"{entries[0]}")[1]+10)*len(self.entries)

		longest_entry = 0
		for entry in self.entries:
			if longest_entry < self.font.size(entry)[0]:
				longest_entry = self.font.size(entry)[0]
		self.box_x_line = self.x_start + 10 + longest_entry + 10

		self.box_height = self.font.size(entries[0])[1]
		self.box_width = screen_width - self.x_start - 15 - (10 + longest_entry + 10)

		#given data
		self.data = [] #here is all the data about a planet #random offers test data
		for entry in self.entries:
			self.data.append("")

	def give_zones(self):
		#return a list of the relevant zones (first index is the close  botton)
		zones = [(self.x_start, self.y_start+self.height*(self.instance-1), 10, 10)]

		for index, entry in enumerate(self.entries):
			#variable box
			zones.append((self.box_x_line, self.y_start+10 + index*(self.box_height+10)+self.height*(self.instance-1), self.box_width, self.box_height))
		return zones


	def depict(self):
		#the box
		screen.fill((0, 50, 0), (self.x_start, self.y_start+self.height*(self.instance-1), screen_width - self.x_start, self.height))
		pygame.draw.rect(screen, (255, 255, 255), (self.x_start, self.y_start+self.height*(self.instance-1), screen_width - self.x_start, self.height), 1) #fuckery to make the edges fit

		#render the close button
		screen.fill((255, 0, 0), (self.x_start, self.y_start+self.height*(self.instance-1), 10, 10))

		#render each text and its corresponding box_x
		for index in range(len(self.entries)):
			#variable name text
			var_text = self.font.render(f"{self.entries[index]}", True, (0, 255, 0))
			screen.blit(var_text, (self.x_start+10, self.y_start+ 10 + index*(self.box_height+10)+self.height*(self.instance-1)))
			#variable box
			screen.fill((128, 128, 128), (self.box_x_line, self.y_start+10 + index*(self.box_height+10)+self.height*(self.instance-1), self.box_width, self.box_height))
			#variable data
			if self.data[index] != "":
				# TODO: string formatierung
				if index == 0:
					data_text = self.font.render(f"{self.data[index]}", True, (255, 255, 255))
				else:
					window_str = "{:.13}".format(self.data[index])
					if len(window_str) > 13:
						window_str = window_str[0:13]
					data_text = self.font.render(window_str, True, (255, 255, 255))
				screen.blit(data_text, (int(self.box_x_line + self.box_width/2 -  self.font.size(window_str)[0]/2), int(10+self.box_height*1.75+index*(self.box_height+10)+self.height*(self.instance-1))))#
			#grey text for units
			elif index == 0:
				data_text = self.font.render("any name", True, (170, 170, 170))
				screen.blit(data_text, (int(self.box_x_line + self.box_width/2 -  self.font.size("any name")[0]/2), int(10+self.box_height*1.75+index*(self.box_height+10)+self.height*(self.instance-1))))
			elif index == 1:
				data_text = self.font.render("earth masses", True, (170, 170, 170))
				screen.blit(data_text, (int(self.box_x_line + self.box_width/2 -  self.font.size("earth masses")[0]/2), int(10+self.box_height*1.75+index*(self.box_height+10)+self.height*(self.instance-1))))
			elif index in (2, 3):
				data_text = self.font.render("km/s", True, (170, 170, 170))
				screen.blit(data_text, (int(self.box_x_line + self.box_width/2 -  self.font.size("km/s")[0]/2), int(10+self.box_height*1.75+index*(self.box_height+10)+self.height*(self.instance-1))))
			elif index in (4,5):
				data_text = self.font.render("10^6 km", True, (170, 170, 170))
				screen.blit(data_text, (int(self.box_x_line + self.box_width/2 -  self.font.size("10^6 km")[0]/2), int(10+self.box_height*1.75+index*(self.box_height+10)+self.height*(self.instance-1))))

def planet_data_button(data = False):
	'''
	show a small box in the upper right corner, sense an itereaction and set a state variable to true of fales, this determines if the planettiles can be seen
	'''
	font = pygame.font.SysFont("arial", 15)
	#the box
	screen.fill((0, 0, 0), (screen_width-font.size("Hide / Show Planetdata")[0]-80, 0, screen_width, font.size("Hide / Show Planetdata")[0]))
	pygame.draw.rect(screen, (255, 255, 255), (screen_width-font.size("Hide / Show Planetdata")[0]-80, 0+1, screen_width-1, font.size("Hide / Show Planetdata")[1]+15), 3) #fuckery to make the edges fit

	#the text
	button_text = font.render("Hide / Show Planetdata", True, (0, 255, 0))
	screen.blit(button_text, (screen_width-font.size("Hide / Show Planetdata")[0]-40, 6))

	if data:
		return (screen_width-font.size("Hide / Show Planetdata")[0]-80, 0+1, screen_width-1, font.size("Hide / Show Planetdata")[1]+15)

#menu
def menu_init(button_list):
	'''
	###set up all the required buttons
	#get all the required vars form a list of all the buttonnames
	'''
	#vars

	button_list = button_list
	color = (0, 0, 0)
	text_size = 25
	height = int(screen_height / len(button_list)) #depends on the number of buttons
	width = 0 #calculate with font and text_size from the list

	#width
	font = pygame.font.SysFont("arial", text_size)
	for text in button_list:
		if font.size(text)[0] > width:
			width = font.size(text)[0]

	#button_zones
	button_zones = []
	for i in range(0, len(button_list)):
		button_zones.append((0, int(i*height), width+50, int((1+i)*height)))
	button_zones = tuple(button_zones)

	#print((button_zones, color, button_list, text_size))
	return (button_zones, color, button_list, text_size) #return all the relevant information

def draw_menu(buttons):
	'''"Interrupt Simulation", "Reset Simulation", "Add Mass",
	#use interation,the menudata and the buttonobject to make the buttons
	'''
	for button in buttons:
		button.depict()

def start_sim(planet_tiles):
	'''
	transfer the data from the planet tiles to the planet blobs
	disable editing of the tiles completely
	start interacting with Pers software
	convert all the data to floats
	'''

	for planet in planet_tiles:
		for index, value in enumerate(planet.data[1:]):
			planet.data[index+1] = float(value)


	return (True, planet_tiles)
	print("start simulation")



def interrupt_sim(state, button_list):
	'''
	stop interacting with Pers software and keep depicting the current state
	enabele tile enditing
	change button to continue simulation and revert the inital changes
	'''
	print("interrupt simulation")
	#interrruption
	if state != -1:
		state = -1
		button_list = [name if name != "Interrupt Simulation" else "Continue Simulation"for name in button_list] #button_list.replace("Interrupt Simulation", "Continue Simulation")
		return (state, button_list)
	#restart
	state = 2
	button_list = [name if name != "Continue Simulation" else "Interrupt Simulation" for name in button_list ]
	return (state, button_list)


def reset_sim():
	'''
	set the intal_stup of all of the blobs to the current one, wait for start simulation, clear trails
	'''
	print("reset simulation")

def add_mass(planet_tiles, planet_button_box):
	'''
	have an option to hide this data
	generate a tile class, (name, mass, vx, vy) should be avaliable (add option to change this), add a button for removing the tile and its planet,
	add tiles to the top of the screen (keep their dimensions limited), color each tile the same way as the corresponging planet and change the color upon clicking on the color field,
	set up a dynamic and acessible data structure tat can be used by others and keeps the data about the planets
	'''
	global default_values

	planet_tiles.insert(0, Planet_Tile(len(planet_tiles)+1, (f"designation{len(planet_tiles)+1}", "mass", "velocity x", "velocity y", "positon x", "position y"), 15, planet_button_box[0], planet_button_box[3]))

	f = open("default_planets.txt", 'r')
	default_values = np.loadtxt(f, skiprows=1, delimiter='\t',  usecols = (1,2,3,4,5))
	f.close()

	if len(planet_tiles) <= 9:
		planet_tiles[0].data[1] = str(default_values[len(planet_tiles) - 1][4])
		planet_tiles[0].data[2] = str(default_values[len(planet_tiles) - 1][2] / 10**3)
		planet_tiles[0].data[3] = str(default_values[len(planet_tiles) - 1][3] / 10**3)
		planet_tiles[0].data[4] = str(default_values[len(planet_tiles) - 1][0] / 10**9)
		planet_tiles[0].data[5] = str(default_values[len(planet_tiles) - 1][1] / 10**9)



	return planet_tiles

def clear_sim():
	print("clear simulation")

def save_inital():
	print("saving inital")

def depict_all_planets():
	print("depict all planets")
	return True

def automatic_scale():

	global pos_sf, screen_width, screen_height, menu_data, planet_button_box, planet_tiles

	pos_sf = pos_scaling_factor(screen_width, screen_height, menu_data, planet_button_box, planet_tiles)

	print("scale automatically")

def load_setup():
	print("loading setup")

def time_step():
	print("set timestep")

def framerate():
	print("set framerate")

def take_pic():
	print("taking picture")


def main():


	#loop vars
	running = True

	global planet_button_box, planet_tiles, pos_sf

	button_list = ["Start Simulation", "Interrupt Simulation", "Reset Simulation", "Add Mass", "Clear All / New Simulation", "Save Initial", "Load Setup", "Depict All Planets", "Automatic Scale", "Timestep", "Framerate", "Take Picture"]
	show_planets = True
	planet_button_box = planet_data_button(data = True)
	planet_tiles = []
	planet_blob_list = []
	input_pos = (0, 1) #remember the position in  planet_tiles where the user is currently entering data
	sim_runs = 0 #0 is false, 1 is inil with inital actions and 2+ is the normal running state
	rescale_now = True #this will trigger the rescaling of the simulation
	starting_state = []
	planet_sizes = []
	pos_sf = 1

	global menu_data

	frametime = [0,0,0]
	framerate = 0

	timer = pygame.time.Clock()
	game_time = 0


	while running:
		screen.fill((0, 0, 0))
		#interaction
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				running = False
			#MOUSEMOTION  gives the pos of the mouse if it is moved
			#text input for the planets
			if event.type == pygame.KEYDOWN and input_pos != ():
				if event.key == pygame.K_BACKSPACE:
					planet_tiles[input_pos[0]].data[input_pos[1]-1] = planet_tiles[input_pos[0]].data[input_pos[1]-1][:-1]
				else:
					if input_pos[1] == 1:
						planet_tiles[input_pos[0]].data[input_pos[1]-1] += event.unicode
					elif event.unicode in (str(0), str(1), str(2), str(3), str(4), str(5), str(6), str(7), str(8), str(9), ".", "-") and len(planet_tiles[input_pos[0]].data[input_pos[1]-1]) < 13:
						planet_tiles[input_pos[0]].data[input_pos[1]-1] += event.unicode

			#MOUSEBUTTONDOWN gives a reaktion if a button has been used
			if event.type == pygame.MOUSEBUTTONDOWN:
				#menüinteractionen
				mouse_pos = pygame.mouse.get_pos()
				if mouse_pos[0] < menu_data[0][0][2]:
					if mouse_pos[1] > menu_data[0][0][1] and mouse_pos[1] < menu_data[0][0][3]:
						tmp = start_sim(planet_tiles)
						sim_runs = tmp[0]
						planet_tiles = tmp[1]
					if mouse_pos[1] > menu_data[0][1][1] and mouse_pos[1] < menu_data[0][1][3]:
						tmp = interrupt_sim(sim_runs, button_list)
						sim_runs = tmp[0]
						button_list = tmp[1]
					if mouse_pos[1] > menu_data[0][2][1] and mouse_pos[1] < menu_data[0][2][3]:
						reset_sim()
					if mouse_pos[1] > menu_data[0][3][1] and mouse_pos[1] < menu_data[0][3][3]:
						planet_tiles = add_mass(planet_tiles, planet_button_box)
					if mouse_pos[1] > menu_data[0][4][1] and mouse_pos[1] < menu_data[0][4][3]:
						clear_sim()
					if mouse_pos[1] > menu_data[0][5][1] and mouse_pos[1] < menu_data[0][5][3]:
						save_inital()
					if mouse_pos[1] > menu_data[0][6][1] and mouse_pos[1] < menu_data[0][6][3]:
						load_setup()
					if mouse_pos[1] > menu_data[0][7][1] and mouse_pos[1] < menu_data[0][7][3]:
						rescale_now = depict_all_planets()
					if mouse_pos[1] > menu_data[0][8][1] and mouse_pos[1] < menu_data[0][8][3]:
						automatic_scale()
					if mouse_pos[1] > menu_data[0][9][1] and mouse_pos[1] < menu_data[0][9][3]:
						time_step()
					if mouse_pos[1] > menu_data[0][10][1] and mouse_pos[1] < menu_data[0][10][3]:
						framerate()
					if mouse_pos[1] > menu_data[0][11][1] and mouse_pos[1] < menu_data[0][11][3]:
						take_pic()

				#planettiles interactions
				if (mouse_pos[0] > planet_button_box[0] and mouse_pos[0] < planet_button_box[2]) and (mouse_pos[1] > planet_button_box[1] and mouse_pos[1] < planet_button_box[3]):
					show_planets = not show_planets
				#see if any interations with a senetive zone is happening
				edit_happend = False
				if mouse_pos[0] > planet_button_box[0]:
					for tile_index, tile in enumerate(planet_tiles):
						for zone_index, zone in enumerate(tile.give_zones()): #check each tuple of zones, the first one is the closing one

							if (mouse_pos[0] >= zone[0] and mouse_pos[0] <= zone[0]+zone[2]) and (mouse_pos[1] >= zone[1] and mouse_pos[1] <= zone[1]+zone[3]):

								#close button and deletion + reordering
								if zone_index == 0:

									del planet_tiles[tile_index]

									for planet_tile_index, planet_tile in enumerate(planet_tiles):
										if planet_tile.instance != (planet_tile_index + 1):
											planet_tile.instance = planet_tile_index + 1

									edit_happend = True
									break

								#value input
								if zone_index > 0:
									'''
									if input_pos[1] != 1:
									#convert the data to float, unless it is the designation
										try:
											planet_tiles[input_pos[0]].data[input_pos[1]-1] = float(planet_tiles[input_pos[0]].data[input_pos[1]-1])
										except:
											planet_tiles[input_pos[0]].data[input_pos[1]-1] = "" '''

									input_pos = (tile_index, zone_index)


						if edit_happend:
							break


			if event.type == pygame.MOUSEBUTTONUP:
				pass


		#depict the planets
		if sim_runs > 0:
			#check if rescaling was requested and rescale if so
			if rescale_now:
				old_pos_sf = pos_sf

				pos_sf = pos_scaling_factor(screen_width, screen_height, menu_data, planet_button_box, planet_tiles)

				if sim_runs == 2:
					for blob in planet_blob_list:
						blob.rescale_trail(pos_sf, old_pos_sf)

				rescale_now = False
			#see if simruns is on 1 and do initalisation actions (convert planet data to float, get the planet sizes, save the inital setup, initialise the planet blobs, Pers init)
			if sim_runs == 1:



				for planet in planet_tiles:
					starting_state.append(planet.data)

				planet_sizes = scaled_planet_sizes(planet_tiles)

				for index, planet in enumerate(planet_tiles):
					planet_blob_list.append(Planet_Blob(planet.data, planet_sizes[index], pos_sf))

				#initialise planets in calc subprogram
				for planet in planet_tiles:
					planet.calc_object = calc.planet(planet.data[1], planet.data[2] * 0.2108, planet.data[3] * 0.2108, planet.data[4] / 149.598, planet.data[5] / 149.598)

				sim_runs += 1

			#depict the planet blobs (depict func fot the planet blobs?)
			for blob in planet_blob_list:
				blob.depict(screen_width, screen_height, menu_data, planet_button_box, planet_tiles)
				#############################the planet positions are still fine here, next time the values reach this position, they've gone wild (by orders of magnitudes)

			#update the planet data via Pers function planet_tiles[index].data


			for planet in planet_tiles:

				planet.data[2] = planet.calc_object.getVel()[0] / (2.108 * 10**-1)
				planet.data[3] = planet.calc_object.getVel()[1] / (2.108 * 10**-1)
				planet.data[4] = planet.calc_object.getPos()[0] * 149.598
				planet.data[5] = planet.calc_object.getPos()[1] * 149.598

			for planet in planet_tiles:
				calc.calc_step(planet.calc_object)
				planet.calc_object.refresh()


			# frametime[1] = frametime[0]
			# frametime[0] = time.time()
			# frametime[2] = frametime[0] - frametime[1]
			#
			# print(frametime[2]*10**3, " ms")

			#import pdb; pdb.set_trace()

			#update the planet blobs
			for index, blob in enumerate(planet_blob_list):
				blob.update(planet_tiles[index].data, pos_sf)

		#depict all the interactive sections

		menu_data = menu_init(button_list)
		buttons = [Button(menu_data[0][i][1], menu_data[0][i][2], menu_data[0][i][3], menu_data[1], menu_data[3], menu_data[2][i]) for i in range(len(menu_data[0]))] #__init__(self, y_pos, width, height, color, text_size, text)
		draw_menu(buttons)
		planet_data_button()
		if show_planets:
			for planet_tile_index, planet_tile in enumerate(planet_tiles):
				if planet_tile.instance != (planet_tile_index + 1):
					planet_tile.instance = planet_tile_index + 1
			for tile in planet_tiles:
				tile.depict()



		game_time += timer.get_rawtime()
		timer.tick()

		#update screen
		pygame.display.update()







if __name__ == "__main__":
	main()
