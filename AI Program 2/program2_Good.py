from scipy.special import softmax
import numpy as np
import random
import time
import matplotlib.pyplot as plt
mutationRate = 100

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


class Activity:
    def __init__(self, name, expected, preferredFacilitators, otherFacilitators):
        self.name = name
        self.expectedEnrollment = expected
        self.preferredFacilitators = preferredFacilitators
        self.otherFacilitators = otherFacilitators
        self.room = None
        self.time = None
        self.facilitator = None
        self.fitness = 0

    def __str__(self):
        return self.name + " " + self.room + " " + self.time + " " + self.facilitator + " " + str(self.fitness)



class Schedule:
    def __init__(self, activities = []):
        self.activities = activities
        self.fitness = 0
        self.probability = 0


    def __str__(self):
        return str(self.fitness)

    def printActivities(self):
        for activity in self.activities:
            print(activity)

    # override the less than operator
    def __lt__(self, other):
        return self.fitness < other.fitness

    # Override equals operator
    def __eq__(self, other):
        self.activities == other.activities
        self.fitness == other.fitness


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


def calcFitnes(schedule):
    # Sechedule is an indivudal shcedule object
    # We can access the activities in the schedule by using schedule.activities
    fitness = 0

    # Check if the room is available at the time
    for activity in schedule.activities:
        for activity2 in schedule.activities:
            if activity.name != activity2.name:
                if activity.room == activity2.room and activity.time == activity2.time:
                    fitness -= 0.5

    # Check if the room is big enough for the class
    for activity in schedule.activities:
            if roomCapacities[activity.room] < activity.expectedEnrollment:
                fitness -= 0.5
            elif roomCapacities[activity.room] > activity.expectedEnrollment * 3:
                fitness -= 0.2
            elif roomCapacities[activity.room] > activity.expectedEnrollment * 6:
                print("Room is too big for " + activity.name + " " + activity.room)
                fitness -= 0.4
            else:
                fitness += 0.3

    # Check if the facilitator is a preferred facilitator or other or not
    for activity in schedule.activities:
            if activity.facilitator in activity.preferredFacilitators:
                fitness += 0.5
            elif activity.facilitator in activity.otherFacilitators:
                fitness += 0.2
            else:
                fitness -= 0.1

    # Check if the facilitator is expected to be in many places at one time
    for activity in schedule.activities:
            # Check if the faciliator is expected to be in many places at one time
            facilitatorCount = 0
            for activity2 in schedule.activities:
                if activity.facilitator == activity2.facilitator and activity.time == activity2.time:
                    facilitatorCount += 1
            # If the faciliator only has one class at that time, add 0.2 to the fitness
            if facilitatorCount == 1:
                fitness += 0.2
            # If the faciliator has two or more classes at that time, subtract 0.2 from the fitness
            elif facilitatorCount >= 2:
                fitness -= 0.2

            # Check if the faciliator is overseeing too many activities
            facilitatorCount = 0
            for activity2 in schedule.activities:
                if activity.facilitator == activity2.facilitator:
                    facilitatorCount += 1
            if facilitatorCount > 4:
                fitness -= 0.5
            elif facilitatorCount <= 2 and activity.facilitator != "Tyler":
                fitness -= 0.2
    
    # If Both Sections SLA100A and SLA100B are scheduled more than 4 hours apart add 0.5 to the fitness
    for activity in schedule.activities:
            if activity.name == "SLA100A":
                for activity2 in schedule.activities:
                    if activity2.name == "SLA100B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) > 4:
                            fitness += 0.5

    for activity in schedule.activities:
            if activity.name == "SLA100A":
                for activity2 in schedule.activities:
                    if activity2.name == "SLA100B":
                        if activity.time == activity2.time:
                            fitness -= 0.5

    for activity in schedule.activities:
            if activity.name == "SLA191A":
                for activity2 in schedule.activities:
                    if activity2.name == "SLA191B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) > 4:
                            fitness += 0.5

    for activity in schedule.activities:
            if activity.name == "SLA191A":
                for activity2 in schedule.activities:
                    if activity2.name == "SLA191B":
                        if activity.time == activity2.time:
                            fitness -= 0.5

    for activity in schedule.activities:
            if activity.name == "SLA191A" or activity.name == "SLA191B":
                for activity2 in schedule.activities:
                    if activity2.name == "SLA100A" or activity2.name == "SLA100B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 1:
                            if "Roman" in activity.room and "Beach" in activity2.room:
                                fitness -= 0.4
                            elif "Beach" in activity.room and "Roman" in activity2.room:
                                fitness -= 0.4
                            else:
                                fitness += 0.5

    for activity in schedule.activities:
            if "Roman" in activity.room:
                for activity2 in schedule.activities:
                    if "Beach" in activity2.room and activity.facilitator == activity2.facilitator:
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 1:
                            fitness -= 0.4
            elif "Beach" in activity.room:
                for activity2 in schedule.activities:
                    if "Roman" in activity2.room and activity.facilitator == activity2.facilitator:
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 1:
                            fitness -= 0.4

    for activity in schedule.activities:
            if activity.name == "SLA191A" or activity.name == "SLA191B":
                for activity2 in schedule.activities:
                    if activity2.name == "SLA100A" or activity2.name == "SLA100B":
                        if abs(timeSlots.index(activity.time) - timeSlots.index(activity2.time)) == 2:
                            fitness += 0.25

    for activity in schedule.activities:
            if activity.name == "SLA191A" or activity.name == "SLA191B":
                for activity2 in schedule.activities:
                    if activity2.name == "SLA100A" or activity2.name == "SLA100B":
                        if activity.time == activity2.time:
                            fitness -= 0.25


    return fitness

def mutate(schedule):
    # Choose a random activity from schedule.activites 
    # Choose to either change the time, room, or facilitator
    # Only change that one thing
    # There shoudl only be a 1% chance of mutation
    # If there is a mutation, return the mutated schedule
    # If there is no mutation, return the original schedule
    if random.randint(0, mutationRate) == 1:
        activity = random.choice(schedule.activities)
        if random.randint(0, 2) == 0:
            activity.time = random.choice(timeSlots)
        elif random.randint(0, 2) == 1:
            activity.room = random.choice(roomList)
        else:
            activity.facilitator = random.choice(facilitators)

    return schedule

    


def crossover(schedule1, schedule2):
    # Choose a random index
    breakPoint = random.randint(0, len(schedule1.activities) - 1)
    # Create two new schedules
    parent1 = schedule1.activities[:]
    parent2 = schedule2.activities[:]
    child1 = Schedule(parent1[:breakPoint] + parent2[breakPoint:][:])
    child2 = Schedule(parent2[:breakPoint] + parent1[breakPoint:][:])

    return child1, child2 


initialActivities = createSchedules(500)
initialSchedules = []
for activity in initialActivities:
    s = Schedule(activity)
    initialSchedules.append(s)

for schedule in initialSchedules:
    schedule.fitness = calcFitnes(schedule)



# Keep the best half of the schedules
initialSchedules.sort(key=lambda x: x.fitness, reverse=True)
initialSchedules = initialSchedules[:len(initialSchedules)//2]


improveThreshold = 0.01
i = 0
# We are going to have a genetic algorithm that will try to find the best schedule
# The genectic algorithm will have a population of n schedules ( which will be half of the total number of schedules created in the beginning, i.e if we make 500 schedules at the start we pass 250 schedules to the genetic algorithm)
# The genetic alogrithm will make children out of two random parents, then will have a 1% chance of mutation (i.e. a random activity will be changed, either the time, room or facilitator (use the facilitator list not the preferred facilitator list or the other facilitator list)))
# We will do this 100 times
print("Starting Genetic Algorithm")
while True:
    i += 1
    if i % 10 == 0:
        print("Generation: " + str(i))
    if i % 3 == 0:
        mutationRate *= 2
    schedulesToGoThrough = initialSchedules[:]
    # Make children
    children = []
    usedParents = []
    for j in range(len(initialSchedules)//2):
        # Choose two random parents
        parent1 = random.choice(schedulesToGoThrough[:])
        schedulesToGoThrough.remove(parent1)
        parent2 = random.choice(schedulesToGoThrough[:])
        schedulesToGoThrough.remove(parent2)
        # Make children out of the parents
        child1, child2 = crossover(parent1, parent2)
        # Mutate the children / parents
        child1 = mutate(child1)
        child2 = mutate(child2)
        parent1 = mutate(parent1)
        parent2 = mutate(parent2)

        # Add the children to the list of children
        children.append(child1)
        children.append(child2)
        usedParents.append(parent1)
        usedParents.append(parent2)


    # Calculate the fitness of the children
    for schedule in children:
        schedule.fitness = calcFitnes(schedule)
    

    # Calculate the fitness of the parents
    for schedule in initialSchedules:
        schedule.fitness = calcFitnes(schedule)


    # Add the children to the list of schedules
    initialSchedules += children


    # Calculate the fitness of the children
    # Sort the schedules by fitness
    initialSchedules.sort(key=lambda x: x.fitness, reverse=True)
    # Print the best fitness

    # Remove the best half of the schedules
    initialSchedules = initialSchedules[:len(initialSchedules)//2]
    if i == 100:
        j = 0
        softMaxList = []
        for schedule in initialSchedules:
            softMaxList.append(schedule.fitness)

        probDistro = softmax(softMaxList)
        G100 = probDistro
    if i >= 100:
        
        j = 0
        softMaxList = []
        for schedule in initialSchedules:
            softMaxList.append(schedule.fitness)

        probDistro = softmax(softMaxList)
        GN = probDistro

        # If current best schedule is within 1% of the best schedule from gen 100, stop the genetic algorithm
        if abs(sum(GN) - sum(G100)) / len(G100) < 0.01:
            break






print("Genetic Algorithm Finished")
with open('bestSchedule.txt', 'w') as f:
    # write the overall best schedule fitness to the file
    f.write(f"Schedule Fitness: {initialSchedules[0].fitness} \n")
    # write the activities in the schedule to the file in the same order as timeSlots
    for timeSlot in timeSlots:
        for activity in initialSchedules[0].activities:
            if activity.time == timeSlot:
                f.write(f"{activity.name} - {activity.room} - {activity.facilitator} - {activity.time} \n")

