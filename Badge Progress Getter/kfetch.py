import argparse
import os
import sys
import re
import requests
import requests.exceptions
import configparser
import json
from datetime import datetime
from bs4 import BeautifulSoup
import badgegetter

# PROBLEM/LANGUAGE PAIRS
#solved1 =set()
#solved2 = set()

_EMAIL = None # Required by the user, will be updated in the main function
_DEFAULT_CONFIG = '/usr/local/etc/kattisrc'

_HEADERS = {'User-Agent': 'kattis-accepted-fetch by {}'.format(_EMAIL),
            'From':_EMAIL}

def get_url(cfg, option, default):
    if cfg.has_option('kattis', option):
        return cfg.get('kattis', option)
    else:
        return 'https://{}/{}'.format(cfg.get('kattis', 'hostname'), default)

def get_config():
    """ Returns a ConfigParser object for the .kattisrc file(s) """
    cfg = configparser.ConfigParser()
    if os.path.exists(_DEFAULT_CONFIG):
        cfg.read(_DEFAULT_CONFIG)

    cfg.read("kattisrc.txt")
    return cfg

def login(login_url, username, password=None, token=None):
    """ Authenticates users """
    login_args = {'user': username, 'script': 'true'}
    if password:
        login_args['password'] = password
    if token:
        login_args['token'] = token
    return requests.post(login_url, data=login_args, headers=_HEADERS)

def login_from_config(cfg):
    """ Authenticates user from .kattisrc file """
    username = cfg.get('user', 'username')
    password = token = None
    try:
        password = cfg.get('user', 'password')
    except configparser.NoOptionError:
        pass
    try:
        token = cfg.get('user', 'token')
    except configparser.NoOptionError:
        pass
    if password is None and token is None:
        raise configparser.Error('It looks like the .kattisrc file appears to be corrupted.')
    loginurl = get_url(cfg, 'loginurl', 'login')
    return login(loginurl, username, password, token)

def submissions(submissions_url, cookies):
    """ Get submissions """
    data = {'script': 'true'}
    return requests.get(submissions_url, data=data, cookies=cookies, headers=_HEADERS)

def get_problem(keys, soup):
    """ Format individual solved problem """
    print()
    print("SOUP")
    print(soup)
    print("SOUPPPP")
    print()
    link = soup.find(class_='name_column').find('a', href=True)['href']
    row = soup.get_text()
    # print(dict(zip(keys, [link.split('/')[2]] + list(row.strip().split('\n')))))
    return dict(zip(keys, [link.split('/')[2]] + list(row.strip().split('\n'))))

def get_stats(cfg, login_reply, problem_cnt=None):
    """ Gets the users stats """
    username = cfg.get('user', 'username')
    profile_url = get_url(cfg, '', 'users/%s' % username)
    try:
        print("TESTING: ", profile_url)
        result = submissions(profile_url, login_reply.cookies)
    except requests.exceptions.RequestException as err:
        print('Profile connection failed:', err)
        sys.exit(1)
    soup = BeautifulSoup(result.text, 'html.parser')
    header = soup.find('div', {'class': 'rank clearfix'})
    out = []
    for tr in header.find_all('tr'):
        out.append([td.text.strip() for td in tr.find_all('td')])

    if problem_cnt is not None:
        out[0].append('Solved')
        out[1].append(str(problem_cnt))
    return dict(zip(out[0], out[1]))

def extract_problems(cfg, login_reply, filename='solved'):
    """ Stores solved prolbems and stats in .json file """
    data = {}
    solved = []
    badges = []

    # CHANGE: users/friggstad instead of problems
    # CHANGE: Didn't scrape first page as a "test" like Jason did
    # TODO: make this users/<profile_id> where profile_id is scraped from the kattisrc file

    profile_url = get_url(cfg, '', 'users/' + cfg.get('user', 'username'))

    subs = []
    problem_cnt = 0
    # should be more than enough pages
    for page_num in range(1000):
        print("Scraping page:", page_num+1)
        # CHANGE: problems to
        submissions_url = profile_url+'?page='+str(page_num)


        try:
            result = submissions(submissions_url, login_reply.cookies)
        except requests.exceptions.RequestException as err:
            print('Submissions connection failed:', err)
            sys.exit(1)

        if result.status_code != 200:
            print('Fetching submissions failed.')
            if result.status_code == 403:
                print('Access denied (403)')
            elif result.status_code == 404:
                print('Incorrect submissions URL (404)')
            else:
                print('Status code:', result.status_code)
            sys.exit(1)

        # CHANGE: skipped the soup, just do it ourselves
        todo = result.text

        page_subs = []
        while True:
            # find a <tr> tag indicating the start of a submission entry
            begin = todo.find("<tr data-submission-id")
            if begin == -1: break
            # eat up everything in the string that came before the location of the tag
            todo = todo[begin:]
            # find the matching closing tag
            end = todo.find("/tr>")
            # add the entire entry for this submission to the problems[] list
            page_subs.append(todo[:end+4])
            todo = todo[end+4:]

        # no submissions on this page, indicates we reached the last page!
        # print number of submissions were scraped
        if not page_subs:
            print('Submissions scraped: ')
            print(len(subs))
            break

        # otherwise, add the submissions from this page to the overall subs
        subs += page_subs

    # NOTE: Indentation level changed.
    # subs is ALL submissions now, not just one page
    for sub in subs:
        # make sure accepted
        if sub.find("Accepted") == -1:
            continue

        begin = sub.find("\"lang\"")
        end = sub[begin:].find("<")
        language = sub[begin+7:begin+end]

        begin = sub.find("/problems/")
        end = sub[begin:].find(">")
        kattis_id = sub[begin+10:begin+end-1]

        path = "/problems/"+kattis_id
        begin = sub.find(path)
        end = sub[begin:].find("<")
        # +2 for the >" part
        problem_name = sub[begin+len(path)+2:begin+end]

        # Instead of printing, you should add them to
        # something you will use to generate the .json file

        # recommendation: solved is a dictionary where the key is the Kattis ID
        # and it stores a pair (problem title, set of languages)
        # for example:
        # if kattis_id not in solved:
        #   solved[kattis_id] = (problem_name, set())
        # solved[kattis_id][1].insert(language) # will insert the language into the set
        #
        # This way, each ID is stored once and each language it is solved in
        # will appear exactly once


        #solved1.add(kattis_id)
        #solved2.add(language)
        print("ID =", kattis_id)
        print("NAME =", problem_name)
        print("LANGUAGE =", language)
        print()

        badges.append({"id": kattis_id, "name": problem_name, "lang": language})


    # data['stats'] = get_stats(cfg, login_reply, problem_cnt)
    # with open('{}.json'.format(filename), 'w') as file_out:
        # json.dump(data, file_out)
    # return problem_cnt

    data['badges'] = badges
    with open('{}.json'.format(filename), 'w') as file_out:
        json.dump(data, file_out)
    return problem_cnt

def check(email):
    return bool(re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email))

def main(args):
    if not check(args.email):
        print('Please enter a valid Kattis account email address.')
        sys.exit(1)

    _EMAIL = args.email
    _HEADERS = {'User-Agent': 'kattis-accepted-fetch by {}'.format(_EMAIL),
            'From':_EMAIL}

    try:
        cfg = get_config()
    except configparser.Error as exc:
        print(exc)
        sys.exit(1)

    try:
        login_reply = login_from_config(cfg)
    except configparser.Error as exc:
        print(exc)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print('Login connection failed:', err)
        sys.exit(1)

    if not login_reply.status_code == 200:
        print('Login failed.')
        if login_reply.status_code == 403:
            print('Incorrect username or password/token (403)')
        elif login_reply.status_code == 404:
            print('Incorrect login URL (404)')
        else:
            print('Status code:', login_reply.status_code)
        sys.exit(1)

    cnt = extract_problems(cfg, login_reply)
    get_stats(cfg, login_reply, cnt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads user\'s Kattis statistics.')
    parser.add_argument(dest='email', metavar='kattis_email', type=str, help='Email address used for Kattis account')
    args = parser.parse_args()
    main(args)
    badgegetter.main()

# update help message
# import webbrowser, os
# webbrowser.open('file://' + os.path.realpath("filename.html"))
