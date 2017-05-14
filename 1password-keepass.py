#!/usr/bin/eny python

import sys
import os
import csv
from xml.sax.saxutils import escape

def is_valid_file(parser, arg):
    """
    Check if arg is a valid file that already exists on the file system.

    Parameters
    ----------
    parser : argparse object
    arg : str

    Returns
    -------
    arg
    """
    arg = os.path.abspath(arg)
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def get_parser():
    """Get parser object for script """

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_file',
                        type=lambda x: is_valid_file(parser, x),
                        metavar='FILE',
                        help='a 1Password TAB delimited text file')
    parser.add_argument('-q', '--quiet',
                        dest='verbose',
                        action="store_false",
                        default=True,
                        help='suppress output to standard out')
    parser.add_argument("-l", "--lang",
                        dest="language",
                        default="en",
                        metavar='LANG',
                        help="input file header language")
    return parser

# return a dictionary of possible fieldnames provided by 1Password
# left = english value, right = other language
# TODO: parse all provided fieldnames and translate instead of return hardcoded values
def set_fieldname_dict(fieldnames, language):

    if language not in ['en', 'nl']:
        sys.exit('The language \'%s\' is not supported.' % language)

    dict = {} # start with empty dictionary

    # rename supported keepass fields
    for fieldname in fieldnames:
        if language == 'nl':
            if fieldname == 'Titel':
                dict['title'] = fieldname
            elif fieldname == 'Gebruikersnaam':
                dict['username'] = fieldname
            elif fieldname == 'Wachtwoord':
                dict['password'] = fieldname
            elif fieldname == 'Webadres':
                dict['url'] = fieldname
            elif fieldname == 'Notities':
                dict['comment'] = fieldname
            elif fieldname == 'Type': # not in keepass, but needs to be skipped
                dict['type'] = fieldname
            # else:
            #     dict[fieldname] = fieldname
        else: # language == 'en'
            if fieldname == 'title':
                dict['title'] = fieldname
            elif fieldname == 'username':
                dict['username'] = fieldname
            elif fieldname == 'password':
                dict['password'] = fieldname
            elif fieldname == 'URL/Location':
                dict['url'] = fieldname
            elif fieldname == 'notes':
                dict['comment'] = fieldname
            elif fieldname == 'type': # not in keepass, but needs to be skipped
                dict['type'] = fieldname
            # else:
            #     dict[fieldname] = fieldname

    return dict

def none_empty(s):
    if s is None:
        return ''
    else:
        return s

def append_comment(comment, note):
    if comment == '':
        return note
    else:
        return comment + '\n' + note

def prepend_comment(comment, note):
    if comment == '':
        return note
    else:
        return note + '\n' + comment

def main(argv):

    args = get_parser().parse_args()

    if args.verbose:
        print('IMPORTANT NOTE: this script ignores all fields that are not used in KeePass by purpose.')

    input_file = args.input_file
    output_file = input_file + '.xml'

    with open(input_file, 'rt', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t', quotechar='"')
        try:
            fieldnames = set_fieldname_dict(reader.fieldnames, args.language)
            # print(fieldnames)

            fo = open(output_file, 'wt', newline='\n')

            print("<!DOCTYPE KEEPASSX_DATABASE>", file=fo)
            print("<database>", file=fo)
            print("    <group>", file=fo)
            print("        <title>1Password Import</title>", file=fo)
            print("        <icon>1</icon>", file=fo)

            i = 0
            for row in reader:
                i += 1

                title = ''
                username = ''
                password = ''
                url = ''
                comment = ''
                type = ''

                # loop trough columns
                for fieldname in fieldnames:
                    if fieldname == 'title':
                        title = escape(none_empty(row[fieldnames[fieldname]]))
                    elif fieldname == 'username':
                        username = escape(none_empty(row[fieldnames[fieldname]]))
                    elif fieldname == 'password':
                        password = escape(none_empty(row[fieldnames[fieldname]]))
                    elif fieldname == 'url':
                        url = escape(none_empty(row[fieldnames[fieldname]]))
                    elif fieldname == 'comment':
                        comment = prepend_comment(comment, escape(none_empty(row[fieldnames[fieldname]])))
                    elif fieldname == 'type':
                        pass # skip 'type'
                    # else:
                    #     # add non-standard fields to comment
                    #     comment = append_comment(comment, escape(none_empty(row[fieldnames[fieldname]]))) # append

                if not (type == '' or type == 'Login'):
                    continue # skip if not a Login

                if title == '' and password == '' and username == '' and comment == '':
                    if args.verbose:
                        print ('Skipping entry {}. No data.'.format(i))
                    continue

                if title != '' and password == '' and username == '' and comment == '' and url == '':
                    if args.verbose:
                        print ('Skipping entry {}. Only title \'{}\'. '.format(i, title))
                    continue

                if title == 'Login' and url == 'http://www.example.com':
                    if args.verbose:
                        print ('Skipping entry {}. Example line.'.format(i))
                    continue

                print("        <entry>", file=fo)
                print("            <title>%s</title>" % title, file=fo)
                print("            <username>%s</username>" % username, file=fo)
                print("            <password>%s</password>" % password, file=fo)

                if url != '':
                    print("            <url>%s</url>" % url, file=fo)

                if comment != '':
                    print("            <comment>%s</comment>" % comment, file=fo)

                print("        </entry>", file=fo)

            print("    </group>", file=fo)
            print("</database>", file=fo)
            fo.close()

            print('Script processed {} entries'.format(i))
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))

if __name__ == "__main__":
    main(sys.argv)
