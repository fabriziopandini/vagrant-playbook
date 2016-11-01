import sys
from optparse import OptionParser

def main(args=None): 
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = OptionParser(usage="vagrant-playbook [OPTIONS]",
    description="Parser for declarative cluster definition for vagrant, aka vagrant playbooks, and generates a yaml to be used with vagrant-compose plugin.")

    parser.add_option("-f", "--file", dest="file",
                      help="File name containing the vagrant playbook", metavar="PLAYBOOK FILE")
    parser.add_option("-p", "--playbook", dest="playbook",
                      help="String containing the vagrant playbook", metavar="PLAYBOOK STRING")

    (options, args) = parser.parse_args()

    if not options.file and not options.playbook:
        parser.error('Playbook not provided. Execute vagrant-playbook -h for available options.')

    from vagrantplaybook.playbook.executor import Executor
    yaml = Executor().execute(yamlfile=options.file, yamlplaybook=options.playbook)

    print (yaml)


if __name__ == "__main__":
    main()
