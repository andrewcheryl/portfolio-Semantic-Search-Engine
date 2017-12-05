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

Data to be collected using Wiki Api.

## 1. EDA

### Explore structure of wiki data

Wikipedia data structure...


- Category ( Xp , Xc)
  - Pages 
  - Categories( Xp , Xc)
      - Pages
      - Categories (Xp,Xc)
          .....

where  Xp = no. of pages , Xc = no. of subcategories

* There is no maximium no. of levels.
* Subcategories can belong to multiple categories/subcategories
* Subcategories can exsist in multiple places within one category heirachy
* Each page can be assigned to multiple categories/ subcategories and multiple times within one category heirachy.
 
Implication - large amount of duplication , extremely deep nesting of subcategories possible

Model Requirements:

* Limit depth of search - default 2 levels of nested subcategories but allow this to be changed
* Remove duplication of subcategories before pulling pages
* Avoid duplication of pages 
* Assess no. of pages before triggering load of articles and provide option to abort (this can easily exceed 10,000 pages with load times > an hour)


### Explore page content

Pages have multiple elements. We are interested in article text and which categories pages belong too. To limit information pulled restrict wiki api queries to 'extract' and 'categories'.

Extracts are delivered inside a nested dictionary structure with html formating. 

Cleaning steps:

1. Remove extract from dictionary
2. Use beautifulsoup to parse html
3. Clean data, lemmatize and remove stop words

Data cleaning 

     Remove any hypertext
     Remove residual html 
     Remove formulae  ( between {} ) 
     Remove any characters not in 'latin' alphabet 
     Lemmatize text
     Remove stop words


## 2. Model development

### Mongo DB setup
Jupyter notebook : 00-Make-database

Wiki data will be stored in a Mongo Database on a separate AWS instance.

The database is named myWiki.

Information is held in 3 collections...

*1.* _category___collection_ : this holds all the subcategories that belong to the load category.

*2.*_page___collection_ : this holds all the unique pages that belong to any category that has been loaded. 

For each page the collection record holds
  
  - pageid
  - title
  - extract
  - list of categories that a page belongs to

*3.*_loads___collection_ : holds a record of which categories have been loaded and when ( this currently is updated only when subcategories are loaded, need to add confirmation that related pages where loaded)


### Load process
Jupyter notebooks: 

 - 01- Extract-data-Machine-Learning
 - 01- Extract-data-Business-Software

Model development was done first for machine learning and then extended toed to business software which has much deeper levels of subcatgories.

Final model can be run for any category.

Based on findings from exploration of wiki data structure the load process was split into 3 processes.

For each requested category , lets call it the load category...

1. Pull all subcategories using a recursive function call. Keep cental list of subcats and remove duplication from results of each recursive function pull.
2. Load subcategories to mongo db  - this is to provide a record of what has been loaded  
3. Identiy unique pages for set of subcategories identifed in step 1
4. For unique pages pull extract and category information , clean extract and load to mongodb. Data cleaning identified in EDA applied.
    

Code for final model build wrapped in a Class.

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
2. Build document matrix using TFidf then apply TruncatedSVD with 100 components. Review of top features resulted in tweaking of cleaning process.
3. Build search function 
    - add serach term to document term matrix (DTM) using Tfidf model fitted in step 2
    - re-run Truncated SVD on augmented DTM
    - run cosine similarity to generate top 10 related articles

Issues :

-  size of dataframe causing lots of crashes - in final build data kept in sparse matrix until final step in search process 
-  how to assess effectiveness of search ? used visual inspection only
-  search works well on single words , not so good on sentences or terms with multple words - need to extend model to use ngrams  - this is currently outstanding
-  for final build step 2 reduced to document term matrix generation only

Code for final model build wrapped in a Class.

Class Wiki_search - functions:

Document term matrix  created when class instantiated.
Search_mywiki can then be rerun multiple times
functions: 

    __init__ -> calls build_dtm_matrix -> calls build_corpus -> returns dtm sparse matrix , dtm index and fitted tfidf

     search_myWiki -> returns  top 10 related articles


### Predictive modeling
TO BE COMPLETED

Two options:

1.Predict 'Load' or Header Category (not subcategory)

2.Harder option - predict subcatgories (can only do if create groups of subcatgories)

For option 1 all data will need to be reloaded as originally considered option 2.

## 3. Model Build
Jupyter notebook : 03- Semantic-search-model-build
All code held in wiki_api.py

Initally designed to run in Flask which has been set up with docker file with setup to download all  the python module requirements. 

To run in standard jupyter/scipy docker container  the following packages are required...
    - spacy
    - nltk
    - pymongo
    - beautifulsoup 
plus download spacy.en and nltk all
Options to install have beeb added to top of Juypter notebook

Code for final model build wrapped in a 3 Classes.

1.Class MyWikiDB - creates connection to MongoDb when required.

2.Class WikiAPI - load categories , this is instantiated with the category name, there is a run flag that defaults True. When the run flag is true it will trigger the full end to end process. If the run flag is false the steps can be triggered individually - this was added for debugging and exploration.

3.Class Wiki_Search - search enging , this require two steps... 

 - Document term matrix  created when class instantiated.
 - Search_mywiki can then be re-run multiple times
 
 The document term matrix is created and kept in a sparse matrix, if takes about 5 seconds to train so it was not necessary to store as pickle and load when search engine iniated. This also ensures that the dtm reflects currently loaded pages. 

### Front end web service
Front end is currently in  jupyter notebook - '03- Semantic-search-model-build'

This provides a user interface to the wiki_api.py code file.

A flask front end is in developement but there are some issues with interactivity required during category load process that need to be resolved.

To run flask front end...
From project directory run

        $ docker build --rm -t flask-dsi-plus .
        $ docker run -it -p 5000:5000 -v `pwd`:/src --rm flask-dsi-plus

TO access category load
    http://127.0.0.1:5000/load_category

To acess search function
    http://127.0.0.1:5000/search_term

## 4. Summary

There are some open points that need to be completed and there are a number of loose ends that would need to be cleaned up to make this a deployable model.

Open points:

- Improve search functionaliy for sentences
- Improve data content management
- Build functional frontend
- Build category prediction


