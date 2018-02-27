# Portfolio project: Novel Semantic Search Engine for Wikipedia Articles

## The Problem Statement
Today there is a vast amount of digital information available and search engines are an essential tool for navigating the information space. In particular, finding 'relevant' or 'related' information with regards to a specific topic can be extremely challenging.  

To improve search accuracy a 'Semantic' search engine seeks to understand the searcher's intent and the contextual meaning of terms as they appear in the searchable dataspace. These types of search engines aim to consider various points including context of search, location, intent, variation of words, synonyms, generalized and specialized queries, concept matching and natural language queries to provide relevant search results.  

For this project I will focus on developing a natural language query tool to find related articles on Wikipedia. 


## Goal

1. Extract Wikipedia articles for a named Category.
2. Engineer a novel Wikipedia search engine.

This problem was broken down into the following elements...

- Data collection process
- Data Storage
- Search algorithm development
- User Interface


## Highlevel approach

### Data Collection and Storage
The data collection process will be designed to capture all articles included within a specified category.

The Wiki API will be used to extract all pages contained within the category and any of its subcategories. The article for each page will then be extracted, cleaned and loaded into an NoSQL database that can be queried using the search engine.


### Search Algorithm
Latent semantic analysis (LSA) will be used to develop the search algorithm. This is a natural language processing technique for analyzing relationships between a set of documents and the terms they contain. LSA assumes that words that are close in meaning will occur in similar pieces of text (a distributional hypothesis). 

3 key steps to creating the search engine:

1. Construct an occurrence matrix from the corpus of documents (referred to as a document term matrix or dtm) containing word counts per document. The matrix uses rows represent to unique words and columns to represent each document. It is constructed as a sparse matrix. The elements of the matrix are weighted, using Tf-idf, to reflect the importance of the words in the corpus. 

Tf-idf stands for term frequency-inverse document frequency. It is is a statistical measure used to evaluate how important a word is to a document in a collection or corpus. The weight of a term that occurs in a document is simply proportional to the term frequency.

2. Apply LSA - The document term matrix has very high dimensionality, so a mathematical technique called singular value decomposition (SVD) is used to reduce the number of rows while preserving the similarity structure among columns. Specifically, we will use scikit learns TruncatedSVD algorithm that only computes the 'k' largest singular values. The resulting LSA matrix will use rows to represent the documents and columns to represent the 'components' of the lower dimensional space.

3. The similarity between two documents in the LSA matrix is measured by taking the cosine of the angle between the two vectors (or the dot product between the normalizations of the two vectors) formed by the two rows for the specified documents. Values close to 1 represent very similar components while values close to 0 represent very dissimilar components.

Note:  To analyze a search term it must be included in this LSA matrix. This requires that each search term is appended to the document term matrix and the LSA matrix recalculated.



## Project scope and structure 

1. EDA
2. Database set up
3. Model Development
    - extraction process
    - search engine
4. Test search engine performance
5. Model Build

## 1. EDA

### Scope of data to be included in search engine

All sub-categories, pages and articles belonging to the following Wikipedia categories:

* [Machine Learning](https://en.wikipedia.org/wiki/Category:Machine_learning)
* [Business Software](https://en.wikipedia.org/wiki/Category:Business_software)

The raw page text and its category information will be written to a collection on a Mongo DB server running on a dedicated AWS instance. 

A Mongo DB was chosen because it holds information in a JSON like format that is easy to work with using a python dictionary.  

Code should be able to pick up any additional categories if requested.

The Wiki API will be used to extract Wikipedia content.

### Explore structure of wiki data

The Wikipedia data structure ...

```
 Category (Xp , Xc)
   Pages 
   Categories (Xp , Xc)
       Pages
       Categories (Xp,Xc)
          .....
```

where Xp = no. of pages , Xc = no. of subcategories

Observations:

* There is no maximum no. of levels.
* Subcategories can belong to multiple categories/subcategories.
* Subcategories can exist in multiple places within one category hierarchy.
* Each page can be assigned to multiple categories/ subcategories and multiple times within one category hierarchy.
 
Implication: There is a large amount of duplication, extremely deep nesting of subcategories is possible.

Model Requirements:

* Limit depth of search - default 2 levels of nested subcategories but allow this to be changed
* Remove duplication of subcategories before pulling pages
* Avoid duplication of pages 
* Assess no. of pages before triggering load of articles and provide option to abort (this can easily exceed 10,000 pages with load times > an hour)


### Explore page content

Pages have multiple elements. We are interested in article text and which categories pages belong too. To limit information pulled restrict wiki api queries to 'extract' and 'categories'.

Extracts are delivered inside a nested dictionary structure with html formatting. 

Cleaning steps:

1. Remove extract from dictionary
2. Use python 'beautifulsoup' package to parse html
3. Clean data - remove residual html, formulae, digits and non 'Latin' characters 
4. Reduce dimensionality - lemmatize and remove stop words

## 2. Database setup

The Wiki data will be stored in a Mongo Database on a separate AWS instance.

### Prepare AWS server
1. Create EC2 t2.micro instance required with Ubuntu 16.04 image
2. Set up security group and open ports ...
 - 22  - to accept SSH traffic
 - 2376 - to accept inbound traffic from anywhere, used to pull images from Docker Hub
 - 27016  - to accept inbound traffic from anywhere, used to connect with MongoDB
 
3. Install Docker app
4. Pull Mongo docker image from Docker Hub 
5. Create a new data volume for the Mongo database store
6. Run docker image to create a docker container

### Mongo DB setup
Jupyter notebook: 01-Make-database.ipynb

The database is named myWiki.

Information is held in 5 collections...

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

Some additional items were added to the end of this jupyter notebook to enable the management of database content.


## 3. Model Development

### Load process
Jupyter notebooks: 

 - 02-Develop-and-test-data-cleaning.ipynb
 - 03-Develop-extraction-process.ipynb

A small test category was used for the model development process. The full extract of the 2 categories results in 6000+ pages, this will only be loaded once the model is working correctly.

Based on findings from the exploration of the wiki data structure the category load process was split into 5 parts:

1. Pull all subcategories using a recursive function call. A list of subcategories is kept and checked for any duplication before further action.
2. Write a record of loaded subcategories to the mongo db.
3. Identify unique pages for unique set of subcategories identified in step 1
4. For each unique page, pull extract and category information
5. Clean extract and load to mongodb. 

An iterative process was used to establish the data cleaning criteria. For the initial iterations the cleaned extract was reviewed, and the criteria tweaked. This was followed by the creation and review of the document term matrix which resulted in some further tweaks to the cleaning criteria.
    

A class, called 'WikiAPI', containing the load functions was built implementing the final model.

Functions contained in "WikiAPI': 

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
Jupyter notebook: 04-Develop-Semantic-search-process.ipynb

The development of the search process was broken down into four steps:

1. Build a 'corpus' of articles - during development this was limited to a test set of 255 pages so that the document term matrix (dtm) was small enough to load into a dataframe for inspection. 

2. Construct the document term matrix for the corpus using Tfidf and load into a panads dataframe. (In the final model implentation the data is kept in a sparse matrix until the final step to present search results.)

3. Apply TruncatedSVD with 200 components. In early tests the size of the dtm dataframe caused lots of crashes so the development process was restricted to a smaller test set. 

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
Evaluating search engine results is challenging, with limited resouces I choose to use a well known and trusted search engine to provide bench mark results.
I measured my search engine against the results found using google, with the search restricited to the en.wikipedia site.

Google search can be restricted to a particular site using ...
 -  ' site:en.wikipedia.org SEARCHTERM '
 
Comparing the top 10 results (where available from google) I tested..
1. The overall effectiveness of my search engine 
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







