#!sh

for fn in tests/integration/test*.py;
do

    output=$(./clispec.py $fn 2>&1)
    retcode=$?

    if [ $retcode != 0 ]
    then
        echo
        echo %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        echo FAILED  $fn
        echo '>>>'
        printf "%s\n" "$output"
        echo %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        echo
    else
        echo SUCCESS $fn
    fi
done
