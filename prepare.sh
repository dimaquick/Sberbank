events=$1
train=$2

mkdir -p stat
cat $events | cut -f 1,3 -d "," | LANG=c sort | uniq | cut -f 2 -d "," | LANG=c sort | uniq -c | awk '{print $1"\t"$2;}' > stat/mcc_user
cat $events | cut -f 1,4 -d "," | LANG=c sort | uniq | cut -f 2 -d "," | LANG=c sort | uniq -c | awk '{print $1"\t"$2;}' > stat/type_user
cat $events | awk -F "," 'length($6)>0' | cut -f 1,6 -d "," | LANG=c sort | uniq | cut -f 2 -d "," | LANG=c sort | uniq -c | \
    LANG=c sort -n -r -k 1,1 | awk '$1>200{print $1"\t"$2;}' > stat/term
cat $events | tr ',:' '  ' | awk '{h=$3*3600+$4*60+$5;if(p==$1&&pd==$2&&h<900+ph){print p","$6","pm;}p=$1;pm=$6;pd=$2;ph=$3*3600+$4*60+$5;}' | \
    LANG=c sort | uniq | awk -F "," '$2!=$3{print $2"_"$3;}' | LANG=c sort | uniq -c | awk '{print $1"\t"$2;}' > stat/pairs_mcc

cat $train $events | awk -F "," 'NF==2{gender[$1]=$2;}NF>2&&$5<0&&$1 in gender&&gender[$1]==1{print $3"\t"$5;}' | LANG=c sort | \
    awk '{if(p!=$1){if(a>0)printf "%s\t%lf\n", p, a/5306;a=0;p=$1;}a-=$2;}END{printf "%s\t%lf\n", p, a/5306;}' > female

cat $train $events | awk -F "," 'NF==2{gender[$1]=$2;}NF>2&&$5<0&&$1 in gender&&gender[$1]==0{print $3"\t"$5;}' | LANG=c sort | \
    awk '{if(p!=$1){if(a>0)printf "%s\t%lf\n", p, a/6694;a=0;p=$1;}a-=$2;}END{printf "%s\t%lf\n", p, a/6694;}' > male

paste female male | awk '{print $1"\t"$2"\t"$4"\t"$2/$4;}' | LANG=c sort -g -k 4,4 > female_male
head -n 18 female_male > stat/mcc_female
tail -n 66 female_male > stat/mcc_male

cat $train $events | awk -F "," 'NF==2{gender[$1]=$2;}NF>2&&$5<0&&$1 in gender&&gender[$1]==1{print $4"\t"$5;}' | LANG=c sort | \
    awk '{if(p!=$1){if(a>0)printf "%s\t%lf\n", p, a;a=0;p=$1;}a-=$2;}END{printf "%s\t%lf\n", p, a;}' > female

cat $train $events | awk -F "," 'NF==2{gender[$1]=$2;}NF>2&&$5<0&&$1 in gender&&gender[$1]==0{print $4"\t"$5;}' | LANG=c sort | \
    awk '{if(p!=$1){if(a>0)printf "%s\t%lf\n", p, a;a=0;p=$1;}a-=$2;}END{printf "%s\t%lf\n", p, a;}' > male

LANG=c join -a 1 female male | awk '{a=$3;if($3=="")a=0;printf "%s\t%lf\t%lf\t%lf\n", $1,$2,a,$2/(0.0000001+$3);}' | LANG=c sort -g -r -k 4,4 > female_male
tail -n 10 female_male > stat/type_female
head -n 13 female_male > stat/type_male

cat $train $events | awk -F "," 'NF==2{gender[$1]=$2;}NF>2&&$5>0&&$1 in gender&&gender[$1]==1{print $3"\t"$5;}' | LANG=c sort | \
    awk '{if(p!=$1){if(a>0)printf "%s\t%lf\n", p, a;a=0;p=$1;}a+=$2;}END{printf "%s\t%lf\n", p, a;}' > female

cat $train $events | awk -F "," 'NF==2{gender[$1]=$2;}NF>2&&$5>0&&$1 in gender&&gender[$1]==0{print $3"\t"$5;}' | LANG=c sort | \
    awk '{if(p!=$1){if(a>0)printf "%s\t%lf\n", p, a;a=0;p=$1;}a+=$2;}END{printf "%s\t%lf\n", p, a;}' > male

LANG=c join -a 1 female male | awk '{a=$3;if($3=="")a=0;print $1"\t"$2"\t"a"\t"$2/(0.0000001+$3);}' | LANG=c sort -g -k 4,4 -r | head -n 50 > stat/mcc_male_plus
LANG=c join -a 1 male female | awk '{a=$3;if($3=="")a=0;print $1"\t"$2"\t"a"\t"$3/(0.0000001+$2);}' | LANG=c sort -g -k 4,4 -r | tail -n 50 > stat/mcc_female_plus

