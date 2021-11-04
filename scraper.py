import re
import urllib
import operator
from bs4 import BeautifulSoup
from urllib.parse import urldefrag, urlparse


crawled_alrdy = set()
longest_page = {}
longest_pagenum = 0


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    hyperlink_list = list()
    words_list = []
    parsed_url = urlparse(url)

    # writing urls into .txt files
    with open("url.txt", "a", encoding="utf-8") as file1, open("longest.txt", "a", encoding="utf-8") as file2, \
            open("content.txt", "a", encoding="utf-8") as file3:

        # checks for valid url and response status
        if is_valid(url):
            if 199 < resp.status < 203:
                if check_crawled(url):
                    html_document = resp.raw_response.content
                    soup_obj = BeautifulSoup(html_document, 'html.parser')
                    file1.write(url + "\n")
                    split_soup = soup_obj.text.split()

                    for word in split_soup:
                        if word.isalnum():
                            if "[]" not in word:
                                if word != "":
                                    words_list.append(word)

                    longest_page[url] = len(words_list)
                    file3.write(url + "\n" + str(words_list) + "\n")
                    file2.write(url + "\n" + str(longest_page[url]) + "\n")

                    for path in soup_obj.find_all('a'):
                        relative = path.get('href')
                        link = urllib.parse.urljoin("https://" + parsed_url.netloc, relative)
                        frag_tuple = urldefrag(link)[0]
                        hyperlink_list.append(frag_tuple)
                        file1.write(frag_tuple + "\n")

    file2.close()
    file3.close()
    file1.close()
    return hyperlink_list
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    #return list()


def check_crawled(url):
    if url[-1] == "/":
        url = url[:-1]
    if url not in crawled_alrdy:
        crawled_alrdy.add(url)
        return True
    return False


def match_domain(url):
    net_loc = url.netloc
    valid_urls = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]

    if net_loc.startswith("www."):
        net_loc = net_loc.strip("www.")

    net_list = net_loc.split(".")
    subdomain = ".".join(net_list)

    if len(net_list) > 3:
        subdomain = ".".join(net_list[1:])

    if net_loc == "today.uci.edu":
        if "/department/information_computer_sciences" in url.path:
            return True

    if net_loc == "hack.ics.uci.edu":
        if "gallery" in url.path:
            return False

    if net_loc == "wics.ics.uci.edu":
        if "/events" in url.path:
            return False

    if net_loc == "grape.ics.uci.edu":
        return False

    if net_loc == "intranet.ics.uci.edu":
        return False

    if net_loc == "archive.ics.uci.edu":
        return False

    for domain in valid_urls:
        if subdomain == domain:
            return True


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False

        if not match_domain(parsed):
            return False

        avoid_crawling = ["txt", "rkt", "svg", "json", "ss", "scm", "py",
                          "wp-content", "calendar", "ical", "img", "pdf", "war",
                          "css", "js", "bmp", "gif", "jpeg", "ico", "png", "tiff",
                          "mid", "mp2", "mp3", "mp4", "wav", "avi", "mov", "mpeg", "ram",
                          "m4v", "mkv", "ogg", "ogv", "pdf", "ps", "eps", "tex", "ppt",
                          "pptx", "doc", "docx", "xls", "xlsx", "names", "data", "dat",
                          "exe", "bz2", "tar", "msi", "bin", "7z", "psd", "dmg", "iso",
                          "epub", "dll", "cnf", "tgz", "sha1", "thmx", "mso", "arff",
                          "rtf", "jar", "csv", "rm", "smil", "wmv", "swf", "wma", "zip",
                          "rar", "gz"]

        for ext in avoid_crawling:
            if ext in parsed.path or (ext) in parsed.query:
                return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise
