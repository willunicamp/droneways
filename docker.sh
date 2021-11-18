#buid docker image and save to disk.
#do it only once
docker build -t willphd/droneways:latest .

#run image after created
sudo docker run -it -u root -v /home/will/workspace/drones_scripts/final_version:/home/will/src/ -w /home/will willphd/droneways bash

