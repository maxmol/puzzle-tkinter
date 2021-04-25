from tkinter import *
from PIL import ImageTk, Image
from functools import partial
from random import shuffle

import mainmenu
from activity import Activity


# Gameplay activity
class PuzzleActivity(Activity):

	# class constructor
	def __init__(self, app, index):
		super().__init__(app)

		# selected puzzle piece index (-1 : nothing)
		self.selectedPiece = -1

		# randomize puzzle pieces
		self.imageIndex = index
		self.randomizedPieces = list(range(0, self.app.difficulty ** 2))
		shuffle(self.randomizedPieces)

		# load the puzzle image, cut it into pieces and create buttons for each of them.
		pilImage = Image.open(app.puzzles[index].filepath).convert("RGB")
		w, h = pilImage.size
		pieceSize = w / app.difficulty
		self.puzzleImages = [None] * (app.difficulty * app.difficulty)
		self.puzzleButtons = [None] * len(self.puzzleImages)
		i = 0
		for column in range(app.difficulty):
			for row in range(app.difficulty):
				self.createPuzzlePiece(pilImage, i, row, column, pieceSize)
				i += 1

		# "Exit" button (returns to the main menu)
		self.btnExit = Button(self.app.window,
			text = 'Exit',
			fg = 'black',
			bg = 'lightgray',
			font = 'Times 18 bold',
			command = self.exit)
		self.btnExit.place(x = 10, y = 610, width = 280, height = 50)

		# "Autocomplete" button
		self.btnAutocomplete = Button(self.app.window,
			text = 'Autocomplete',
			fg = 'black',
			bg = 'lightgray',
			font = 'Times 18 bold',
			command = self.autocomplete)
		self.btnAutocomplete.place(x = 310, y = 610, width = 280, height = 50)

		# declare a variable for a text label which appears when the player has completed the puzzle
		self.winTextLabel = None

		# declare a variable for background image widget
		self.backgroundWidget = None

		# block user from using buttons after "Autocomplete" button was pressed
		self.blockInput = False

		# a queue data structure that stores tuples of 2 pieces that need to be swapped
		self.autocompleteSwapQueue = None

	# make a puzzle piece button
	def createPuzzlePiece(self, img, i, row, column, pieceSize):

		# calculate row and column for the piece from its index
		randRow = self.randomizedPieces[i] // self.app.difficulty
		randColumn = self.randomizedPieces[i] % self.app.difficulty

		# calculate x, y position for cropping the image
		x = row * pieceSize
		y = column * pieceSize

		# cut a puzzle piece from the image
		pilCropped = img.crop([x, y, x + pieceSize - 4, y + pieceSize - 4])
		self.puzzleImages[i] = ImageTk.PhotoImage(pilCropped)

		# make a button
		piece = Button(self.app.window,
			image = self.puzzleImages[i],
			command = partial(self.clickOnPiece, i),
			bg = 'white',
			borderwidth = 8)
		piece.place(
			x = randRow * pieceSize,
			y = randColumn * pieceSize,
			width = pieceSize,
			height = pieceSize)

		# store current row and column in the button object
		piece.row, piece.column = randRow, randColumn

		# store correct row and column
		piece.rowCorrect = row
		piece.columnCorrect = column

		# save the button for later use and removal
		self.puzzleButtons[i] = piece

	# called when the puzzle piece button is pressed
	def clickOnPiece(self, i):

		# if autocomplete is in progress, don't allow user input
		if self.blockInput:
			return

		if self.selectedPiece == -1:
			# when nothing is selected

			self.selectedPiece = i
			self.puzzleButtons[i].config(bg = "green")
		else:
			btn1 = self.puzzleButtons[self.selectedPiece]

			if self.selectedPiece != i:
				btn2 = self.puzzleButtons[i]

				# check if two puzzle pieces are next to each other
				# (otherwise you can't switch them)
				if self.checkCanSwitch(btn1, btn2):
					btn2.config(bg = "green")
					self.app.window.after(100, self.interchange, btn1, btn2)
				else:
					btn1.config(bg = "red")
					btn2.config(bg = "red")
					self.app.window.after(150, self.resetColors, btn1, btn2)

			else:
				# clicked on the same piece twice
				btn1.config(bg = "white")

			# cancel selection
			self.selectedPiece = -1

	@staticmethod
	def resetColors(btn1, btn2 = None):
		btn1.config(bg = "white")
		if btn2:
			btn2.config(bg = "white")

	@staticmethod
	def checkCanSwitch(btn1, btn2):
		aboveOrBelow = btn1.row == btn2.row and abs(btn1.column - btn2.column) == 1
		leftOrRight = btn1.column == btn2.column and abs(btn1.row - btn2.row) == 1

		return aboveOrBelow or leftOrRight

	# swap two pieces
	def interchange(self, btn1, btn2):
		x1, y1 = btn1.winfo_x(), btn1.winfo_y()
		x2, y2 = btn2.winfo_x(), btn2.winfo_y()

		moveX = x2 - x1
		moveY = y2 - y1

		btn1.row, btn2.row = btn2.row, btn1.row
		btn1.column, btn2.column = btn2.column, btn1.column

		self.interchangeStep(btn1, x1, y1, btn2, x2, y2, moveX, moveY, 1)

		if self.checkCorrectness():
			self.app.window.after(300, self.win)

	# pieces swapping animation
	def interchangeStep(self, btn1, x1, y1, btn2, x2, y2, moveX, moveY, i):
		if btn1.winfo_exists() and btn2.winfo_exists():
			btn1.place(
				x = x1 + moveX * i / 10,
				y = y1 + moveY * i / 10)

			btn2.place(
				x = x2 - moveX * i / 10,
				y = y2 - moveY * i / 10)

			if i == 10:
				# end 10-frame animation
				btn1.config(bg = "white")
				btn2.config(bg = "white")
			else:
				# repeat until i is 10
				self.app.window.after(20, self.interchangeStep, btn1, x1, y1, btn2, x2, y2, moveX, moveY, i + 1)

	# checks if the puzzle is completed
	def checkCorrectness(self):
		for piece in self.puzzleButtons:
			if piece.row != piece.rowCorrect or piece.column != piece.columnCorrect:
				return False

		return True

	# generate a queue of swaps needed to complete the puzzle
	def computeAutocomplete(self):
		size = self.app.difficulty

		# initialize two-dimensional cache arrays for faster access to each current and correct positions in the puzzle
		positionsCache = [None] * size
		correctPositionsCache = [None] * size

		for i in range(size):
			positionsCache[i] = [None] * size
			correctPositionsCache[i] = [None] * size

		for piece in self.puzzleButtons:
			positionsCache[piece.row][piece.column] = piece
			correctPositionsCache[piece.rowCorrect][piece.columnCorrect] = piece

			# make additional fields in the piece button widget to store virtual position during the calculation
			piece.tempRow = piece.row
			piece.tempColumn = piece.column

		# FIFO queue for swaps
		swapQueue = []

		# inline function for virtual swapping
		def swapPieces(piece1, piece2):
			# save to queue
			swapQueue.append((piece1, piece2))

			# interchange positions
			piece1.tempRow, piece2.tempRow = piece2.tempRow, piece1.tempRow
			piece1.tempColumn, piece2.tempColumn = piece2.tempColumn, piece1.tempColumn
			positionsCache[piece1.tempRow][piece1.tempColumn] = piece1
			positionsCache[piece2.tempRow][piece2.tempColumn] = piece2

		# complete the puzzle by moving pieces to their correct position one by one from top left to bottom right
		for column in range(size):
			for row in range(size):
				piece = correctPositionsCache[row][column]

				if piece == None:
					continue

				# move to correct row
				horizontalDelta = piece.rowCorrect - piece.tempRow
				while horizontalDelta != 0:
					if horizontalDelta > 0:
						swapPieces(piece, positionsCache[piece.tempRow + 1][piece.tempColumn])
						horizontalDelta -= 1
					else:
						swapPieces(piece, positionsCache[piece.tempRow - 1][piece.tempColumn])
						horizontalDelta += 1

				# move to correct column
				verticalDelta = piece.columnCorrect - piece.tempColumn
				while verticalDelta != 0:
					if verticalDelta > 0:
						swapPieces(piece, positionsCache[piece.tempRow][piece.tempColumn + 1])
						verticalDelta -= 1
					else:
						swapPieces(piece, positionsCache[piece.tempRow][piece.tempColumn - 1])
						verticalDelta += 1

		# save final result
		self.autocompleteSwapQueue = swapQueue

	def autocomplete(self):

		# stop user interaction
		self.blockInput = True

		# generate a queue of individual steps only once
		if self.autocompleteSwapQueue == None:
			self.computeAutocomplete()

		# actually move the puzzle pieces
		if len(self.autocompleteSwapQueue) > 0:
			pieces = self.autocompleteSwapQueue.pop(0)
			self.interchange(pieces[0], pieces[1])
			self.app.window.after(350, self.autocomplete)


	# called after the puzzle was completed
	def win(self):

		# remove all pieces
		for piece in self.puzzleButtons:
			piece.destroy()

		# and place a full image instead
		self.backgroundWidget = Label(self.app.window, image = self.app.puzzles[self.imageIndex])
		self.backgroundWidget.place(x = 0, y = 0)

		# win text label
		self.winTextLabel = Label(self.app.window,
			text = 'Good job!',
			fg = 'darkblue',
			font = 'Times 24 italic bold'
		)
		self.winTextLabel.place(x = 32, y = 32)

	# remove widgets created by this activity
	def onRemove(self):
		for piece in self.puzzleButtons:
			piece.destroy()

		if self.backgroundWidget:
			self.backgroundWidget.destroy()
		if self.winTextLabel:
			self.winTextLabel.destroy()
		if self.btnAutocomplete:
			self.btnAutocomplete.destroy()
		if self.btnExit:
			self.btnExit.destroy()

	def exit(self):
		self.switchTo(mainmenu.MainMenuActivity)
