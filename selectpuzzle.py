from tkinter import *

from puzzle import PuzzleActivity
from activity import Activity


# Activity for selecting an image for the puzzle
class SelectActivity(Activity):

	# class constructor
	def __init__(self, app):
		super().__init__(app)

		# "Select a puzzle" text label
		self.titleLabel = Label(app.window,
			text = 'Select a puzzle',
			fg = 'darkblue',
			font = 'Times 24 italic bold')
		self.titleLabel.place(x = 32, y = 32)

		# create buttons for all puzzle images
		self.puzzleButtons = []
		for i in range(len(app.puzzles)):
			self.createPuzzleButton(i)

	# helper function to create puzzle image selection buttons
	def createPuzzleButton(self, puzzleIndex):

		# called when the puzzle image is clicked on
		def callback():
			self.switchTo(PuzzleActivity, puzzleIndex)

		b = Button(self.app.window, image = self.app.puzzles[puzzleIndex], command = callback)

		# calculate row and column from array index
		row = puzzleIndex % 3
		column = puzzleIndex // 3

		# set button position
		b.place(
			x = 80 + row * 170,
			y = 150 + column * 170,
			width = 150,
			height = 150)

		# save the newly created button object to remove later
		self.puzzleButtons.append(b)

	# remove widgets created by this activity
	def onRemove(self):
		self.titleLabel.destroy()
		for btn in self.puzzleButtons:
			btn.destroy()