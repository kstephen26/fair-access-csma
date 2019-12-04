#!/bin/bash
for i in {1..100} 
do
	if [ $i -eq 2 ] || [ $i -eq 5 ] || [ $i -eq 10 ] || [ $i -eq 25 ] || [ $i -eq 50 ] || [ $i -eq 75 ] || [ $i -eq 100 ]
	then
		for x in {1..3}
		do
		echo $x Run
		python3 project.py 4 $i 100 all normal NullMacExponentialBackoff	
		done
	fi
done

for i in {1..100} 
do
	if [ $i -eq 2 ] || [ $i -eq 5 ] || [ $i -eq 10 ] || [ $i -eq 25 ] || [ $i -eq 50 ] || [ $i -eq 75 ] || [ $i -eq 100 ]
	then
		for x in {1..3}
		do
		echo $x Run
		python3 project.py 4 $i 100 neighbors normal NullMacExponentialBackoff
		done
	fi
done