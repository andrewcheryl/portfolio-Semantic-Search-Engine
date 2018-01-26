# Portfolio project : Novel Semantic Search Engine for Wikipedia Articles

## Problem Statement
Extract Wikipedia articles from a named Category.
Engineer a novel wikipedia search engine.

This problem can be broken down into ...

- Data collection
- Data Storage
- Search algorithm development
- User Interface

## Scope of data for search engine

All sub-categories , pages and articles belonging to the following wikipedia categories:

* [Machine Learning](https://en.wikipedia.org/wiki/Category:Machine_learning)
* [Business Software](https://en.wikipedia.org/wiki/Category:Business_software)

The raw page text and its category information should be written to a collection on a Mongo server running on a dedicated AWS instance.

Code should be able to pick up any addtional categories if requested.

Data to be collected using the Wiki Api.

## Project structure 

1. EDA
2. Database set up
3. Model Development
    - extraction process
    - search engine
4. Model Build

### Repository structure
Folders
- ipybn - Jupyter notebooks
- lib - python files

Project information files
- search_engine_tests.xlsx
- README.md

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
     Remove single characters 
     Lemmatize text
     Remove stop words


## 2. Database setup

Wiki data will be stored in a Mongo Database on a separate AWS instance.

### Prepare AWS server
1. Create EC2 t2.micro instance required with Ubuntu 16.04 image
2. Set up security group and open ports ...
 - 22  - to accept SSH traffic
 - 2376 - to accept inbound traffic from anywhere , used to pull images from Docker Hub
 - 27016  - to accept inbound traffic from amywhere, used to connect with MongoDB
 
3. Install Docker app
4. Pull Mongo docker image from Docker Hub 
5. Create a new data volume for the Mongo database store
6. Run docker image to create a docker container

### Mongo DB setup
Jupyter notebook : 01-Make-database

The database is named myWiki.

Information is held in 3 collections...

*1.* _category___collection_ : this holds all the subcategories that belong to the load category.

*2.*_pagetest___collection_ : this will hold a small test set of pages that can be used in development process to test extraction and cleaning process. 

*3.*_page___collection_ : this holds all the unique pages that belong to any category that has been loaded. 

For each page the collection record holds
  
  - pageid
  - title
  - extract
  - list of categories that a page belongs to

*4.*_loads___collection_ : holds a record of which categories have been loaded and when ( this currently is updated only when subcategories are loaded, need to add confirmation that related pages where loaded)

*5.*_pageload___collection_ : holds a record of which categories have been loaded and when ( this currently is updated only when subcategories are loaded, need to add confirmation that related pages where loaded)

Some addtional items where added to the end of this jupyter notebook to enable management of database content.


## 3. Model Development

### Load process
Jupyter notebooks: 

 - 02-Develop-and-test-data-cleaning.ipynb
 - 03-Develop-extraction-process.ipynb

Model development was done for a one small category first with 255 pages.

Final model can be run for any category.

Based on findings from exploration of wiki data structure the load process was split into 3 processes.

For each requested category , lets call it the load category...

1. Pull all subcategories using a recursive function call. Keep cental list of subcats and remove duplication from results of each recursive function pull.
2. Load subcategories to mongo db  - this is to provide a record of what has been loaded  
3. Identiy unique pages for set of subcategories identifed in step 1
4. For unique pages pull extract and category information , clean extract and load to mongodb. Data cleaning process tested and final version chosen for model build.
    

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
Jupyter notebook : 04-Develop-Semantic-search-process.ipynb

Seaarch process broken down into three steps:

1. Build corpus - during development this was limited to a test set of 255 pages so that dtm could be loaded into a dataframe for inspection.

Issues encounted:
-  size of dtm dataframe causing lots of crashes - in final build data kept in sparse matrix until final step to present search results. 

2. Build document matrix using Tfidf then apply TruncatedSVD with 200 components. Review of top features resulted in tweaking of cleaning process.

3. Build search function 
    - add search term to document term matrix (DTM) using Tfidf model fitted in step 2. 
    - re-run Truncated SVD on augmented DTM
    - run cosine similarity to generate top 10 related aticles
    
4. Test search engine effectiveness



Code for final model build wrapped in a Class.

Class Wiki_search - functions:

Document term matrix  created when class instantiated.
Search_mywiki can then be rerun multiple times
functions: 

    __init__ -> calls build_dtm_matrix -> calls build_corpus -> returns dtm sparse matrix , dtm index and fitted tfidf

     search_myWiki -> returns  top 10 related articles

### Python package requirements
To run in a standard jupyter/scipy docker container  the following packages are required...
    - spacy
    - nltk
    - pymongo
    - beautifulsoup 
plus download spacy.en and nltk all

All required packages can be installed by running 00-Installed-Packages.ipynb 


## 4. Model Build
Jupyter notebook : 05-Model-Build-Extraction-and-Semantic-search.ipynb
Python code  : wiki_api.py

The code was designed so that it could be held in a single python file to enable deployment using a 'Flask micro web framework'. However , the category extraction process can result in a large number of pages being pulled and can take hours to complete. In order to provide feedback duing the extraction process, and an option to abort the load process, the front end was built in a jupyter notebook instead.  

Code for final model build wrapped in a 3 Classes.

1.Class MyWikiDB - creates connection to MongoDb when required.

2.Class WikiAPI - load categories , this is instantiated with the category name, there is a run flag that defaults True. When the run flag is true it will trigger the full end to end process. If the run flag is false the steps can be triggered individually - this was added for debugging and exploration.

3.Class Wiki_Search - search enging , this require two steps... 

 - Document term matrix  created when class instantiated.
 - Search_mywiki can then be re-run multiple times
 
 The document term matrix is created and kept in a sparse matrix, if takes about 5 seconds to train so it was not necessary to store as pickle and load when search engine iniated. This also ensures that the dtm reflects currently loaded pages. 







