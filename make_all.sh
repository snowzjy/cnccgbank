#! /bin/bash

if [[ $1 == "all" || $1 == "*" ]]; then
    SECTION=""
    TARGET="*"
elif [[ $1 =~ ^[0-9]{2}$ ]]; then
    SECTION=${1:-00}
    TARGET="chtb_${SECTION}*"
else
    TARGET=`basename $1`
fi

echo Started at: `date`
./make_lab.sh "$TARGET" \
&& ./make_fix.sh "$TARGET" \
&& ./make_ccgbank.sh "$TARGET"  \
&& ./t -q -D final_dots -lapps.sanity -r SanityChecks -0 final/"$TARGET" 
echo Finished at: `date`
