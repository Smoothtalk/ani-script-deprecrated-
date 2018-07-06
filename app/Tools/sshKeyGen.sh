#!/bin/bash
host=$1
port=$2

makePub="echo -e  \'n\n\'|ssh-keygen -q -t rsa -N \"\" -f ~/.ssh/id_rsa"
eval $makePub
echo ""

if [ $port = 22 ]
then
  makeSSHDir1="ssh "
  makeSSHDir2=" mkdir -p .ssh"
  makeSSHDir=$makeSSHDir1$host$makeSSHDir2
  #echo $makeSSHDir
  eval $makeSSHDir
  appendPub1="cat ~/.ssh/id_rsa.pub | ssh "
  appendPub2=" 'cat >> .ssh/authorized_keys'"
  appendPub=$appendPub1$host$appendPub2
  #echo $appendPub
  eval $appendPub
else
  makeSSHDir1="ssh -p"
  makeSSHDir2=' '
  makeSSHDir3=" mkdir -p .ssh"
  makeSSHDir=$makeSSHDir1$port$makeSSHDir2$host$makeSSHDir3
  #echo $makeSSHDir
  eval $makeSSHDir
  appendPub1="cat ~/.ssh/id_rsa.pub | ssh -p"
  appendPub2=" "
  appendPub3=" 'cat >> .ssh/authorized_keys'"
  appendPub=$appendPub1$port$appendPub2$host$appendPub3
  #echo $appendPub
  eval $appendPub
fi
