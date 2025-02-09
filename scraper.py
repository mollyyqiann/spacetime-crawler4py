import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def filter_fragment(url):
    idx = url.find('#')
    if idx == -1:
        return url
    return url[: idx]


def scraper(url, resp):
    links = extract_next_links(url, resp)
    linkFiles = open("links.txt", "a")
    link_with_size = open("links_size.txt", "a")
    linkWithOutFragments = open("link_without_fragment.txt", "a")
    allContents = open("contents.txt", "a")
    if resp.raw_response is None:
        return []
    content = resp.raw_response.content
    fileContent = BeautifulSoup(content, "html.parser").get_text()
    fileContent = fileContent.replace("\n", " ")
    allContents.write(fileContent + "\n")
    size = len(fileContent.split())
    link_with_size.write("{} {}\n".format(url, size))
    for link in links:
        if is_valid(link):
            linkFiles.write(str(link) + "\n")
            linkWithOutFragments.write(str(filter_fragment(link)) + "\n")

    linkFiles.close()
    link_with_size.close()
    linkWithOutFragments.close()
    allContents.close()
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    hyperlinks = []
    if resp.status != 200:
        return []
    else:
        content = resp.raw_response.content
        allLinks = BeautifulSoup(content, "lxml").findAll('a')
        for lk in allLinks:
            u = lk.get('href')
            if u is not None:
                lk = lk.get('href').strip()
            else:
                continue
            if lk.startswith("http") or lk.startswith("https"):
                hyperlinks.append(lk)
        return hyperlinks


def checkValidUrls(hostName):
    validUrls = ['\\.ics\\.uci\\.edu/', '\\.cs\\.uci\\.edu', '\\.informatics\\.uci\\.edu/', '\\.stat\\.uci\\.edu/']
    for url in validUrls:
        if re.match('.*' + url, hostName):
            return True
    return False


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.hostname is None:
            return False
        return checkValidUrls(parsed.hostname) and (not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()))

    except TypeError:
        print("TypeError for ", parsed)
        raise
