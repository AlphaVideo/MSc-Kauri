#!/bin/bash

for j in {1..4}
do
  for i in {1..1}
  do
        docker stack deploy -c hotstuff${j}.yaml hotstuff1 &
        sleep 410

        for container in $(docker ps -q -f name="server")
        do
                docker exec -it $container bash -c "cd libhotstuff && tac log* | grep -m1 'commit <block'"
                docker exec -it $container bash -c "cd libhotstuff && tac log* | grep -m1 'x now state'"

                break
        done

        docker stack rm hotstuff1
        sleep 30

  done
done

todo, move the yaml file to be produced by a script, and add manually the values in it, so we can easily increase the pipelining and alter params if we want
I wonder if we can adjust the other values.