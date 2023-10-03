#!/bin/bash
APPS="normal double-speed unlimited-speed"
cd my-apps
for a in $APPS
do
    echo ${a}
    tar --disable-copyfile -czf ${a}.spl ${a}
done
cd ..
