import pandas as pd
import googlemaps
from datetime import datetime, timedelta
import datetime
from itertools import cycle, islice
from datetime import datetime

directions_api_key = googlemaps.Client(key='AIzaSyAO4lGZvhukpPyotLD4UUai8tyP8N64bUk')

def optdisndtime(origin,dest):
    now = datetime.now()
    departure_time = now
    directions_result = directions_api_key.directions(origin, dest, mode="driving", departure_time=departure_time)
    route = directions_result[0]['summary']
    travel_time = directions_result[0]['legs'][0]['duration']['text']
    distance = directions_result[0]['legs'][0]['distance']['text']
    return (route,travel_time,distance)

salesrep_data=pd.read_csv("E:/optimal/Salesrep.csv")
appointments_data=pd.read_csv("E:/optimal/appointments.csv")

def allot_appointments(salesrep_data, appointments_data):
    appointment_allocation = {sales_rep_id: [] for sales_rep_id in salesrep_data['Home_addr']}
    appointments_data = appointments_data.sort_values(by='Start_time')
    for i, appointment in appointments_data.iterrows():
        appointment_allocated = False
        for _, salesrep in salesrep_data.iterrows():
            if salesrep['Capacity'] > 0 and salesrep['Home_addr'] != appointment['Full_addr']:
                distance = optdisndtime(salesrep['Home_addr'], appointment['Full_addr'])[2]
                if float(distance.split()[0]) <= 10:
                    for allocated_appointment in appointment_allocation[salesrep['Home_addr']]:
                        end_time = datetime.strptime(allocated_appointment['End_time'], '%I:%M %p')
                        if end_time + timedelta(minutes=60) > datetime.strptime(appointment['Start_time'], '%I:%M %p'):
                            break
                    else:
                        start_time = datetime.strptime(appointment['Start_time'], '%I:%M %p')
                        end_time = start_time + timedelta(hours=int(appointment['Duration']))
                        allocated_appointment = {
                            'ID': appointment['ID'],
                            'Customer_name': appointment['Customer_name'],
                            'Full_addr': appointment['Full_addr'],
                            'Start_time': appointment['Start_time'],
                            'Duration': appointment['Duration'],
                            'Sales_rep': salesrep['ID'],
                            'End_time': end_time.strftime("%I:%M %p")
                        }
                        appointment_allocation[salesrep['Home_addr']].append(allocated_appointment)
                        salesrep_data.loc[salesrep_data['ID'] == salesrep['ID'], 'Capacity'] -= 1
                        appointment_allocated = True
                        break
        '''
        if not appointment_allocated:
            print(f"No sales rep available for appointment {appointment['ID']}")
        '''
    return appointment_allocation

appointment_allocation = allot_appointments(salesrep_data, appointments_data)
# print(appointment_allocation)

def apptlist():
    appointlist=appointment_allocation
    output_list = [ ["Home Addr: " + k] + ["Appt " + str(v['ID']) +"("+v['Start_time']+"-"+v['End_time']+")" +": " + v['Full_addr'] for v in appointlist[k]] + ["Home Addr: " + k] for k in appointlist]
    return output_list

for i, loc in enumerate(apptlist()):
    print(f"Sales Rep {i+1} Route map: ", end="")
    total_time = 0
    appt_count = 0
    visited_list = []
    home_count = 0
    is_home_printed = False
    for j, (origin, dest) in enumerate(zip(loc, islice(cycle(loc), 1, None))):
        # print("j", j, len(loc))
        route, travel_time, distance = optdisndtime(origin, dest)
        # travel_time = int(travel_time.split()[0])
        if j < len(loc)-1:
            if ("Home Addr" in origin and "Appt" in dest) or ("Home Addr" in dest and "Appt" in origin) or ("Appt" in origin and "Appt" in dest):
                
                if origin not in visited_list and dest not in visited_list:
                    print(f"{origin} --- (Travel: {travel_time}, Distance: {distance}, Route: {route}) ---> {dest}", end="")
                    total_time += int(travel_time.split()[0])
                    if "Home Addr" in dest:
                        is_home_printed = True
                else:
                    # if j != len(loc)-2:
                    print(f" ---- (Travel: {travel_time}, Distance: {distance}, Route: {route}) --->",end="") # time
                    total_time += int(travel_time.split()[0])
                    continue
                
                if "Appt" in origin or "Appt" in dest:
                    appt_count += 1
                    if "Appt" in origin and origin not in visited_list:
                        visited_list.append(origin)
                    if "Appt" in dest and dest not in visited_list:
                        visited_list.append(dest)
            else:
                # appt_count += 1
                # print(f"{origin} ---(Travel: {travel_time},Distance: {distance})---> {dest} (Appt {appt_count})", end="")
                continue
        if j == len(loc)-1:
            #print(home_count)
            if "Home Addr" in origin and not is_home_printed:
                print(f"{origin}", end="")
            print(f" ---- (Total Travel: {total_time} min; Total Appts: {appt_count})")
        # else:
            #print(f" ----", end="")
    #print("\n-------------------------",end="\n")
    print(f"\nSales Rep {i+1} visited appointments are: ", visited_list , end="\n============================\n\n")


# def apptlist():
#     appointlist=appointment_allocation
#     output_list = [[k] + [v['Full_addr'] for v in appointlist[k]] for k in appointlist]
#     return output_list

# for i in apptlist():
#     print(i)
# for i, loc in enumerate(apptlist()):
#     print(f"Route map for salesrep {i+1}: ", end="")
#     total_time = 0
#     appt_count = 0
#     for j, (origin, dest) in enumerate(zip(loc, islice(cycle(loc), 1, None))):
#         route, travel_time, distance = optdisndtime(origin, dest)
#         total_time += int(travel_time.split()[0])
#         if j < len(loc)-1:
#             appt_count += 1
#             print(f"Home addr: '{origin}' ---(Travel: {travel_time},Distance: {distance}, Route: {route})---> Appt",j+1,":", end="")
#         if j == len(loc)-1:
#             print(f"'{origin}' ---> Home Addr (Total Travel: {total_time} min; Total Appts: {appt_count})","\n")
#         else:
#             print(f"", end="")

'''
def load_sales():
	sales = []
	with open(salesrep_data, 'r') as file:
		reader = csv.DictReader(file)
		for row in reader:
			sales.append({
				'ID': int(row['ID']),
				'Salesrep_name': row['Salesrep_name'],
				'Home_addr': row['Home_addr'],
				'Capacity': int(row['Capacity']),
			})
	return sales

def load_customers():
	customers = []
	with open(appointments_data, 'r') as file:
		reader = csv.DictReader(file)
		for row in reader:
			customers.append({
				'ID': int(row['ID']),
				'Customer_name': row['Customer_name'],
				'Full_addr': row['Full_addr'],
				'Start_time': datetime.datetime.strptime(row['Start_time'], '%I:%M %p'),
				'Duration': int(row['Duration']),
				'Sales_rep': None  # initially null
			})
	return customers
for i in load_sales():
	print(i["Home_addr"])
'''