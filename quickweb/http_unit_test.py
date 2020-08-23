#! /usr/bin/env python
"""HTTP Unit Testing

Usage:
    http_unit_test <server_base_url> <test_file>

Options:
    -h --help     Show this screen.
"""
import sys
import yaml
from docopt import docopt
from os.path import dirname, realpath, join
from webtest import TestApp
from colorama import init

init()

# Make sure we use the source directory for imports when running during development
script_dir = join(dirname(realpath(__file__)), "..")
sys.path.insert(0, script_dir)

from quickweb.colorhelper import info, print_success, print_error  # noqa: E402


def validate_headers(response, validation_rules):
    validate_headers = validation_rules.get("headers")
    if validate_headers:
        for header_match in validate_headers:
            (header_name, header_value) = list(header_match.items())[0]
            found_header = False
            for resp_header_name, resp_header_value in response.headerlist:
                if header_name.lower() == resp_header_name.lower():
                    if resp_header_value.lower() != header_value.lower():
                        print()  # previous print does not have end of line
                        print_error(
                            "FAILED: %s %s != %s "
                            % (header_name, resp_header_value, header_value)
                        )
                        exit(1)
                    else:
                        found_header = True
                        break
            if not found_header:
                print()  # previous print does not have end of line
                print_error("FAILED: Header %s missing from response" % header_name)
                print_error("Available Headers" + str(response.headerlist))
                exit(1)


def validate(response, validation_rules):
    """
    Validates an HTTP response, headers and body (when provided for validation)
    """
    validate_headers(response, validation_rules)

    validate_body_list = validation_rules.get("body", [])
    if validate_body_list and isinstance(validate_body_list, str):
        validate_body_list = [validate_body_list]

    last_found_pos = None
    last_validate_body = None
    # webtest resturns the body as bytes() on python3, we need to decode it for find()
    response_body = str(response.body)
    for validate_body in validate_body_list:
        find_pos = response_body.find(validate_body, last_found_pos)
        if find_pos == -1:
            print()  # previous print does not have end of line
            if last_validate_body:
                print_error(
                    "FAILED: '%s' was not found after '%s', in body:\n%s "
                    % (validate_body, last_validate_body, response_body)
                )
            else:
                print_error(
                    "FAILED: '%s' is missing from body:\n%s "
                    % (validate_body, response_body)
                )
            exit(1)
        last_found_pos = find_pos + len(validate_body)
        last_validate_body = validate_body


def run_test(server_base_url, test_filename):
    """ Run test case fro mthe test file """
    print("Runing tests at %s using %s" % (info(server_base_url), info(test_filename)))
    app = TestApp(server_base_url)

    with open(test_filename, "r") as yaml_file:
        doc = yaml.safe_load_all(yaml_file)
        for test_doc in doc:
            title = test_doc["title"]
            padding = (80 - len(title)) * " "
            print("- %s%s- " % (test_doc["title"], padding), end="")
            test_input = test_doc.get("input")
            if not test_input:
                continue
            # webtest does the status validation based on the status input parameter
            expect_status = test_doc["validate"].get("status")
            response = app.get(test_input["url"], status=expect_status)
            validate(response, test_doc["validate"])
            print_success("OK")


def main():
    """ main function """
    arguments = docopt(__doc__, version="HTTP Unit Testing (latest)")
    run_test(arguments["<server_base_url>"], arguments["<test_file>"])


if __name__ == "__main__":
    main()
