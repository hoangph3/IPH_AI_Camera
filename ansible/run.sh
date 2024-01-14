docker run --rm --net=host \
-v $(pwd)/ansible:/data \
hoangph3/ansible:$(uname -m)-2.10 ansible-playbook $1
