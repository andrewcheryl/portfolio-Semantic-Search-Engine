from flask import Flask, jsonify, request
from flask import render_template
from lib.wiki_api import MyWikiDB, WikiAPI , WikiSearch


#flask content - 3 pages
# 1. Load new Category
# 2. Search term
# 3. Category prediction - to come


#Instantiate WikiSearch
mySearch=WikiSearch()
print('dtm created')

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World! What do you know ---my first web page'

@app.route('/load_category',methods=['GET','POST'])
def wiki_cat_interface():
    
    if request.method=='POST':
        
        cat_name=request.form.getlist('category_name')
        WikiAPI('Category:'+cat_name[0])
    
    else:
        result=('enter category to load')
    
    return render_template("load_category.html", output = result)


@app.route('/search_term',methods=['GET','POST'])

def search_term_interface():
    
    if request.method=='POST':
        
        search_term=request.form.getlist('search-term')
        result=mySearch.search_myWiki(search_term)
   
    else:
        result=()

    return render_template("search_term.html", output = result)


if __name__ == '__main__':
    app.run(host = "0.0.0.0")
