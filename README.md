# Portfolio project : Novel Semantic Search Engine for Wikipedia Articles

## Problem Statement
1. Extract Wikipedia articles from a named Category.
2. Engineer a novel wikipedia search engine.

This problem can be broken down into ...

- Data collection
- Data Storage
- Search algorithm development
- User Interface

## Scope of data for search engine

All sub-categories , pages and articles belonging to the following wikipedia categories...

* [Machine Learning](https://en.wikipedia.org/wiki/Category:Machine_learning)
* [Business Software](https://en.wikipedia.org/wiki/Category:Business_software)

The raw page text and its category information will be written to a collection on a Mongo DB server running on a dedicated AWS instance. 

A Mongo DB was chosen because it holds information in a JSON like format that is easy to work with using a python dictionary.  

Code should be able to pick up any addtional categories if requested.

The Wiki API will be used to extract wikipedia content.

## Project structure 

1. EDA
2. Database set up
3. Model Development
    - extraction process
    - search engine
4. Test search engine performance
5. Model Build

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
Jupyter notebook : 01-Make-database.ipynb

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

A small test category was used for the model development process. The full 5800 from the two specified categories was only loaded once model was working correctly.

Based on findings from the exploration of the wiki data structure the category load process was split into 4 parts ...

1. Pull all subcategories using a recursive function call. A list of all subcategories was kept and a check for any duplication performed before any further action.
2. Write a record of loaded subcategories to the mongo db.
3. Identiy unique pages for unique set of subcategories identifed in step 1
4. For each unique pages pull extract and category information , clean extract and load to mongodb. 


Establishing the data cleaning criteria was an interative process. The the intial step the cleaned extract was reviewed and the criteria tweake , then as a second step  the document term matrix created for the search engine was  reviewed and further tweaks added.
    

The code for final model was wrapped in a the following class.

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

The development of the search process was broken down into four steps:

1. Build corpus - during development this was limited to a test set of 255 pages so that dtm could be loaded into a dataframe for inspection. 

2. Build document matrix using Tfidf then apply TruncatedSVD with 200 components. Review of top features resulted in tweaking of cleaning process.
In early tests the size of the dtm dataframe caused lots of crashes so the development process was restricted to a smaller test set. In the final model data is kept in a sparse matrix until the final step to present search results. 

3. Build search function 
    - add search term to document term matrix (DTM) using Tfidf model fitted in step 2. 
    - re-run Truncated SVD on augmented DTM
    - run cosine similarity to generate top 10 related aticles
    

The code for final model build wrapped in a Class.

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

All required packages can be installed by running the '00-Installed-Packages.ipynb' notebook.

## 4. Test search engine effectiveness
Evaluating search engine results is challening, with limited resouces I choose to use a well known and trusted search engine to provide bench mark results.
I measured my search engine against the results found using google, with the search restricited to the en.wikipedia site.

Google search can be restricted to a particular site using ...
 -  ' site:en.wikipedia.org SEARCHTERM '
 
Comparing the top 10 results (where available from google) I tested..
1. overall effectiveness of search engine 
2. 3 different sets of hyperparatmeters for creating the document term matrix using the Tfidf algorithm. 

On average my search engine found 3 of the top 5 results from google. This was a good performance given the google search was over the entire en.wikipedia content. Many of the items not picked up where not included in the MongoDB content.

The full results are in provided in the excel workbook  search-engine-tests.xlsx


## 5. Model Build
- Jupyter notebook : 05-Model-Build-Extraction-and-Semantic-search.ipynb
- Python code  : wiki_api.py

The code was designed so that it could be held in a single python file to enable deployment using a 'Flask micro web framework'. However , the category extraction process can result in a large number of pages being pulled and can take hours to complete. In order to provide feedback duing the extraction process, and an option to abort the load process, the front end was built in a jupyter notebook instead.  

The code for the final model is wrapped into 3 Classes...

1.Class MyWikiDB - creates connection to MongoDb when required.

2.Class WikiAPI - load categories , this is instantiated with the category name, there is a run flag that defaults True. When the run flag is true it will trigger the full end to end process. If the run flag is false the steps can be triggered individually - this was added for debugging and exploration.

3.Class Wiki_Search - search enging , this require two steps... 

 - Document term matrix  created when class instantiated.
 - Search_mywiki can then be re-run multiple times
 
 The document term matrix is created and kept in a sparse matrix, if takes about 45 seconds to train when populated with the full 5800 pages but only needs to be trained once per 'search' session. 







