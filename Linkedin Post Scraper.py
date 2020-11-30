#!/usr/bin/env python
# coding: utf-8

# In[9]:


#required installs (i.e. pip3 install in terminal): pandas, selenium, bs4, and possibly chromedriver(it may come with selenium)
#Download Chromedriver from: https://chromedriver.chromium.org/downloads
#To see what version to install: Go to chrome --> on top right click three dot icon --> help --> about Google Chrome
#Move the chrome driver to (/usr/local/bin) -- open finder -> Command+Shift+G -> search /usr/local/bin -> move from downloads

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import pandas as pd



#accessing Chromedriver
browser = webdriver.Chrome('chromedriver')


#Replace with you username and password
username = "username"
password = "password"

#Open login page
browser.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

#Enter login info:
elementID = browser.find_element_by_id('username')
elementID.send_keys(username)

elementID = browser.find_element_by_id('password')
elementID.send_keys(password)
elementID.submit()


#Go to company webpage
browser.get('https://www.linkedin.com/company/rei/')


#Simulate scrolling to capture all posts
SCROLL_PAUSE_TIME = 1.5

# Get scroll height
last_height = browser.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


    
#Check out page source code
company_page = browser.page_source   



# #Import exception check for message popups (not needed atm)
# from selenium.common.exceptions import NoSuchElementException
# try:
#     if browser.find_element_by_class_name('msg-overlay-list-bubble--is-minimized') is not None:
#         pass
# except NoSuchElementException:
#     try:
#         if browser.find_element_by_class_name('msg-overlay-bubble-header') is not None:
#             browser.find_element_by_class_name('msg-overlay-bubble-header').click()
#     except NoSuchElementException:
#         pass


#Use Beautiful Soup to get access tags
linkedin_soup = bs(company_page.encode("utf-8"), "html")
linkedin_soup.prettify()

#Find the post blocks
containers = linkedin_soup.findAll("div",{"class":"occludable-update ember-view"})
container = containers[0].find("div","feed-shared-update-v2__description-wrapper ember-view")


# Lists that we will iterate to
post_dates = []
post_texts = []
post_likes = []
post_comments = []
video_views = []
media_links = []
media_type = []


#Looping through the posts and appending them to the lists
for container in containers:
    
    try:
        posted_date = container.find("span",{"class":"visually-hidden"})
        text_box = container.find("div",{"class":"feed-shared-update-v2__description-wrapper ember-view"})
        text = text_box.find("span",{"dir":"ltr"})
        new_likes = container.findAll("li", {"class":"social-details-social-counts__reactions social-details-social-counts__item"})
        new_comments = container.findAll("li", {"class": "social-details-social-counts__comments social-details-social-counts__item"})

        #Appending date and text to lists
        post_dates.append(posted_date.text.strip())
        post_texts.append(text_box.text.strip())


        #Determining media type and collecting video views if applicable
        try:
            video_box = container.findAll("div",{"class": "feed-shared-update-v2__content feed-shared-linkedin-video ember-view"})
            video_link = video_box[0].find("video", {"class":"vjs-tech"})
            media_links.append(video_link['src'])
            media_type.append("Video")
        except:
            try:
                image_box = container.findAll("div",{"class": "feed-shared-image__container"})
                image_link = image_box[0].find("img", {"class":"ivm-view-attr__img--centered feed-shared-image__image feed-shared-image__image--constrained lazy-image ember-view"})
                media_links.append(image_link['src'])
                media_type.append("Image")
            except:
                try:
                    image_box = container.findAll("div",{"class": "feed-shared-image__container"})
                    image_link = image_box[0].find("img", {"class":"ivm-view-attr__img--centered feed-shared-image__image lazy-image ember-view"})
                    media_links.append(image_link['src'])
                    media_type.append("Image")
                except:
                    try:
                        article_box = container.findAll("div",{"class": "feed-shared-article__description-container"})
                        article_link = article_box[0].find('a', href=True)
                        media_links.append(article_link['href'])
                        media_type.append("Article")
                    except:
                        try:
                            video_box = container.findAll("div",{"class": "feed-shared-external-video__meta"})          
                            video_link = video_box[0].find('a', href=True)
                            media_links.append(video_link['href'])
                            media_type.append("Youtube Video")   
                        except:
                            try:
                                poll_box = container.findAll("div",{"class": "feed-shared-update-v2__content overflow-hidden feed-shared-poll ember-view"})
                                media_links.append("None")
                                media_type.append("Other: Poll, Shared Post, etc")
                            except:
                                media_links.append("None")
                                media_type.append("Unknown")



        #Getting Video Views. (The folling three lines prevents class name overlap)
        view_container2 = set(container.findAll("li", {'class':["social-details-social-counts__item"]}))
        view_container1 = set(container.findAll("li", {'class':["social-details-social-counts__reactions","social-details-social-counts__comments social-details-social-counts__item"]}))
        result = view_container2 - view_container1

        view_container = []
        for i in result:
            view_container += i

        try:
            video_views.append(view_container[1].text.strip().replace(' Views',''))

        except:
            video_views.append('N/A')

        
        #Appending likes and comments if they exist
        try:
            post_likes.append(new_likes[0].text.strip())
        except:
            post_likes.append(0)
            pass

        try:
            post_comments.append(new_comments[0].text.strip())                           
        except:                                                           
            post_comments.append(0)
            pass
    
    except:
        pass

    
# #Cleaning the dates
# cleaned_dates = []
# for i in post_dates:
#     d = str(i[0:3]).replace('\n\n', '').replace('•','').replace(' ', '')
#     cleaned_dates += [d]


#Stripping non-numeric values
comment_count = []
for i in post_comments:
    s = str(i).replace('Comment','').replace('s','').replace(' ','')
    comment_count += [s]


    
#Constructing Pandas Dataframe
data = {
    "Date Posted": post_dates,
    "Media Type": media_type,
    "Post Text": post_texts,
    "Post Likes": post_likes,
    "Post Comments": comment_count,
    "Video Views": video_views,
    "Media Links": media_links
}

df = pd.DataFrame(data)


#Exporting csv to program folder
df.to_csv("linkedin_page_posts.csv", encoding='utf-8', index=False)

#Export to Excel
writer = pd.ExcelWriter("linkedin_page_posts.xlsx", engine='xlsxwriter')
df.to_excel(writer, index =False)
writer.save()






