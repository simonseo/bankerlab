mkdir input
mkdir output
mkdir detailed-FIFO
mkdir detailed-Banker

cd input
for i in {10..12}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/input-$i" > input-$i.txt
  done
for i in {1..9}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/input-0$i" > input-0$i.txt
  done
cd ..

cd output
for i in {10..12}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/output-$i" > output-$i.txt
  done
for i in {1..9}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/output-0$i" > output-0$i.txt
  done
cd ..

cd detailed-Banker
for i in {10..12}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/output-$i-banker-detailed" > output-banker-detailed-$i.txt
  done
for i in {1..9}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/output-0$i-banker-detailed" > output-banker-detailed-0$i.txt
  done
  rm output-banker-detailed-03.txt
  rm output-banker-detailed-08.txt
  rm output-banker-detailed-11.txt
cd ..

cd detailed-FIFO
for i in {10..12}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/output-$i-fifo-detailed" > output-fifo-detailed-$i.txt
  done
for i in {1..9}
  do
    curl "https://cs.nyu.edu/~gottlieb/courses/os202/labs/lab3/output-0$i-fifo-detailed" > output-fifo-detailed-0$i.txt
  done
  rm output-fifo-detailed-04.txt
  rm output-fifo-detailed-08.txt
  rm output-fifo-detailed-09.txt
  rm output-fifo-detailed-10.txt 
  rm output-fifo-detailed-11.txt
cd ..
