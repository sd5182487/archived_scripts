#    !! Warning!!
#    This wget cmd takes -H option which will create lots of folders
#    To restrict it inside ccs.neu.edu, dont include this option

echo "if you are running this with ubuntu or other linux flavors contain timeout cmd"
echo "it's easier to do : timeout 600s p1.sh"
echo "more details inside script comment part"

#start crawling the links
wget -U "htdig" --spider -r -H -w 5 -A html,pdf -D 'neu.edu,ccs.neu.edu' -e robots=on -o raw.txt http://www.ccs.neu.edu
#please stop wget cmd after >500s then run the following cmd

#if you are running this with ubuntu or other linux flavors contain timeout cmd
#it's easier to do:
#
#timeout 600s p1.sh
#
#then we dont need to manually terminate the script
#BUT,I'm using a mac OS so....
#you know it.

#output the first unique 100 links
cat raw.txt | grep Removing | awk '{print $2}' | sed 's/^`//' | sed "s/'$//" | head -n100 > p1.txt
#grep -A1 '[txt/html]|[application/pdf]' | grep Removing | awk '{print $2}' | sed 's/^`//' | sed "s/'$//" | head -n100 > p1.txt
#trying to get rid of www.ccs.neu.edu/robots.txt. but doesnt matter as Mat said