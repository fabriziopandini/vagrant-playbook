Declarative cluster definition for vagrant, to be used with vagrant-compose plugin.

vagrant-compose is a vagrant plugin, that can be used for creating complex multi-machine scenarios including several set of nodes/virtual machines, each one with different characteristic, software stacks and configuration.

The DSL used by vagrant-compose requires some ruby knowledge, because the Vagrantfile itself is based on ruby, and this fact sometimes is and obstacle for people with limited programming background.

By using vagrant-playbook this issue is mostly addressed because the definition of the cluster is done in yaml, and the ruby programming part within the Vagrantfile is reduced to the minimum.
 
see github: https://github.com/fabriziopandini/vagrant-playbook for detailed documentation.
