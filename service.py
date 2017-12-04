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
    
    def load_cats(cat_name):
        if cat_name!=[]:
            wiki=WikiAPI('Category:'+cat_name[0])
            wiki.wiki_cats()
            result1=wiki.write_subcats_to_mongo()
            result2=wiki.wiki_pages()
            
        else:
            result1='no category'
            result2=""
        return result1, result2 , wiki
    
    load_page=[]
    if request.method=='POST':
        
        load_page=request.form.getlist('load_page')
        cat_name=request.form.getlist('category_name')
        
        if load_page[0]=='yes':
            result1, result2, wiki =load_cats(cat_name)
            result3=wiki.load_articles()
            result=[result1, result2, result3]
           
        elif load_page[0]=='new':
            result=('enter category to load')
            
        else:
            if cat_name!=[]:
                result1, result2 =load_cats(cat_name)
                #wiki=WikiAPI('Category:'+cat_name[0])
                #wiki.wiki_cats()
                #result1=wiki.write_subcats_to_mongo()
                #result2=wiki.wiki_pages()
                result=[result1, result2]
            else:
                result=('enter category to load')
    else:
        result=('enter category to load')
    
    return render_template("load_category.html", output = result)


@app.route('/search_term',methods=['GET','POST'])

def search_term_interface():
    
    if request.method=='POST':
        
        search_term=request.form(['search-term'])
        result=mySearch.search_myWiki(search_term)
   
    else:
        result=()

    return render_template("search_term.html", output = result)


if __name__ == '__main__':
    app.run(host = "0.0.0.0")
