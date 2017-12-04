# Project 4 Semantic Search


## Problem Statement
Engineer a novel wikipedia search engine.

This problem can be broken down into ...
- Data collection
- Data Storage
- Search algorithm development
- Predictive modeling
- User Interface


## Scope of data

All categories , pages and articles belonging to the following  wikipedia categories:

* [Machine Learning](https://en.wikipedia.org/wiki/Category:Machine_learning)
* [Business Software](https://en.wikipedia.org/wiki/Category:Business_software)

The raw page text and its category information should be written to a collection on a Mongo server running on a dedicated AWS instance.

Data collected using Wiki Api

## EDA

### Explore structure of wiki data

Wikipedia data structure...

Category ( Xp , Xc)
    Pages 
    Categories( Xp , Xc)
        Pages
        Categories (Xp,Xc)
          .....

where  Xp = no. of pages , Xc = no. of subcategories

* There is no maximium no. of levels.
* Categories can belong to multiple catgories 
* Subcatgories can exsist in multiple places within a category heirachy
* Each page can be assigned to multiple categories/ subcategories
* implication - large amount of duplication , extremely deep nesting of subcategories

Model Requirments:
* Limit depth of search - default 2 levels of nested subcategories but allow this to be changed
* remove duplication of subcategories before pulling pages
* avoid duplication of pages 
* assess no of pages before triggering load of articles and provide option to abort (this can easily be 10,000 pages with load times > an hour)


### Explore page content

Pages have multiple elements. We are interested in article text and which ccategories pages belong too. To limit information pulled restrict wiki api queries to 'extract' and 'categories'.

Extracts are delivered inside a nested dictionary structure with html formating. 

Cleaning steps:

1. remove extract from dictionary
2. use beautifulsoup to parse html
3. Clean data , lemmatuze and remove stop words

Data cleaning 
    * Remove any hypertext
    * Remove residual html 
    * remove formula.  - between {}
    * Remove any characters not in 'normal' alphabet 
    * Lemmatize text
    * Remove stop words


## Model development

### Mongo Db setup
Jupyter notebook : 00- Make-database

Wiki data is stored in a Mongo Database on a separate AWS instance.

The database is named myWiki
information is held in 3 collections
1. category_collection - this holds all the subcatgories that belong to the load category.
2. page_collection - this holds all the unique pages that belong to any category that has been loaded. 
For each page the collection record holds
    - pageid
    - title
    - extract
    - categories that a page belongs
3. loads_collection - holds a record of whihc categories have been loaded and when ( this currently is update only when subcategories are loaded, need to add confirmation that pages where loaded)


### load process
Jupyter notebooks: 
 - 01- Extract-data-Machine-Learning
 - 01- Extract-data-Business-Software

Model development was first on the machine learning and then extended to business software which has much deeper levels of subcatgories.

Final model can be run for any category.

Based on findings from exploration of wiki data structure the load process was split into 3 processes.
For requested category , lets call it load category
    1. Pull all subcategories using a recursive function call. Keep cental list of subcats and remove duplication from results of each recursive function pull.
    2. Load subcategories to mongo db  - this is to provide a record of what has been loaded  
    3. Identiy unique pages for set of subcategories identifed in step 1
    4. For unique pages pull extract and category information , clean extract and load to mongodb. Data cleaning identified in EDA applied.
    

Class WikiAPI - functions:

    'wiki_cats'  -> calls 'pull_wiki_data' -> calls 'read_categories' -> 
    returns unique list of subcategories & ids,
    writes subcategories to self.subcategories ready to load
    
    'write_subcats_to_mongo' -> writes contents of self.subcats to 
    category collection in mongodb
    
    'wiki_pages' -> calls 'pull_wiki_data' - > calls 'read_pages' -> 
    returns unique no. pages & no. duplicates,
    results written to self.pages ready for 'load_articles'
    
    'load_articles' -> calls 'read_articles' -> calls 'pull_wiki_page' & 'cleaner'


### Search algorithm development
Jupyter notebook : 02- Semantic-search-model-developement

Seaarch process broken down into three steps:
1. Build corpus - during development this was limited to a 1000 pages as running into memory issues using dataframes in order to investiagte results
2. Build document matrix using TFidf then apply TruncatedSVD with 100 components. REview top features produced and tweak cleaning process
3. Build search function 
    - add serach term to document term matrix (DTM) using Tfidf model fitted in step 2
    - rerun Truncated SVD on augmented DTM
    - run cosine similarity to generate top 10 related articles

Issues 
    -  size of dataframe causing lots of crashes - in final build data kept in sparse matrix until final step in search process
    -  how to assess effectiveness of search ? used visual inspection only
    -  search works well on single words , not so good on sentences or terms with multple words - need to extend model to use ngrams  - this is currently outstanding
    -  for final build step 2 reduced to document term matrix generation only

## Predictive modeling
TO BE COMPLETED


## Model Build
Jupyter notebook : 03- Semantic-search-model-build
All code held in wiki_api.py


### Front end web service
Front end is currently in  jupyter notebook - '03- Semantic-search-model-build'
THis provides a user interface to the wiki_api.py cde file.

A flask front end is in developement but there are some issues wit interactivty required during category load process that need to be resolved.

