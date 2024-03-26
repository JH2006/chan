FROM gcc:8.1.0

maintainer JH 

run apt update
run apt install -y net-tools
run apt install -y vim
run apt install -y openssh-server
run apt install -y build-essential
run apt install -y gdb
run echo "root:password"|chpasswd
run ssh-keygen -A
run mkdir -p /var/run/sshd

expose 22 8080

docker run -it -p 22:22 -p 8080:8080 -v /Users/jerryhuang/Developer/Trading :/home/trading -name ubuntu ubuntu