import json
import time
import webbrowser
import os
import threading
import server


class OpenServer(threading.Thread):
    def run(self):
        server.run()


def main():
    # open the solved problems file
    completed = json.load(open("solved.json"))["badges"]
    completed_problems = [x["id"] for x in completed]
    completed_lang = {}

    # convert languages used to solve into a dict with template {"lang": count used to solve}
    for question in completed:
        if question["lang"] not in completed_lang:
            completed_lang[question["lang"]] = 0
        completed_lang[question["lang"]] += 1

    # read in badges
    out_dict = {"badges": []}
    with open("badges.json") as f:
        badges = json.load(f)

    for group in badges["badges"]:
        next_group = {"group-name": group["group-name"], "badges": []}
        for badge in group["badges"]:
            badge_type = badge["type"]
            name = badge["name"]
            ids = badge["ids"]
            lang_req = badge["langs"]
            siz = len(ids)
            finished = []
            left_langs = {}
            lang_count = 0
            lang_completed = 0
            percent_done = 0
            completed_badge = False
            # check if badge requires certain amount of problems to be solved in certain language
            if badge_type == "langs":
                works = True
                finished = {}
                for key in lang_req:
                    lang_count += lang_req[key]
                    if key not in completed_lang: # check if lang has been used to solve problem
                        left_langs[key] = lang_req[key]
                        works = False
                    elif completed_lang[key] < lang_req[key]: # check if not enough solves with a lang
                        lang_completed += completed_lang[key]
                        left_langs[key] = lang_req[key] - completed_lang[key]
                        finished[key] = completed_lang[key]
                        works = False
                completed_badge = works
                percent_done = [lang_completed, lang_count]
            elif badge_type == "problems":
                for i in reversed(range(siz)):
                    if ids[i][0] in completed_problems: # check if problem has been solved
                        finished.append(ids[i])
                        completed_problems.remove(ids[i][0])
                        del ids[i]
                percent_done = [len(finished), siz]
                completed_badge = len(ids) == 0
            next_group["badges"].append({"type": badge_type, "name": name, "desc": badge["desc"], "icon": badge["icon"], "progress": percent_done, "left": ids,
                                       "completed_problems": finished, "finished": completed_badge, "left_langs": left_langs, "links": badge["links"]})
        out_dict["badges"].append(next_group)
    # write badge progress to file
    with open("badgesprogress.json", "w") as f:
        json.dump(out_dict, f)

    # open local server to host progress file so it can be opened by site
    open_server = OpenServer()
    open_server.start()

    # open html file
    filename = 'file:///' + os.path.dirname(os.path.dirname(__file__)) + "/kattis-badge-site/public/index.html"
    time.sleep(2)
    webbrowser.open_new_tab(filename)


if __name__ == "__main__":
    main()
