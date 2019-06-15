allLocations = [[1,3], [2,3]]
truckCapacity = 2

# print(allLocations[0])

Truckloads = []
if len(allLocations) > truckCapacity:
    for i in range(truckCapacity):
        min_value = 9999999999
        index = -1
        for j in range(len(allLocations)-1):
            x = allLocations[j][0]
            y = allLocations[j][1]
            d = (x*x) + (y*y)
            if(d < min_value):
                index = j
            Truckloads.append(allLocations[index])
            del allLocations[index]
    print(Truckloads)
else:
    print(allLocations)
            

# List<List<Integer>> TruckLoads = new ArrayList<ArrayList<Integer>>()
# for(int i=0; i<truckCapacity; i++) {
#     List<Integer> inner = new ArrayList<Integer>
#     min = 9999999999
#     index = -1
#     for(int j=0; allLocations.size(); j++) {
#         x = allLocations[j][0]
#         y = allLocations[j][1]
#         d = (x*x) + (y*y)
#         if(d < min) {
#             index = j
#         }
#     }
#     TruckLoads.append(allLocations[index])
#     allLocations.remove(index) 
# }