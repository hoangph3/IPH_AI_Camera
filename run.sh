docker run --rm --net=host \
-v $(pwd)/ansible:/data
willhallonline/ansible:latest ansible-playbook $1