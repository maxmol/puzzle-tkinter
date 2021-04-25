from tkinter import *
import os

from mainmenu import MainMenuActivity


# Game class is used to store configuration and data that is accessible to all activities
class Game:

	# class constructor
	def __init__(self):
		self.title = 'Puzzle'  # game window title
		self.assetsFolder = 'assets/'  # game assets are stored in this folder (e.g. puzzle images)
		self.difficulty = 4  # number of rows and columns of pieces in a puzzle (4 here means the puzzle has 4x4 = 16 pieces)
		self.puzzles = []  # puzzle images from `assetFolder` stored as PhotoImage (from tkinter)
		self.window = None  # Tkinter window

	# create a Tkinter window
	def initTk(self):
		window = Tk()
		window.title(self.title)

		# the game doesn't support adaptive scaling, changing the resolution can lead to broken layout
		window.geometry('600x670')
		window.resizable(False, False)

		self.window = window  # store created window object

		self.fetchPuzzles()

		return window

	# read all images in `Game.assetsFolder` and save them to a list
	def fetchPuzzles(self):
		self.puzzles.clear()

		puzzlesFolder = self.assetsFolder + 'puzzles/'
		for f in os.listdir(puzzlesFolder):
			if f.endswith('.png'):
				img = PhotoImage(file = puzzlesFolder + f)
				img.filepath = puzzlesFolder + f

				self.puzzles.append(img)


def startGame(difficulty):
	app = Game()
	app.difficulty = difficulty
	tkWindow = app.initTk()

	MainMenuActivity(app)  # instantiate Main Menu

	tkWindow.mainloop()  # start tkinter window


if __name__ == '__main__':
	print("Choose difficulty (1-4)")
	difficulty = int(input()) + 1

	# clamp difficulty to 2-5
	difficulty = max(min(difficulty, 5), 2)

	startGame(difficulty)
