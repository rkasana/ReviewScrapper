# Import the necessary packages

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

# Initialize the flask app

app = Flask(__name__)  # initializing the flask app with the name app

baseUrl = "https://www.flipkart.com"

@app.route('/', methods=['GET'])  #  route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

# Creating the routes to redirect the control inside the application itself


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")  # obtaining the search string entered in the form
            # Get the comments of each page

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString  # preparing the URL to search the product on flipkart
            uClient = uReq(flipkart_url)  # requesting the webpage from the internet
            flipkartPage = uClient.read()  # reading the webpage
            uClient.close()  # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
            bigboxes = flipkart_html.findAll("div", {
                "class": "bhgxx2 col-12-12"})  # seacrhing for appropriate tag to redirect to the product link
            del bigboxes[0:3]  # the first 3 members of the list do not contain relevant information, hence deleting them.
            box = bigboxes[0]  # taking the first iteration (for demo)
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']  # extracting the actual product link
            prodRes = requests.get(productLink)  # getting the product page from server
            prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML

            all_reviews = prod_html.find_all('div', {'class': "col _39LH-M"})  # finding the HTML section containing the customer comments

            commentsURL = "https://www.flipkart.com" + all_reviews[0].find_all('a')[-1].get('href')

            req_data = requests.get(commentsURL)
            review_soup = bs(req_data.content, 'html.parser')

            next_page = review_soup.find_all('a', {'class': '_2Xp0TH'})

            # links for comments of all pages
            links = []
            for page in next_page:
                link = page.get('href')
                links.append(baseUrl + link)
            print(links)

            ## save the comments in the csv file
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)

            reviews = get_data(searchString,links)
            return render_template('results.html', reviews=reviews)
        except Exception as e:
            print('the Exception message is :', e)
            return 'something is wrong'

    else:
        return render_template('index.html')


def get_data(searchString,links):
    reviews = []  # initializing an empty list for reviews iterating over the comment section to
                  # get the details of the customer and their comments
    for first_page_link in links:
        req_data = requests.get(first_page_link)
        review_soup = bs(req_data.content, 'html.parser')

        commentboxes = review_soup.find_all('div', {'class': "_1PBCrt"})
        for commentbox in commentboxes:
            try:
                name = commentbox.find_all('div', {'class':"row"})[2].p.text
            except:
                name = 'No Name'
            try:
                rating = commentbox.find_all('div',{'class':"row"})[0].div.text
            except:
                rating = 'No Rating'
            try:
                commentHead = commentbox.find_all('div',{'class':"row"})[0].p.text
            except:
                commentHead = 'No Comment Heading'
            try:
                custComment = commentbox.find_all('div',{'class':"row"})[1].div.div.div.text
            except:
                custComment = 'No Customer Comment'

            mydict = {"Product": searchString, "Name": name, "Comment Heading":commentHead,
                      "Rating": rating, "Comment": custComment}

            # x = table.insert_one(mydict) # inserting the dictionary containing the review comments
                                           # to the collection
            reviews.append(mydict)  # appending the comments to the reviews list
    return reviews


# @app.route('/nextPage', methods=['POST', 'GET'])  # route to show the review comments in a web UI
# def nextPage():
#
#     get_data(searchString,links)
# #
# #     first_page_link = links[0]
# #     req_data = requests.get(first_page_link)
# #     review_soup = bs(req_data.content,'html.parser')
# #
# #     all_reviews = review_soup.find_all('div', {'class': 'col _39LH-M'})
# #
# #     reviews = []  # initializing an empty list for reviews iterating
# #                     # over the comment section to get the details
# #                     # of the customer and their comments
# #
# #     for commentbox in commentboxes:
# #
# #         try:
# #             name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
# #         except:
# #             name = 'No Name'
# #
# #         try:
# #             rating = commentbox.div.div.div.div.text
# #         except:
# #             rating = 'No Rating'
# #
# #         try:
# #             commentHead = commentbox.div.div.div.p.text
# #         except:
# #             commentHead = 'No Comment Heading'
# #
# #         try:
# #             comtag = commentbox.div.div.find_all('div', {'class': ''})
# #             custComment = comtag[0].div.text
# #         except:
# #             custComment = 'No Customer Comment'
# #
# #         mydict = {"Product": searchString, "Name": name,
# #                   "Rating": rating, "Comment": custComment}
# #
# #         # x = table.insert_one(mydict) # inserting the dictionary containing the review comments
# #         # to the collection
# #
# #         reviews.append(mydict)  # appending the comments to the reviews list
# #     return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
# #
# #
# #     render_template('results1.html')
# #
# #
# # @app.route('/previousPage',methods=['POST','GET'])
# # def previousPage():
# #     render_template('results.html')
# #

if __name__ == "__main__":
    app.run(host = '127.0.0.1', port = 8001, debug = True) # running the app on local machine 8000
    # app.run(debug=True)






