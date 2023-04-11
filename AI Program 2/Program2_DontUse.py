from scipy.special import softmax
import numpy as np
import random
import time


# Data Section

# Define facilitators
facilitators = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]

# Define classes and their details
classes = {
    "SLA100A": {"expectedEnrollment": 50, "preferredFacilitators": ["Glen", "Lock", "Banks", "Zeldin"], "otherFacilitators": ["Numen", "Richards"]},
    "SLA100B": {"expectedEnrollment": 50, "preferredFacilitators": ["Glen", "Lock", "Banks", "Zeldin"], "otherFacilitators": ["Numen", "Richards"]},
    "SLA191A": {"expectedEnrollment": 50, "preferredFacilitators": ["Glen", "Lock", "Banks", "Zeldin"], "otherFacilitators": ["Numen", "Richards"]},
    "SLA191B": {"expectedEnrollment": 50, "preferredFacilitators": ["Glen", "Lock", "Banks", "Zeldin"], "otherFacilitators": ["Numen", "Richards"]},
    "SLA201": {"expectedEnrollment": 50, "preferredFacilitators": ["Glen", "Banks", "Zeldin", "Shaw"], "otherFacilitators": ["Numen", "Richards", "Singer"]},
    "SLA291": {"expectedEnrollment": 50, "preferredFacilitators": ["Lock", "Banks", "Zeldin", "Singer"], "otherFacilitators": ["Numen", "Richards", "Shaw", "Tyler"]},
    "SLA303": {"expectedEnrollment": 60, "preferredFacilitators": ["Glen", "Zeldin", "Banks"], "otherFacilitators": ["Numen", "Singer", "Shaw"]},
    "SLA304": {"expectedEnrollment": 25, "preferredFacilitators": ["Glen", "Banks", "Tyler"], "otherFacilitators": ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]},
    "SLA394": {"expectedEnrollment": 20, "preferredFacilitators": ["Tyler", "Singer"], "otherFacilitators": ["Richards", "Zeldin"]},
    "SLA449": {"expectedEnrollment": 60, "preferredFacilitators": ["Tyler", "Singer", "Shaw"], "otherFacilitators": ["Zeldin", "Uther"]},
    "SLA451": {"expectedEnrollment": 100, "preferredFacilitators": ["Tyler", "Singer", "Shaw"], "otherFacilitators": ["Zeldin", "Uther", "Richards", "Banks"]}
}

# Define room capacities
roomCapacities = {
    "Slater 003": 45,
    "Roman 216": 30,
    "Loft 206": 75,
    "Roman 201": 50,
    "Loft 310": 108,
    "Beach 201": 60,
    "Beach 301": 75,
    "Logos 325": 450,
    "Frank 119": 60
}

roomList = list(roomCapacities.keys())


timeSlots = ['10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM']


# Activity Class
class Activity:
    def __init__(self, name, enrollment, preferredFacilitators, otherFacilitators):
        self.name = name
        self.enrollment = enrollment
        self.preferredFacilitators = preferredFacilitators
        self.otherFacilitators = otherFacilitators
        self.room = None
        self.time = None
        self.facilitator = None
        self.fitness = 0

    def __str__(self):
        return self.name + " " + self.room + " " + self.time + " " + self.facilitator + " " + str(self.fitness)



class Schedule:
    def __init__(self, activities):
        self.activities = activities
        self.fitness = 0
        self.probability = 0


    def __str__(self):
        return str(self.fitness)

    def printActivities(self):
        for activity in self.activities:
            print(activity)



# Takes in a list of n differnet schedules, each schedul having 11 activities
def calculateFitness(schedules):
    # For each schedule
    for schedule in schedules:

        # For each activity in the schedule
        for activity in schedule:

            # Check if the activity is scheduled at the same time as another activity in the same room
            for activity2 in schedule:
                if activity != activity2:
                    if activity.room == activity2.room and activity.time == activity2.time:
                        activity.fitness -= 0.5

        # Room Size Checks
        # If a room is too small subtract 0.5 from the fitness
        # If the room is 3 times more than the expected enrollment subtract 0.2 from the fitness
        # If the room is 6 times more than the expected enrollment subtract 0.4 from the 
        # Otherwise add 0.3 to the fitness
        for activity in schedule:
            if roomCapacities[activity.room] < activity.enrollment:
                activity.fitness -= 0.5
            elif roomCapacities[activity.room] < activity.enrollment * 3:
                activity.fitness -= 0.2
            elif roomCapacities[activity.room] < activity.enrollment * 6:
                activity.fitness -= 0.4
            else:
                activity.fitness += 0.3

        # Facilitaor Checks
        # If the activity is scheduled with a preferred facilitator add 0.5 to the fitness
        # If the activity is scheduled with an other facilitator add 0.2 to the fitness
        # Otherwise subtract 0.1 from the fitness
        for activity in schedule:
            if activity.facilitator in activity.preferredFacilitators:
                activity.fitness += 0.5
            elif activity.facilitator in activity.otherFacilitators:
                activity.fitness += 0.2
            else:
                activity.fitness -= 0.1

        # Faciliator Load Checks
        # If the faciliator is scheduled for only 1 activity in the current time slot add 0.2 to the fitness
        # If the facilitator is scheduled for 2 or more activities in the current time slot subtract 0.2 to the fitness
        # If the faciliator is overseeing more than 4 activities total subtract 0.5 from the fitness
        # If the faciliator only has 1 or 2 activities total sub  0.2 to the fitness (Unless the faciliator is Dr. Tyler, no fitness penalty for him)
        for activity in schedule:
            # Check if the faciliator is expected to be in many places at one time
            facilitatorCount = 0
            for activity2 in schedule:
                if activity.facilitator == activity2.facilitator and activity.time == activity2.time:
                    facilitatorCount += 1
            if facilitatorCount == 1:
                activity.fitness += 0.2
            elif facilitatorCount >= 2:
                activity.fitness -= 0.2

            # Check if the faciliator is overseeing too many activities
            facilitatorCount = 0
            for activity2 in schedule:
                if activity.facilitator == activity2.facilitator:
                    facilitatorCount += 1
            if facilitatorCount > 4:
                activity.fitness -= 0.5
            elif facilitatorCount <= 2 and activity.facilitator != "Tyler":
                activity.fitness -= 0.2

        # Activty Specific Checks
        # If Both Sections SLA100A and SLA100B are scheduled more than 4 hours apart add 0.5 to the fitness
        for activity in schedule:
            if activity.name == "SLA100A":
                for activity2 in schedule:
                    if activity2.name == "SLA100B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) > 4:
                            activity.fitness += 0.5
                            activity2.fitness += 0.5
        # If both section sof SLA100A and SLA100B are scheduled at the same time subtract 0.5 from the fitness
        for activity in schedule:
            if activity.name == "SLA100A":
                for activity2 in schedule:
                    if activity2.name == "SLA100B":
                        if activity.time == activity2.time:
                            activity.fitness -= 0.5
                            activity2.fitness -= 0.5
        # If both sections of SLA191A and SLA191B are scheduled more than 4 hours apart add 0.5 to the fitness
        for activity in schedule:
            if activity.name == "SLA191A":
                for activity2 in schedule:
                    if activity2.name == "SLA191B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) > 4:
                            activity.fitness += 0.5
                            activity2.fitness += 0.5

        # If both sections of SLA191A and SLA191B are scheduled at the same time subtract 0.5 from the fitness
        for activity in schedule:
            if activity.name == "SLA191A":
                for activity2 in schedule:
                    if activity2.name == "SLA191B":
                        if activity.time == activity2.time:
                            activity.fitness -= 0.5
                            activity2.fitness -= 0.5
        # If a section of SLA191 Either A or B is scheduled in a consecutive time slot with a section of SLA100A or SLA100B add 0.5 to the fitness
        # Unless one of the activities is in Roman or Beach and the other is in the opposit if thats the case subtract 0.4 from the fitness instead
        for activity in schedule:
            if activity.name == "SLA191A" or activity.name == "SLA191B":
                for activity2 in schedule:
                    if activity2.name == "SLA100A" or activity2.name == "SLA100B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 1:
                            if "Roman" in activity.room and "Beach" in activity2.room:
                                activity.fitness -= 0.4
                                activity2.fitness -= 0.4
                            elif "Beach" in activity.room and "Roman" in activity2.room:
                                activity.fitness -= 0.4
                                activity2.fitness -= 0.4
                            else:
                                activity.fitness += 0.5
                                activity2.fitness += 0.5

        # Now we need todo the same except with faciliators
        # If a faciliator is inside Roman or Beach and their next activity is in the opposite room add subtract 0.4 from the fitness
        for activity in schedule:
            if "Roman" in activity.room:
                for activity2 in schedule:
                    if "Beach" in activity2.room and activity.facilitator == activity2.facilitator:
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 1:
                            activity.fitness -= 0.4
                            activity2.fitness -= 0.4
            elif "Beach" in activity.room:
                for activity2 in schedule:
                    if "Roman" in activity2.room and activity.facilitator == activity2.facilitator:
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 1:
                            activity.fitness -= 0.4
                            activity2.fitness -= 0.4

        # If a saection of SLA191A/B and a section of SLA100A/B are scheduled with one time in between them add 0.25 to the fitness (meaning activity1 is at 10am and activity2 is at 12pm)
        for activity in schedule:
            if activity.name == "SLA191A" or activity.name == "SLA191B":
                for activity2 in schedule:
                    if activity2.name == "SLA100A" or activity2.name == "SLA100B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 2:
                            activity.fitness += 0.25
                            activity2.fitness += 0.25

        # If a section of SLA191A/B and a section of SLA100A/B scheduled in the same time slot subtract 0.25 from the fitness
        for activity in schedule:
            if activity.name == "SLA191A" or activity.name == "SLA191B":
                for activity2 in schedule:
                    if activity2.name == "SLA100A" or activity2.name == "SLA100B":
                        if activity.time == activity2.time:
                            activity.fitness -= 0.25
                            activity2.fitness -= 0.25

    return schedules   




def createSchedules(n):
    # Randomly create 10 differnt schedules that has randomly chosen, room, time, and facilitator, for each activity
    schedules = []
    for i in range(n):
        schedule = []
        for name, details in classes.items():
            activity = Activity(name, details["expectedEnrollment"], details["preferredFacilitators"], details["otherFacilitators"])
            activity.room = random.choice(list(roomCapacities.keys()))
            activity.time = random.choice(timeSlots)
            activity.facilitator = random.choice(facilitators)
            schedule.append(activity)
        schedules.append(schedule)

    return schedules


# Main Section

if __name__ == "__main__":
    # Randomly create 10 differnt schedules that has randomly chosen, room, time, and facilitator, for each activity
    schedules = createSchedules(500)

    schedulesWithActivitiesWithFitness = calculateFitness(schedules)

    scheduleObjects = []


    
    for schedule in schedulesWithActivitiesWithFitness:
        scheduleObject = Schedule(schedule)
        scheduleObject.fitness = sum([activity.fitness for activity in schedule])
        scheduleObjects.append(scheduleObject)





    calcProbOfSchedules = []
    for schedule in scheduleObjects:
        calcProbOfSchedules.append(schedule.fitness)

    

    proabilityDistro = softmax(calcProbOfSchedules)


    # for each schedule object in newArray assign the proabilityDistro value to the schedule object (they are in the same order so it should be fine)
    for i, schedule in enumerate(calcProbOfSchedules):
        scheduleObjects[i].probability = proabilityDistro[i]

    # Keep the top half of the schedules
    newScheduleObjects = []
    for schedule in sorted(scheduleObjects, key=lambda x: x.probability, reverse=True):
        if len(newScheduleObjects) < len(scheduleObjects) / 2:
            newScheduleObjects.append(schedule)
        else:
            break




    
    currentOptions = newScheduleObjects
    generatedSchedules = []

    

    # Now that we have the top half of the schedules, it's time to start the genetic algorithm
    # We will do this by randomly selecting two schedules from the top half and randomly selecting a number between 1 and the number of activities in a schedule (in this case each schedule has 11 activities)
    # We will take schedule 1 (parent 1) and schedule 2 (parent 2) and create a new schedule (child) by taking the first random number of activities from parent 1 and the rest of the activities from parent 2
    # We will then take schedule2 (parent 1) and schedule 1 (parent 2) and create a new schedule (child) by taking the first random number of activities from parent 1 and the rest of the activities from parent 2
    # We will set the scheulde.fitnes to 0 and for each activity in the schedule, set the activity.fitness to 0
    # Then for each activity in the schedule, we will calculate the fitness of the activity (we do this by passing the whole list of activities of the schedule to the calculateFitness function)
    # We will then add the schedule to the generatedSchedules list
    # We will do this until currentOptions is empty, and then restart the process by keeping the top half of the generatedSchedules list and repeating the process 100 times
    # We will then take the top 10 schedules and print them to the console
    mutationRate = 100
    improvement_threshold = 0.001
    improvement = 1
    generatedSchedules = []
    G100 = 0

    best_fitness = 0
    last_improvement_gen = 0
    i = 0
    while improvement_threshold < improvement:
        i += 1
        
        print("Generation: " + str(i))
        if i % 10 == 0:
            mutationRate += 10
        for j in range(len(currentOptions) // 2):
            parent1 = random.choice(currentOptions)
            while True:
                parent2 = random.choice(currentOptions)
                if parent1 != parent2:
                    break

            # reset fitness
            for activity in parent1.activities + parent2.activities:
                activity.fitness = 0
            parent1.fitness = 0
            parent2.fitness = 0

            breakPoint = random.randint(1, len(parent1.activities))

            child1 = Schedule(parent1.activities[:breakPoint] + parent2.activities[breakPoint:])
            child2 = Schedule(parent2.activities[:breakPoint] + parent1.activities[breakPoint:])

            for activity in child1.activities + child2.activities:
                activity.fitness = 0
            child1.fitness = 0
            child2.fitness = 0

            # mutate with a 1% chance
            if random.randint(0, mutationRate) == 1:
                for schedule in [parent1, parent2, child1, child2]:
                    for activity in schedule.activities:
                        if random.randint(0, mutationRate) == 1:
                            activity.room = random.choice(list(roomCapacities.keys()))
                            activity.time = random.choice(timeSlots)
                            activity.facilitator = random.choice(facilitators)
                            activity.fitness = 0

            # calculate fitness of the activities in child1 and child2 schedules
            child1.fitness = sum([activity.fitness for activity in calculateFitness([child1.activities])[0]])
            child2.fitness = sum([activity.fitness for activity in calculateFitness([child2.activities])[0]])

            # calculate fitness of the activities in parent1 and parent2 schedules
            parent1.fitness = sum([activity.fitness for activity in calculateFitness([parent1.activities])[0]])
            parent2.fitness = sum([activity.fitness for activity in calculateFitness([parent2.activities])[0]])

            # add schedules to the generatedSchedules list
            generatedSchedules.append(child1)
            generatedSchedules.append(child2)
            generatedSchedules.append(parent1)
            generatedSchedules.append(parent2)

            # remove parent1 and parent2 schedules from the currentOptions list
            currentOptions.remove(parent1)
            currentOptions.remove(parent2)

        # set currentOptions list to the top half of the generatedSchedules list
        currentOptions = sorted(generatedSchedules, key=lambda x: x.fitness, reverse=True)
        currentOptions = currentOptions[:len(currentOptions) // 2]
        # clear generatedSchedules list
        generatedSchedules = []


        if i > 100:
            if i == 100:
                G100 = currentOptions[0].fitness
        # check for improvement
            current_fitness = currentOptions[0].fitness
            improvement = (best_fitness - current_fitness) / best_fitness if best_fitness != 0 else 1
            if improvement < improvement_threshold:
                last_improvement_gen += 1
            else:
                best_fitness = current_fitness
                last_improvement_gen = 0

            if last_improvement_gen > 50:
                print(f"No improvement for {last_improvement_gen} generations. Stopping.")
                break
        else:
            continue

        with open('bestSchedule.txt', 'w') as f:
            # write the overall best schedule fitness to the file
            f.write(f"Schedule Fitness: {currentOptions[0].fitness} \n")
            # write the activities in the schedule to the file in the same order as timeSlots
            for timeSlot in timeSlots:
                for activity in currentOptions[0].activities:
                    if activity.time == timeSlot:
                        f.write(f"{activity.name} - {activity.room} - {activity.facilitator} - {activity.time} \n")

print("Program finished")

  
   