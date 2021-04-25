# Base class for all activities (user interface pages)
class Activity:

	# class constructor
	def __init__(self, app):
		self.app = app

	# close this activity and open another one
	def switchTo(self, activityClass, *args):
		self.onRemove()

		activityClass(self.app, *args)

	# abstract method which is called before the activity is removed
	# all tkinter widgets created by the activity must be removed here
	def onRemove(self):
		pass
