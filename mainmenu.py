from tkinter import *

from selectpuzzle import SelectActivity
from activity import Activity


# Main menu activity with a button to start the game
class MainMenuActivity(Activity):

	# class constructor
	def __init__(self, app):
		super().__init__(app)

		# create a canvas for background images
		canvas = Canvas(app.window, width = 600, height = 600)
		canvas.pack()
		self.canvas = canvas

		# start background cycling
		self.currentBackgroundIndex = -1
		self.bgImage = None
		self.nextBackgroundImage()

		# "Puzzle Game" text label
		self.titleLabel = Label(app.window,
			text = 'Puzzle Game',
			fg = 'darkblue',
			font = 'Times 24 italic bold')
		self.titleLabel.place(x = 32, y = 32)

		# start button
		self.btnStart = Button(app.window,
			text = 'Play',
			fg = 'black',
			bg = 'lightgray',
			font = 'Times 18 bold',
			command = self.play)
		self.btnStart.place(x = 10, y = 610, width = 580, height = 50)

	# change window background to the next one in cycling order
	def nextBackgroundImage(self):
		# cycle through puzzle images
		self.currentBackgroundIndex = (self.currentBackgroundIndex + 1) % len(self.app.puzzles)

		if self.canvas.winfo_exists():  # canvas is valid
			if self.bgImage:
				self.canvas.delete(self.bgImage)  # delete the old image

			# create a new image
			self.bgImage = self.canvas.create_image(
				0, 0,  # x and y coordinates
				image = self.app.puzzles[self.currentBackgroundIndex],
				anchor = NW)

		# repeat after 2 seconds
		self.app.window.after(2000, self.nextBackgroundImage)

	# remove widgets created by this activity
	def onRemove(self):
		self.canvas.destroy()
		self.titleLabel.destroy()
		self.btnStart.destroy()

	# "Play" button is pressed
	def play(self):
		self.switchTo(SelectActivity)
