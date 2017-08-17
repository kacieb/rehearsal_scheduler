# AUTHOR AND CODE INFORMATION
# Author: Kacie Bawiec
# Title: Rehearsal Scheduler (scheduler.py)
# Created: August 2017
# Purpose: The purpose of this code is to create a rehearsal scheduler that
#	will account for actor conflicts and scene lengths, and generate a working
#	schedule.

# -----------------------------------------------------------------------------
# ^ max length of a line

# Notes About Code:
#	HOW TO USE is located at the bottom, including an example.
#	Currently, the user needs to create Scene objects and the Calendar object,
#		but does all scheduling actions through the Scheduler class.
#	Master "Scheduler" class has access to both the Calendar class and the
#		dictionary of Scenes. Everything is done through "Scheduler".
#	Calendar has charge of Actor objects; Scene only has string names
#	What matters is which ACTORS are in a scene, not which CHARACTERS (for
#		scheduling purposes)
#	TIMEBLOCKS must be of equal length (ie 30 min intervals)
#	While the Scene class can have nonspeaking actors, there is no
#		accomodation for this in the scheduler code currently. Scheduling 
#		requires all actors in a scene. Could later update this by trying the
#		scheduler with the nonspeaking actors eliminated if the scheduler
#		fails to schedule scenes with all actors (although, might not bother,
#		because at that point it might be easier for the human to take care of
#		things).
#	The Scheduler does not accomodate for breaks.

# Next steps to improve code:
#	Make EXACTLY ONE class that the user needs to interact with, which will
#		handle creation of all other necessary classes.
#	Improve visual output (printing could look nicer).
#	Long term: Convert this into an interactive web app with a visual schedule
#		and more visually pleasing output.


class Actor():
	"""Actor class holds actor conflicts.

	Attributes:
	    name (string): name of actor
	    conflict_chart (dict): dictionary holding conflicts 
	"""
	def __init__(self, name, calendar):
		self.name = name
		self.create_conflict_chart(calendar)

	def create_conflict_chart(self, calendar):
		day_time_chart = calendar.day_time_chart
		days = day_time_chart.keys()

		self.conflict_chart = {}

		for day in days:
			temp_d = {}
			for timeblock in day_time_chart[day]:
				temp_d[timeblock] = True # true = available
			self.conflict_chart[day] = temp_d

	def add_conflict(self, day, time):
		self.conflict_chart[day][time] = False

	def remove_conflict(self, day, time):
		self.conflict_chart[day][time] = True

	# Returns TRUE if actor is available for requested times on specific day.
	def is_available(self, day, times):
		for time in times:
			if self.conflict_chart[day][time] == False:
				return False
		return True

class Scene():
	"""Holds scene actor names and length information.

	Attributes:
	    name (string): name of scene
	    speaking_actors (list): names of speaking actors
	    all_actors (list): all actors
	    length (int): number of timeblocks the scene needs
	"""

	def __init__(self, name, length, speaking_actors, nonspeaking_actors=[]):
		""" Initializes a scene

		Args:
			name (string): name of scene
			length (int): number of timeblocks the scene needs
			speaking_actors (list): names of speaking actors
			OPTIONAL nonspeaking_actors (list): names of nonspeaking actors
		"""

		self.name = name
		self.speaking_actors = speaking_actors
		self.all_actors = speaking_actors
		self.all_actors.extend(nonspeaking_actors)
		self.length = length

	# add or remove an actor: NOT FULLY IMPLEMENTED
	def add_actor(self, name, speaking=True):
		self.all_actors.append(name)
		if speaking:
			self.speaking_actors.append(name)

	def remove_actor(self, name):
		pass

class Calendar():
	"""Calendar class contains all actors and days being considered.

	Attributes:
		names (list): list of names of actors
		day_time_chart (dict): day-time chart (see documentation)
		days (list): list of days as strings
		interval (float): value between scenes (ie 0.5)
	    actor_objects (dict): dictionary of form d[actor_name] = actor object
	"""

	def __init__(self, names, day_time_chart, days, interval, conflicts=[]):
		"""Initialize Calendar: calendar creates/contains all actor objects

		Args:
			names (list): list of names of actors
			day_time_chart (dict): day-time chart (see documentation)
			days (list): list of days as strings
			interval (float): value between scenes (ie 0.5)
			conflicts (list of [name, day, time] lists): actor conflicts
		"""	
		self.names = names
		self.day_time_chart = day_time_chart
		self.interval = interval
		self.create_actor_objects()
		self.days = days

		for conflict in conflicts:
			self.add_conflict(conflict)

	def create_actor_objects(self):
		self.actor_objects = {}
		for name in self.names: # create actor objects
			self.actor_objects[name] = Actor(name, self)

	# Functions to add/remove conflicts
	def add_conflict(self, conflict):
		name = conflict[0]
		day = conflict[1]
		times = conflict[2]
		for time in times:
			self.actor_objects[name].add_conflict(day, time)

	def remove_conflict(self, conflict):
		name = conflict[0]
		day = conflict[1]
		times = conflict[2]
		for time in times:
			self.actor_objects[name].remove_conflict(day, time)

	# Check if a list of actors is available at a day/times
	def is_available(self, names, day, times):
		for name in names:
			if not self.actor_objects[name].is_available(day, times):
				return False
		return True

	# Clears all conflicts by remaking actor objects.
	def clear_conflicts(self):
		self.create_actor_objects()

class Scheduler():
	"""Takes a calendar and scenes, can do scheduling demands.

	NOTE: currently requests ALL ACTORS in a scene, does not account
		for the nonspeaking actors.

	Attributes:
	    calendar (Calendar): calendar object holding days and times
	    scenes (dict of Scene objects): keys are scene names
	"""

	def __init__(self, calendar, scenes):
		self.calendar = calendar
		self.scenes = scenes

	# determines if a scene works in a particular location
	def scene_works(self, scene, day, time_start, time_end = 9000000):
		# determine times to check based on scene length
		num_timeblocks = self.scenes[scene].length
		interval = self.calendar.interval
		scene_time_end = time_start + num_timeblocks*interval
		
		if scene_time_end > time_end:
			return False

		times = self.generate_times(time_start, scene_time_end)

		# check whether the scene can be done at the selected time
		try: # accounts for time required not being available on a day
			return self.calendar.is_available(self.scenes[scene].all_actors,
				day, times)
		except:
			return False

	# determines all possible start times for a specified scene
	def return_times_for_scene(self, scene):
		# return all times that a particular scene can start
		# outputs strings in the form "Day at Time"

		# BRUTE FORCE STRATEGY
		# manually check each timeslot start using above function
		# for each day:
		#	for each possible start time:
		#		does scene fit? if so, add it to list
		# return final list

		working_times = []

		days = self.calendar.day_time_chart.keys()
		for day in days:
			times = self.calendar.day_time_chart[day]
			for time in times:
				if self.scene_works(scene, day, time):
					tempStr = str(day) + " at " + str(time) # STRING
					working_times.append(tempStr)

		return working_times

	# determines all scenes that fit in a timeslot
	def return_scenes_that_fit(self, day, time_start, time_end):
		# return all scenes that fit in given timeslot
		# outputs strings in form "Scene at Time"
		
		# Strategy:
		# Loop through all scenes, see if they fit into any of timeslots
		#	if fits, return "scene fits at X"

		times = self.generate_times(time_start, time_end)

		working_scenes = []
		for scene in self.scenes.keys():
			for time in times:
				if self.scene_works(scene, day, time, time_end):
					working_scenes.append(scene + " at " + str(time))

		return working_scenes

	def generate_times(self, time_start, time_end):
		# NOTE does NOT include timeslot for time_end
		#	putting in 7, 8 with interval 0.5 would return [7,7.5]
		interval = self.calendar.interval
		num_timeblocks = int((time_end - time_start) / interval)
		times = []
		for i in range(0, num_timeblocks):
			times.append(time_start + interval*i)

		return times

	# ---------------------------- SCHEDULER and helper functions

	def schedule(self, days, scenes):
		""" Automatically schedules scenes around actor conflicts.
		
		Args:
			days (list of strings): list of days to consider
			scenes (list of strings): scenes to schedule

		Returns:
			Dictionary of form d[scene_name] = [day, time_start]
		"""

		# Create empty schedule
		timeblocks = []
		for day in days:
			for block in self.calendar.day_time_chart[day]:
				timeblocks.append([day, block])

		schedule = [0 for i in range(len(timeblocks))]

		# Create structure to hold final schedule
		final_arrangement = {}

		# Recursive call to try to make the schedule
		if self.schedule_solve(schedule, scenes, timeblocks, final_arrangement, scene_idx=0):
		 	return final_arrangement
		else:
		 	return None
	
	# Helper functions for schedule function	

	def schedule_solve(self, schedule, scene_list, timeblocks, current_arrangement, scene_idx=0):
		# Base case (no scenes left)
		if scene_idx == len(scene_list):
			return True

		# Select scene to next schedule
		scene = scene_list[scene_idx]
		timeblocks_required = self.scenes[scene].length

		# Loop through all possible times
		for i in range(0, len(schedule)):
			day = timeblocks[i][0]
			time_start = timeblocks[i][1]

			# If scene fits, continue

			# Check if schedule has space
			schedule_open = True
			for j in range(i, i+timeblocks_required):
				try:
					if schedule[j] == 1:
						schedule_open = False
				except:
					schedule_open = False

			# Check if actors are available during desired timeslots
			if schedule_open and self.schedule_is_valid(scene, day, time_start):
				# Set scene into schedule
				for j in range(i, i+timeblocks_required):
					schedule[j] = 1

				# Adjust current scene/time dictionary
				current_arrangement[scene] = timeblocks[i]

				# Recurse
				if self.schedule_solve(schedule, scene_list, timeblocks, 
					current_arrangement,scene_idx+1):
						return True

				# If unsuccessful, remove scene and continue trying to fit it
				for j in range(i, i+timeblocks_required):
					schedule[j] = 0
				current_arrangement[scene] = ""

		return False # No schedule exists

	def schedule_is_valid(self, scene, day, time_start):
		return self.scene_works(scene, day, time_start)


# -----------------------------------------------------------------------------

# HOW TO USE CODE
# Note: I would like to include a more user-friendly way to do this.
#	Notes about how to do that are included below.

# 1. Create a list with actor names
names = ["Kacie", "Collin", "Peter", "Tal"]

# 2. Create a list with the names of the days
days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]

# 3. Decide on the timeblock interval to use
interval = 0.5 # represents half-hour timeblocks

# 4. Create day-time chart, which is a dictionary in the form
#	d[name_of_day] = [times].
#		Example of August 18th 7 - 9 block and August 19th 1 - 4 block
#			(note the interval is represented)
# 		day_time_chart = { "8/18": [7, 7.5, 8, 8.5],
# 					   	   "8/19": [1, 1.5, 2, 2.5, 3, 3.5] }
# COULD MAKE THIS BETTER: There could be an function to do this
#	that will generate the time lists from input and using the above
#	days list
day_time_chart = {"Day 1": [7, 7.5, 8, 8.5, 9, 9.5],
				   "Day 2": [7, 7.5, 8, 8.5, 9, 9.5],
				   "Day 3": [7, 7.5, 8, 8.5, 9, 9.5],
				   "Day 4": [7, 7.5, 8, 8.5, 9, 9.5],
				   "Day 5": [7, 7.5, 8, 8.5, 9, 9.5]}

# 5. Create list of scene names
list_of_scenes = ["Scene 1", "Scene 2", "Scene 3", "Scene 4",
				  "Scene 5", "Scene 6", "Scene 7", "Scene 8", "Scene 9"]

# 6. Create dictionary of scene objects. Dictionary should be of the form
#	d[scene_name] = Scene(scene_name, num_timeblocks, list_of_actors_in_scene)
#	Note: for the example of interval = 0.5, if a scene needs 2 hours,
#		then num_timeblocks should equal 4 (4 half-hour chunks)
# COULD MAKE THIS BETTER: There could be a function to generate this.
scene_dict = { "Scene 1": Scene("Scene 1", 4, ["Kacie", "Collin", "Peter"]),
		   "Scene 2": Scene("Scene 2", 2, ["Kacie", "Collin"]),
		   "Scene 3": Scene("Scene 3", 3, ["Peter", "Tal"]),
		   "Scene 4": Scene("Scene 4", 2, ["Kacie", "Tal"]),
		   "Scene 5": Scene("Scene 5", 1, ["Peter", "Collin"]),
		   "Scene 6": Scene("Scene 6", 6, ["Kacie", "Collin", "Peter","Tal"]),
		   "Scene 7": Scene("Scene 7", 2, ["Peter", "Tal"]),
		   "Scene 8": Scene("Scene 8", 6, ["Kacie", "Collin", "Tal"]),
		   "Scene 9": Scene("Scene 9", 4, ["Kacie"])}

# 7. Create a list of conflicts. Conflicts are of the form
#	[actor_name, day, times] where times must be a list of times 
#	(EVEN IF it is only a single timeblock)
#	Note: If an actor has multiple days of conflicts, these must be separate
#		conflict objects.
# COULD MAKE THIS BETTER: Function to generate this, more robust conflicts.
conflicts = [['Tal', 'Day 1', [7, 7.5, 8, 8.5, 9, 9.5]],
			  ['Peter', 'Day 2', [8, 8.5, 9, 9.5]],
			  ['Collin', 'Day 2', [7, 7.5, 8, 8.5, 9, 9.5]],
			  ['Peter', 'Day 4', [7, 7.5, 8, 8.5, 9, 9.5]],
			  ['Kacie', 'Day 5', [7, 7.5, 8, 8.5, 9, 9.5]]]

# 8. Create Calendar object using above variables.
myCal = Calendar(names, day_time_chart, days, interval, conflicts)

# 9. Create Scheduler object using above variables.
myScheduler = Scheduler(myCal, scene_dict)

# 10. Schedule! Prints a dictionary in the form d[scene_name] = [day, time]
#	if a possible schedule exists, and prints None if one does not exist
#	Note: The days and list_of_scenes can be customized. For example, if a
#		calendar holds 30 days, you may choose to only generate the schedule
#		for one week (7 days). You may also specify which scenes to schedule.
#	Note 2: The scheduler does NOT account for doing any scene more than once.
# COULD MAKE THIS BETTER: Update printing so it is nicer for the user.
print(myScheduler.schedule(days, list_of_scenes))

# EXTRA
# Other things that can be done:
#	Print out times that a scene can be done
#	Print out scenes that fit into a particular timeblock