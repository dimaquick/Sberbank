models=$1
train=$2
test=$3
events=$4
mkdir -p predict
for i in $(jot $models 0); do
    python main.py -l $train -v $test -d 3 -e 0.005 -S 0.65 -R $i -T 15500 -E $events -s ../stat/ -V -O predict/predict$i > a 2> b
done
cd predict
paste predict* | awk '{a=0;for(i=1;i<=NF;++i)a+=$i;print a/NF;}' | paste - $test | awk 'BEGIN{print "customer_id,gender";}{print $2","$1;}' > submission
cd ..
