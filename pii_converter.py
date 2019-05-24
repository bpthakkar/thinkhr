import sys
import getopt
import os
import re
import json


def line_validation(line):
    # This function is to validate line based on acceptable patterns,
    # Pattern can be added or removed depending on the acceptance criteria
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
    # Function will parse the line and return the dictionary object
    # Since there are 2 possible acceptable format for the first name and last name, added logic to handle that
    # separately

    data = {
        'firstname':  '',
        'lastname': '',
        'zipcode': '',
        'phonenumber': '',
        'color': ''
    }

    fields = line.split(',')

    # Check for the field count fo find the first name and last name values correctly
    if len(fields) == 4:
        field = fields.pop(0)
        names = field.split()
        data['firstname'] = names[0]
        data['lastname'] = names[1]
    elif len(fields) == 5:
        data['firstname'] = fields.pop(0)
        data['lastname'] = fields.pop(0).strip()

    # Assigning remaining fields value using regex since it can be in any order
    for count, field in enumerate(fields, 1):
        field = field.strip()
        if re.search('^[0-9]{5}', field):
            # print('Zip =', field)
            data['zipcode'] = field
        elif re.search(r'^\(?[0-9]{3}\)?(-|\s)[0-9]{3}(-|\s)[0-9]{4}', field):
            # print('Phone # =', field)
            data['phonenumber'] = field
        elif re.search(r'[a-z|A-Z]*',field):
            data['color'] = field

    # print(data)
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

    usage = 'USAGE: python pii_converter.py --in inputfile [--out outputfile] \n' \
            'USAGE: python pii_converter.py inputfile [outputfile]'

    # parsing command line arguments and validating the same
    try:
        opts, args = getopt.getopt(argv, 'h', ['in=', 'out='])
    except getopt.GetoptError:
        print(usage)
        sys.exit()

    # Get command argument if no flag used, Print the usage if there are no argument passed
    if not opts and not args:
        print(usage)
        sys.exit()
    elif args and len(args) >= 2:
        inputfile = args[0]
        outputfile = args[1]
    elif args:
        inputfile = args[0]

    # Get the commandline details using flag
    for opt, param in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt == '--in':
            inputfile = param
        elif opt == '--out':
            outputfile = param
        else:
            print(usage)
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
                print('VALID ==>> ', line)
                entry_list.append(line_parse(line))
            else:
                print('NOT VALID ==>> ', line)
                error_list.append(index)

        infile_handler.close()

        pii_json['enteries'] = sorted(entry_list, key=lambda entry: entry['lastname']+', '+entry['firstname'])
        # print('NOT SHORTED ', entry_list)
        # print('SHORTED ', sorted(entry_list, key=lambda entry: entry['lastname']+', '+entry['firstname']))
        pii_json['errors'] = error_list

        print('Final formatted JSON data')
        print(json.dumps(pii_json, indent=2))

        if outputfile == '':
            outputfile = inputfile + '.json'

        outfile_handler = open(outputfile, "w")
        outfile_handler.write(json.dumps(pii_json, indent=2))
        outfile_handler.close()


if __name__ == "__main__":
    main(sys.argv[1:])
