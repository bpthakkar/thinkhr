import sys
import getopt
import os
import re
import json


def line_validation(line):

    # Valid patter can be added or deleted based on the requirement
    valid_patterns = \
        [r'^(\D*)(,\s)+([a-z|A-Z]*)(,\s)+[0-9]{5}(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}(,\s)+([a-z|A-Z]*)$',
         r'^(\D*)(,\s)+([a-z|A-Z]*)(,\s)+[0-9]{5}(,\s)+([a-z|A-Z]*)(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}$',
         r'^(\D*)(,\s)+([a-z|A-Z]*)(,\s)+([a-z|A-Z]*)(,\s)+[0-9]{5}(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}$',
         r'^(\D*)(,\s)+([a-z|A-Z]*)(,\s)+([a-z|A-Z]*)(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}(,\s)+[0-9]{5}$',
         r'^(\D*)(,\s)+([a-z|A-Z]*)(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}(,\s)+([a-z|A-Z]*)(,\s)+[0-9]{5}$',
         r'^(\D*)(,\s)+([a-z|A-Z]*)(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}(,\s)+[0-9]{5}(,\s)+([a-z|A-Z]*)$',
         r'^(\D*)(,\s)+([a-z|A-Z]*)(,\s)+[0-9]{5}(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}$',
         r'^(\D*)(,\s)+[0-9]{5}(,\s)+([a-z|A-Z]*)(,\s)+\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}$']

    for pattern in valid_patterns:
        matched = re.search(pattern, line)
        if matched:
            return True
    return False


def line_parse(line):
    data = {
        'firstname':  '',
        'lastname': '',
        'zipcode': '',
        'phonenumber': '',
        'color': ''
    }

    fields = line.split(',')

    # Assign approriate first name and last name
    if len(fields) == 4:
        field = fields.pop(0)
        names = field.split()
        data['firstname'] = names[0]
        data['lastname'] = names[1]
    elif len(fields) == 5:
        data['firstname'] = fields.pop(0)
        data['lastname'] = fields.pop(0).strip()

    for count, field in enumerate(fields, 1):
        field = field.strip()
        if re.search('^[0-9]{5}', field):
            # print('Zip =', field)
            data['zipcode'] = field
        elif re.search(r'^\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}', field):
            # or re.search('',field)
            # print('Phone # =', field)
            data['phonenumber'] = field
        elif re.search(r'[a-z|A-Z]*',field):
            data['color'] = field
            # print('Not Identified ', field)

    print(data)
    return data


def main(argv):
    inputfile = ''
    outputfile = ''
    entry_list = []
    error_list = []

    pii_json = {
        'enteries': '',
        'errors': ''
    }

    # parsing command line arguments
    try:
        opts, args = getopt.getopt(argv, 'h', ['in=', 'out='])
    except getopt.GetoptError:
        print('USAGE: python pii.py --in <inputfile> [--out <outputfile>]')
        print('USAGE: python pii.py <inputfile> [<outputfile>]')
        sys.exit()

    # Get the command details if there are no flag used
    if not opts and not args:
        print('USAGE: python pii.py --in <inputfile> [--out <outputfile>]')
        print('USAGE: python pii.py <inputfile> [<outputfile>]')
        sys.exit()
    elif args and len(args) >= 2:
        inputfile = args[0]
        outputfile = args[1]
    elif args:
        inputfile = args[0]

    # Get the commandline details using flag
    for opt, param in opts:
        if opt == '-h':
            print('USAGE: python pii.py --in <inputfile> [--out <outputfile>]')
            print('USAGE: python pii.py <inputfile> [<outputfile>]')
            sys.exit()
        elif opt == '--in':
            inputfile = param
        elif opt == '--out':
            outputfile = param
        else:
            print('USAGE: python pii.py --in <inputfile> --out <outputfile>')
            sys.exit()

    # print('In file name', inputfile)
    # print('Out file name', outputfile)

    # Check for the file existence and content
    if not os.path.exists(inputfile) or not os.stat(inputfile).st_size:
        print('File does not exist or empty')
    else:
        try:
            infile_handler = open(inputfile, 'r')
        except IOError:
            print('Unable to ready input file')

        for index, line in enumerate(infile_handler):
            # print(index, ' => ', line)
            val = line_validation(line)
            if val:
                entry_list.append(line_parse(line))
            else:
                error_list.append(index)

        infile_handler.close()

        pii_json['enteries'] = sorted(entry_list, key=lambda entry: entry['lastname']+', '+entry['firstname'])
        # print('NOT SHORTED ', entry_list)
        # print('SHORTED ', sorted(entry_list, key=lambda entry: entry['lastname']+', '+entry['firstname']))
        pii_json['errors'] = error_list

        print('JSON ==== ', json.dumps(pii_json, indent=2))

        if outputfile == '':
            outputfile = inputfile + '.json'

        outfile_handler = open(outputfile, "w")
        outfile_handler.write(json.dumps(pii_json, indent=2))
        outfile_handler.close()


if __name__ == "__main__":
    main(sys.argv[1:])
