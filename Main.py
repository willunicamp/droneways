from Controller import Controller
import time
import sys
def main():
    graph_path = sys.argv[1]
    save_path = sys.argv[2]
    c = Controller(graph_path,save_path)
    #c.draw_graphs()
    #return
#    c.min_max_path_charts()
    start = ntimes = step = 0

    while(True):
        option = int(input("Select option: \n"+
                       "1. Execute fishbone heuristics \n"+
                       "2. Execute spiderweb heuristics\n"+
                       "3. Calculate properties\n"
                       "4. Compare heuristics and generate plot\n"))
        t = time.time()
        if option in {1,2}:
           start = int(input("Start: "))
           ntimes = int(input("Iterations: "))
           step = int(input("Step: "))

        if(option == 1):
            c.executeFishbone(start, ntimes, step)
        elif(option == 2):
            c.executeSpiderweb(start, ntimes, step)
        elif(option == 3):
            c.calculate_properties()
        elif(option == 4):
            c.compare()
        else:
            break
        print("Time: "+str(time.time()-t))

    #c.draw_graphs()
#    t = time.time()
#    print("Efficiency ratio: "+str(c.efficiency()))
#    print("Time: "+str(time.time()-t))
#    print("Edges ratio: " + str(c.ratio()))
if __name__ == "__main__":
    main()
