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

There is no maximium no. of levels.

Categories can belong to multiple catgories 

Each page can be assigned to multiple categories

Requirments:
- Limit depth of search 
- remove duplication during load process 

- Add logic to avoid getting stuck in a loop - by removing duplication - also need to do this to reduce volume of articles

When pulling need to consider - 
    * Remove duplication
    * Pull ALL items in category
    * Keep tree structure - how are we going to serach

### Pull Articles for each page
Avoid duplication due to volume 
Data cleaning 
    • Remove any hypertext
    • Remove weird puntuation
    • Remove digits
    • Lemmatize text
    • Remove stop words



## Data Storage
Store data in a Mongo Database ( an open source nosql database that stores data in JSON ). The benefit of using a nosql datbase is taht the data does not need to be structured and no complex table strucutre or sql code are requried to store or query the data. 

Data will be stored in a flat structure made up of 3  ???

Mongo DB hosted on AWS instance.

Set up....



## Search algorithm development
We want your code to be modular enough that any valid category from Wikipedia can be queried by your code. 

Code should be able to pull additional wikipedia categories beyond ML and Business Software. 



## Predictive modeling



## Front end web service
Develop a simiple tront end web service using flask to provide user access to search engine and to trigger python script for each of the activites

Finally, you should be able to pass the url of a wikipedia page and it will generate a prediction for the best category for that page, along with a probability of that being the correct category. 

