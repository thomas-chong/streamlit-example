import requests,lxml,json,re
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from streamlit_tags import st_tags
from io import StringIO
import time


def newScraper(listOfTopics):
    st.subheader('Progress:')
    my_bar = st.progress(0)
    resultDict = {}
    progress = 0

    # configurations
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
    }
    baseURL = 'https://www.scmp.com'

    data = []
    
    for topic in listOfTopics:
        print(topic)
        scrapeURL = f'https://www.scmp.com/topics/{topic}'
        html = requests.get(scrapeURL,headers=headers)
        status_code = html.status_code
        print(status_code)
        if status_code == 200:
            response = html.text
            soup = BeautifulSoup(response, 'lxml')

            print('-----------------------------------')
            articleArea = soup.find('div',class_='article-area')
            allArticles = articleArea.findAll('div',class_='article-level')
            # print(allArticles)
            for article in allArticles:
                # get title 
                title = article.find('div',class_='article__title')
                print(f"Title: {title.text}")

                # get article link 
                a = title.find('a')

                articleURL = baseURL + a['href']
                print(f"Link: {articleURL}")
                print()
                try: 
                    html1 = requests.get(articleURL,headers=headers)
                    response1 = html1.text
                    soup1 = BeautifulSoup(response1, 'lxml')
                    
                    metadata = json.loads("".join(soup1.find("script", text=                                re.compile("articleBody")).contents))

                    # print(json.dumps(metadata, indent=4, sort_keys=True))
                    articleBody = metadata['articleBody']
                    headline = metadata['headline']
                    alternativeHeadline = metadata['alternativeHeadline']
                    dateCreated = metadata['dateCreated']
                    dateModified = metadata['dateModified']
                    datePublished = metadata['datePublished']
                    author = metadata['author']['name']
                    articleURL = metadata['mainEntityOfPage']
                    imageURL = metadata['image']['url']
                    articleSection = metadata['articleSection']

                    subHeadlines = soup1.find('div',class_ = 'info__subHeadline')
                    summaryPoints = subHeadlines.findAll('li',
                    class_='generic-article__summary--li content--li')
                    summary = []
                    for summarypoint in summaryPoints:
                        print(f'- {summarypoint.text}')
                        summary.append(summarypoint.text)

                    # print(f'Published At: {publishedAt.text}')
                except:
                    summary = ''

                data.append([headline,alternativeHeadline,summary,author,articleBody,datePublished,dateCreated,dateModified,articleURL,imageURL,articleSection])
                print('---------------------------------------------')
                # print(len(allArticles))
        progress += (1/(len(listOfTopics)))
        my_bar.progress(progress)

    df = pd.DataFrame(data, columns=['SCMP news headline','alternativeHeadline','Summary Points','Author','Content','Date Published','Date Created','Date Modified','Article Link','Image Link','Section'])
    print(df)
    df.to_csv('SCMPNewsScrapeResults.csv',index=False)


    st.success('SCMP News Scraping completed successfully.')
    return df

# title
st.title(":male-detective: Financial News Summarization")

listOfTopics = ['hong-kong-stock-exchange','hong-kong-economy','china-stock-market','stocks','commodities','regulation','currencies','bonds','stocks-blog','central-banks']

col1 = st.columns(1)

containsUpload = False
with col1:
    st.subheader('Generate SCMP news scraping manually')
    chosen_topics = st_tags(
                label='Add Topics here!',
                text='Press enter to add more',
                value=listOfTopics,
                suggestions=['hong-kong-stock-exchange','hong-kong-economy','china-stock-market','stocks','commodities','regulation','currencies','bonds','stocks-blog','central-banks'],
                key="aljnf"
            )

    st.caption('Current List of Keywords')
    st.write((chosen_topics))

submitted = st.button("Submit")
    
if submitted:
    if containsUpload:
        st.write('Use Existing Datasets.')
    else:
        st.write('SCMP News Scraping for the following topics: ',str(chosen_topics))
        df = newScraper(chosen_topics)   
        st.download_button(
            label="Download data as CSV",
            data=df,
            file_name='large_df.csv',
            mime='text/csv',
        )