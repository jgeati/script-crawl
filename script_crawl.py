import time
import os
from os import listdir
from os.path import isfile, join
from selenium import webdriver
import pyautogui
import random
from fuzzywuzzy import fuzz
import json

javascript_parser_2 = "var stack = [];" \
                      " var parsed = [];" \
                      " function MyDOMParser(root) {" \
                      " 	var level = 1;" \
                      "	var id = 1;" \
                      "	var parentid = 1;" \
                      "	if (root.nodeType == 1) {" \
                      "		computed = window.getComputedStyle(root,null);" \
                      "       var computed_css = [];" \
                      "       for (var k = 0; k < computed.length; k++) {" \
                      "           computed_css.push(computed[k] + ':' + computed[computed[k]]);" \
                      "       }" \
                      "		root_elem = {'parentid': parentid, 'id': id, 'level': level, 'node': root, 'computedstyle': computed_css};" \
                      "       elem_to_push = {'parentid': parentid, 'id': id, 'level': level, 'node': root.outerHTML, 'computedstyle': computed_css};" \
                      "		stack.push(root_elem);" \
                      "		parsed.push(elem_to_push);" \
                      "		while(stack.length != 0){" \
                      "			elem = stack.pop();" \
                      "			for (var i = 0; i < elem.node.children.length; i++) {" \
                      "               elem_computed = window.getComputedStyle(elem.node.children[i],null);" \
                      "               var elem_computed_css = [];" \
                      "               for (var m = 0; m < elem_computed.length; m++) {" \
                      "                   elem_computed_css.push(elem_computed[m] + ':' + elem_computed[elem_computed[m]]);" \
                      "               }" \
                      "				s_elem = {'parentid': elem.id, 'id': ++id, 'level': elem.level+1 , 'node': elem.node.children[i], 'computedstyle': elem_computed_css};" \
                      "               s_elem_to_push = {'parentid': elem.id, 'id': id, 'level': elem.level+1 , 'node': elem.node.children[i].outerHTML, 'computedstyle': elem_computed_css};" \
                      "				stack.push(s_elem);" \
                      "				parsed.push(s_elem_to_push);" \
                      "			}" \
                      "		}" \
                      "	}" \
                      "}" \
                      "MyDOMParser(document.children[0]);" \
                      "return parsed;"


class HTMLItem(object):
    def __init__(self, id, level, parent_id, html_obj, computedstyle):
        self.id = id
        self.level = level
        self.parent_id = parent_id
        self.html_obj = html_obj
        self.computedstyle = computedstyle
        self.readermode = False

    def inReader(self):
        self.readermode = True


def extract_features():
    return


def get_reader(firefox_browser, js_parser):
    parsed_elements = []
    parsed_iframes = []
    viewport_area = 0
    pyautogui.press('f9')
    time.sleep(10)
    try:
        viewport_width = float(firefox_browser.execute_script('return window.innerWidth'))
        viewport_height = float(firefox_browser.execute_script('return window.innerHeight'))
        viewport_area = viewport_width * viewport_height

        temp_parsed_elements = firefox_browser.execute_script(js_parser)

        # print(len(temp_parsed_elements))

        for parsed_element in temp_parsed_elements:
            parsed_elements.append(HTMLItem(parsed_element['id'], parsed_element['level'], parsed_element['parentid'],
                                            parsed_element['node'], parsed_element['computedstyle']))

        # IFRAME element extraction code
        iframe_elements = firefox_browser.find_elements_by_tag_name('iframe')

        for iframe in iframe_elements:
            firefox_browser.switch_to.frame(iframe)  # switch_to_frame(iframe)
            temp_parsed_iframe_elements = firefox_browser.execute_script(js_parser)

            for parsed_iframe_element in temp_parsed_iframe_elements:
                parsed_iframes.append(HTMLItem(parsed_iframe_element['id'], parsed_iframe_element['level'],
                                               parsed_iframe_element['parentid'], parsed_iframe_element['node'],
                                               parsed_iframe_element['computedstyle']))

            firefox_browser.switch_to.default_content()  # switch_to_default_content()
    except Exception as e:
        print('Exception while opening reader in selenium ' + str(e))

    return viewport_area, parsed_elements, parsed_iframes


def getLinks(domain, firefox_browser):
    linklist = []
    firefox_browser.get(str(domain[0]))
    if domain[1] == 0:
        links = firefox_browser.find_elements_by_tag_name("a")
        for l in links:
            link = str(l.get_attribute('href'))
            if domain[0] in link:
                linklist.append(link)

        for site in random.sample(linklist, 5):
            browsers.insert(0, (site, 1))
        print(browsers)


def browser_script(domain, firefox_browser, js_parser):
    time.sleep(10)
    parsed_elements = []
    parsed_iframes = []
    viewport_area = 0

    try:
        getLinks(domain, firefox_browser)

        # viewport area
        viewport_width = float(firefox_browser.execute_script('return window.innerWidth'))
        viewport_height = float(firefox_browser.execute_script('return window.innerHeight'))
        viewport_area = viewport_width * viewport_height

        temp_parsed_elements = firefox_browser.execute_script(js_parser)

        # print(len(temp_parsed_elements))

        for parsed_element in temp_parsed_elements:
            parsed_elements.append(HTMLItem(parsed_element['id'], parsed_element['level'], parsed_element['parentid'],
                                            parsed_element['node'], parsed_element['computedstyle']))

        # IFRAME element extraction code
        iframe_elements = firefox_browser.find_elements_by_tag_name('iframe')

        for iframe in iframe_elements:
            firefox_browser.switch_to.frame(iframe)  # switch_to_frame(iframe)
            temp_parsed_iframe_elements = firefox_browser.execute_script(js_parser)

            for parsed_iframe_element in temp_parsed_iframe_elements:
                parsed_iframes.append(HTMLItem(parsed_iframe_element['id'], parsed_iframe_element['level'],
                                               parsed_iframe_element['parentid'], parsed_iframe_element['node'],
                                               parsed_iframe_element['computedstyle']))

            firefox_browser.switch_to.default_content()  # switch_to_default_content()

    except Exception as e:
        print('Exception while opening url in selenium ' + str(e))

    return viewport_area, parsed_elements, parsed_iframes


def check_edit_distance(i, x):
    startx = min(x.find(' '), x.find('>'))
    starti = min(i.find(' '), i.find('>'))
    if x[:startx] == i[:starti] and fuzz.ratio(i, x) > 90:
        return True

    return False


def match_img(i, x):
    startx = x.find('src="')
    endx = x.find('"', startx + 5)
    starti = i.find('src="')
    endi = i.find('"', starti + 5)
    if i[starti:endi] == x[startx:endx]:
        return True

    return False


def remove_links(i, x):
    while x.find('<a href') != -1:
        try:
            startx = x.find('<a href')
            endx = x.find('</a>', startx)
            starti = i.find('<a href')
            endi = i.find('</a>', starti)
            x = x[:startx] + x[endx+4:]
            i = i[:starti] + i[endi+4:]
        except:
            return False
    if i == x:
        return True

    return False


def find_matches(normal, reader):
    matches = []
    count = 0
    for i in normal:
        for x in reader:
            if x.html_obj == i.html_obj:
                matches.append(x.html_obj)
                i.inReader()
                count += 1
                break

            if check_edit_distance(x.html_obj, i.html_obj):
                matches.append(x.html_obj)
                i.inReader()
                count += 1
                break

            if x.html_obj.startswith('<p>') and i.html_obj.startswith(
                    '<p>') and 'href' in x.html_obj and 'href' in i.html_obj:
                if remove_links(i.html_obj, x.html_obj):
                    matches.append(x.html_obj)
                    i.inReader()
                    count += 1
                    break

            if x.html_obj.startswith('<img') and i.html_obj.startswith('<img'):
                if match_img(i.html_obj, x.html_obj):
                    matches.append(x.html_obj)
                    i.inReader()
                    count += 1
                    break

    # for i in matches:
    #     print(i)


def examine_css(normal, reader):
    for elem in reader:
        print(elem.__dict__)
        #print(elem.__dict__['computedstyle'])
        #print(len(elem.__dict__['computedstyle']))


def start_crawl(browsers, js_parser):
    sitecounter = 0
    for site in browsers:
        firefox_profile = webdriver.FirefoxProfile()
        # Set default Firefox preferences
        firefox_profile.set_preference('app.update.enabled', False)
        # Clear cache
        firefox_profile.set_preference("browser.cache.disk.enable", False)
        firefox_profile.set_preference("browser.cache.memory.enable", False)
        firefox_profile.set_preference("browser.cache.offline.enable", False)
        firefox_profile.set_preference("network.http.use-cache", False)

        firefox_browser = webdriver.Firefox(firefox_profile=firefox_profile)
        firefox_browser.set_page_load_timeout(120)  ##change with 120
        firefox_browser.maximize_window()

        normal = browser_script(site, firefox_browser, js_parser)
        reader = get_reader(firefox_browser, js_parser)

        base_len = len(normal[1])
        if base_len - (base_len * .1) <= len(reader[1]) <= base_len + (base_len * 1):
            isReader = False
            print('no!')
        else:
            isReader = True
            print('reader!')

        if isReader:
            find_matches(normal[1], reader[1])

            with open('C:/Users/Owner/crawls/normal' + str(sitecounter) + '.json', 'w') as writefile:
                for line in normal[1]:
                    json.dump(line.__dict__, writefile, indent=2)

            with open('C:/Users/Owner/crawls/reader' + str(sitecounter) + '.json', 'w') as writefile:
                for line in reader[1]:
                    json.dump(line.__dict__, writefile, indent=2)

            sitecounter += 1

        firefox_browser.quit()


browsers = []
with open('./news_websites.txt', 'r') as sitefile:
    for line in sitefile.read().splitlines():
        browsers.append(('https://www.' + line, 0))

start_crawl(browsers, javascript_parser_2)

# encode writing to files with json
