# vagrant-playbook
Declarative cluster definition for vagrant, to be used in combination with vagrant-compose plugin.

vagrant-compose is a vagrant plugin, that can be used for creating complex multi-machine scenarios including several set of nodes/virtual machines, each one with different characteristic, software stacks and configuration.

The DSL used by vagrant-compose required some ruby knowledge, because the Vagrantfile itself is based on ruby, and this fact sometimes is and obstacle for people with limited programming background.

By using vagrant-playbook this problem is mostly assressed because the definition of the cluster is done in yml, and the ruby programming part is reduced to the minimum.
