from scipy.special import softmax
import random


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


    def __str__(self):
        return str(self.fitness)

    def printActivities(self):
        for activity in self.activities:
            print(activity)



# Takes in a list of n differnet schedules, each schedul having 11 activities
def calculateFitness(schedules):
     # For each activity in each schedule, calculate the fitness
    # Activity fitness starts at 0
    # If there are multiple activities in the same room at the same time, subtract 0.5 from the fitness

    for schedule in schedules:
        for activity in schedule:
            for otherActivity in schedule:
                if activity.room == otherActivity.room and activity.time == otherActivity.time and activity.name != otherActivity.name:
                    activity.fitness -= 0.5

    # Room Size Section
    # If the room size is too small for the expected enrollment, subtract 0.5 from the fitness
    # If there are activities in the room with capatacity > 3 times the expected enrollment, subtract 0.2 from the fitness
    # IF there are activities in the room with capatcity > 6 times expected enrollment, subtract 0.4 from the fitness
    # Otherwise add 0.3 to the fitness

    for schedule in schedules:
        for activity in schedule:
            if roomCapacities[activity.room] < activity.enrollment:
                activity.fitness -= 0.5
            elif roomCapacities[activity.room] > 3 * activity.enrollment:
                activity.fitness -= 0.2
            elif roomCapacities[activity.room] > 6 * activity.enrollment:
                activity.fitness -= 0.4
            else:
                activity.fitness += 0.3

    # Facilitator Section
    # If an actvitiy is overseen by a preferred facilitator, add 0.5 to the fitness / 
    # If an activity is overseen by an other facilitator, add 0.2 to the fitness / 
    # If an activity is overseen by any other facilitator, subtract 0.1 from the fitness /
    # If the faciliator is scheduled for only 1 activity in the time slot, add 0.2 to the fitness/ 
    # If the facilitator is scheulded for more than 1 activity in the time slot, subtract 0.2 from the fitness / 
    # If the facilitator is scheuled to oversee more than 4 activities in the day, subtract 0.5 from the fitness/
    # If the facilitator is schlued to over see 1 or 2 activities (except for Dr Tyler), subtract 0.4 to the fitness
    # If the facilitator has consecutive time slots in Roman / Beach and then in Beach / Roman, subtract 0.2 from the fitness


    # For each activity in each schedule, calculate the fitness

    
    for schedule in schedules:
        for activity in schedule:
            # If the activity is overseen by a preferred facilitator, add 0.5 to the fitness
            if activity.facilitator in activity.preferredFacilitators:
                activity.fitness += 0.5
            # If the activity is overseen by an other facilitator, add 0.2 to the fitness
            elif activity.facilitator in activity.otherFacilitators:
                activity.fitness += 0.2
            # If the activity is overseen by any other facilitator, subtract 0.1 from the fitness
            else:
                activity.fitness -= 0.1

            # If the faciliator is scheduled for only 1 activity in the time slot, add 0.2 to the fitness
            count = 0
            for otherActivity in schedule:
                if activity.facilitator == otherActivity.facilitator and activity.time == otherActivity.time:
                    count += 1
            # Ideally we would only have one instance of an activity in a time slot with the same facilitator
            if count == 1:
                activity.fitness += 0.2
            # If the facilitator is scheduled for more than 1 activity in the time slot, subtract 0.2 from the fitness
            elif count > 1:
                activity.fitness -= 0.2

            # If the facilitator is scheduled to oversee more than 4 activities in the day, subtract 0.5 from the fitness
            count = 0
            for otherActivity in schedule:
                if activity.facilitator == otherActivity.facilitator:
                    count += 1
            # If they are scheduled for more than 4 activities, subtract 0.5 from the fitness
            if count > 4:
                activity.fitness -= 0.5
            # If they are scheduled for 1 or 2 activities (except for Dr Tyler), subtract 0.4 from the fitness
            elif count == 1 or count == 2:
                if activity.facilitator != "Tyler":
                    activity.fitness -= 0.4

            # If the facilitator has consecutive time slots in Roman / Beach and then in Beach / Roman, subtract 0.2 from the fitness
            if "Roman" in activity.room or "Beach" in activity.room:
                if "Roman" in activity.room:
                    building = "Roman"
                else:
                    building = "Beach"
                for otherActivity in schedule:
                    if activity.facilitator == otherActivity.facilitator and activity.time == timeSlots[timeSlots.index(otherActivity.time) - 1]:
                        if building not in otherActivity.room:
                            activity.fitness -= 0.2
                            otherActivity.fitness -= 0.2
                    
   
            
    
    # FINISH THIS SECTION
    # Activity Specific Section
    # IF the two sections SLA100A and SLA100B are more than 4 hours apart, add 0.5 to the fitness/
    # IF both sections of SLA100 are in the same time slot, subtract 0.5 from the fitness/
    # If the two sections of SLA191 are more than 4 hours apart, add 0.5 to the fitness/
    # If both sections of SLA191 are in the same time slot, subtract 0.5 from the fitness/

    # A section of SLA 191 and a section of SLA100 are overseen in conseutive time (10am and 11am), add 0.5 to the fitness
    # In this case however if one of the courses is in Roman or Beach and the other isn't subtract 0.4 from the fitness (it's fine if neither are in Roman or Beach)
    # A section of SLA 191 and a section of SLA 100 are taught separated by 1 hour (10am and 12pm) add 0.25 to the fitness
    # A section of SLA 191 and a section of SLA 100 are taught in the same time slot subtract 0.25 from the fitness

     # IF the two sections SLA100A and SLA100B are more than 4 hours apart, add 0.5 to the fitness
    for schedule in schedules:
        for activity in schedule:
            if "SLA100A" in activity.name:
                for otherActivity in schedule:
                    if "SLA100B" in otherActivity.name:
                        if timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) > 4:
                            activity.fitness += 0.5
                        elif timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) < -4:
                            activity.fitness += 0.5
                        else:
                            activity.fitness -= 0.5
            elif "SLA100B" in activity.name:
                for otherActivity in schedule:
                    if "SLA100A" in otherActivity.name:
                        if timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) > 4:
                            activity.fitness += 0.5
                        elif timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) < -4:
                            activity.fitness += 0.5
                        else:
                            activity.fitness -= 0.5

    # IF both sections of SLA100 are in the same time slot, subtract 0.5 from the fitness
    for schedule in schedules:
        for activity in schedule:
            if "SLA100A" in activity.name:
                for otherActivity in schedule:
                    if "SLA100B" in otherActivity.name:
                        if activity.time == otherActivity.time:
                            activity.fitness -= 0.5
            elif "SLA100B" in activity.name:
                for otherActivity in schedule:
                    if "SLA100A" in otherActivity.name:
                        if activity.time == otherActivity.time:
                            activity.fitness -= 0.5

    # If the two sections of SLA191 are more than 4 hours apart, add 0.5 to the fitness
    for schedule in schedules:
        for activity in schedule:
            if "SLA191A" in activity.name:
                for otherActivity in schedule:
                    if "SLA191B" in otherActivity.name:
                        if timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) > 4:
                            activity.fitness += 0.5
                        elif timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) < -4:
                            activity.fitness += 0.5
                        else:
                            activity.fitness -= 0.5
            elif "SLA191B" in activity.name:
                for otherActivity in schedule:
                    if "SLA191A" in otherActivity.name:
                        if timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) > 4:
                            activity.fitness += 0.5
                        elif timeSlots.index(activity.time) - timeSlots.index(otherActivity.time) < -4:
                            activity.fitness += 0.5
                        else:
                            activity.fitness -= 0.5

    # If both sections of SLA191 are in the same time slot, subtract 0.5 from the fitness
    for schedule in schedules:
        for activity in schedule:
            if "SLA191A" in activity.name:
                for otherActivity in schedule:
                    if "SLA191B" in otherActivity.name:
                        if activity.time == otherActivity.time:
                            activity.fitness -= 0.5
            elif "SLA191B" in activity.name:
                for otherActivity in schedule:
                    if "SLA191A" in otherActivity.name:
                        if activity.time == otherActivity.time:
                            activity.fitness -= 0.5

    
    

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
    schedules = createSchedules(50)

    schedulesWithActivitiesWithFitness = calculateFitness(schedules)

    scheduleObjects = []



# Write the above write to file statment with out using enumerate
    with open("schedules.txt", "w") as file:
        for schedule in schedulesWithActivitiesWithFitness:
            file.write("Schedule Fitness: " + str(sum([activity.fitness for activity in schedule])) + "\n")
            # Also write the schedules activities to the file
            for activity in schedule:
                file.write(str(activity) +  " \n")
            file.write("\n")


    
            scheduleObject = Schedule(schedule)
            scheduleObject.fitness = sum([activity.fitness for activity in schedule])
            print(sum([activity.fitness for activity in schedule]))
            scheduleObjects.append(scheduleObject)

    newArray = []
    for schedule in scheduleObjects:
        newArray.append(schedule.fitness)

    proabilityDistro = softmax(newArray)
    print(proabilityDistro)




    



    # # print the schedules fitness and then the activities in each schedule to the console
    # for i, schedule in enumerate(sorted(scheduleObjects, key=lambda x: x.fitness, reverse=True)[:10]):
    #     print("Schedule " + str(i) + " Fitness: " + str(schedule.fitness))
    #     for activity in schedule.activities:
    #         print(activity.name, activity.room, activity.time, activity.facilitator, activity.fitness)
    #     print()
    # print('=' * 50)
    

    





# # OPtional stuff Uncomment to enable
#  #print the 10 best schedules
#     for i, schedule in enumerate(sorted(schedulesWithActivitiesWithFitness, key=lambda x: sum([activity.fitness for activity in x]), reverse=True)[:10]):
#         sum = 0
#         for activity in schedule:
#             sum += activity.fitness
#         print("Schedule " + str(i) + " Fitness: " + str(sum))
#         for activity in schedule:
#             print(activity.name, activity.room, activity.time, activity.facilitator, activity.fitness)
#         print()
#     print('=' * 50)
#    # print all schedule objects
#     for schedule in scheduleObjects:
#         print(schedule)
#         # print the activities in each schedule
#         for element in schedule.activities:
#             print(element)
#         print()

#     # Create a probability distribution based on the fitness of each schedule
#     # The higher the fitness the higher the probability
#     # The lower the fitness the lower the probability
#     # Each Schedule object has the sum of the fitness of all the activities in the schedule

