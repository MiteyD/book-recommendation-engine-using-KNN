# -*- coding: utf-8 -*-
"""Copy of fcc_book_recommendation_knn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19w_N7ospJH6hovVSzK8xyCpkHKbhhDaW

*Note: You are currently reading this using Google Colaboratory which is a cloud-hosted version of Jupyter Notebook. This is a document containing both text cells for documentation and runnable code cells. If you are unfamiliar with Jupyter Notebook, watch this 3-minute introduction before starting this challenge: https://www.youtube.com/watch?v=inN8seMm7UI*

---

In this challenge, you will create a book recommendation algorithm using **K-Nearest Neighbors**.

You will use the [Book-Crossings dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/). This dataset contains 1.1 million ratings (scale of 1-10) of 270,000 books by 90,000 users. 

After importing and cleaning the data, use `NearestNeighbors` from `sklearn.neighbors` to develop a model that shows books that are similar to a given book. The Nearest Neighbors algorithm measures distance to determine the “closeness” of instances.

Create a function named `get_recommends` that takes a book title (from the dataset) as an argument and returns a list of 5 similar books with their distances from the book argument.

This code:

`get_recommends("The Queen of the Damned (Vampire Chronicles (Paperback))")`

should return:

```
[
  'The Queen of the Damned (Vampire Chronicles (Paperback))',
  [
    ['Catch 22', 0.793983519077301], 
    ['The Witching Hour (Lives of the Mayfair Witches)', 0.7448656558990479], 
    ['Interview with the Vampire', 0.7345068454742432],
    ['The Tale of the Body Thief (Vampire Chronicles (Paperback))', 0.5376338362693787],
    ['The Vampire Lestat (Vampire Chronicles, Book II)', 0.5178412199020386]
  ]
]
```

Notice that the data returned from `get_recommends()` is a list. The first element in the list is the book title passed in to the function. The second element in the list is a list of five more lists. Each of the five lists contains a recommended book and the distance from the recommended book to the book passed in to the function.

If you graph the dataset (optional), you will notice that most books are not rated frequently. To ensure statistical significance, remove from the dataset users with less than 200 ratings and books with less than 100 ratings.

The first three cells import libraries you may need and the data to use. The final cell is for testing. Write all your code in between those cells.
"""

# import libraries (you may add additional imports but you may not have to)
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt

# get data files
!wget https://cdn.freecodecamp.org/project-data/books/book-crossings.zip

!unzip book-crossings.zip

books_filename = 'BX-Books.csv'
ratings_filename = 'BX-Book-Ratings.csv'

# import csv data into dataframes
df_books = pd.read_csv(
    books_filename,
    encoding = "ISO-8859-1",
    sep=";",
    header=0,
    names=['isbn', 'title', 'author'],
    usecols=['isbn', 'title', 'author'],
    dtype={'isbn': 'str', 'title': 'str', 'author': 'str'})

df_ratings = pd.read_csv(
    ratings_filename,
    encoding = "ISO-8859-1",
    sep=";",
    header=0,
    names=['user', 'isbn', 'rating'],
    usecols=['user', 'isbn', 'rating'],
    dtype={'user': 'int32', 'isbn': 'str', 'rating': 'float32'})

# add your code here - consider creating a new cell for each section of code
print(df_books)

print(df_ratings)

# Calculate user and book rating counts
user_RatingCount = df_ratings.groupby('user')['rating'].count().reset_index().rename(columns = {'rating':'userTotalRatingCount'})
book_RatingCount = df_ratings.groupby('isbn')['rating'].count().reset_index().rename(columns = {'rating':'bookTotalRatingCount'})

# Add to df_ratings
df_ratings = df_ratings.merge(user_RatingCount,how='left', left_on='user', right_on='user')
df_ratings = df_ratings.merge(book_RatingCount, how='left', left_on='isbn', right_on='isbn')

# Filter data for statistical significance
df_ratings_2 =df_ratings.loc[(df_ratings['userTotalRatingCount']>=200) & (df_ratings['bookTotalRatingCount']>=100)]

# merge data sets
books_with_ratings = pd.merge(df_ratings_2, df_books, on='isbn')
print(books_with_ratings)

# Remove duplicates
books_with_ratings_2 = books_with_ratings.drop_duplicates(['title', 'user'])

# Preparing data table for analysis
books_with_ratings_pivot = pd.pivot_table(data=books_with_ratings_2, values='rating', index='title', columns='user').fillna(0)
print(books_with_ratings_pivot)

# Convert to 2D matrıx
books_with_ratings_matrix = csr_matrix(books_with_ratings_pivot.values)

# Train Model
model_knn = NearestNeighbors(algorithm='auto', metric='cosine')
model_knn.fit(books_with_ratings_matrix)

# function to return recommended books - this will be tested
def get_recommends(book = ""):

  X = books_with_ratings_pivot[books_with_ratings_pivot.index == book]
  X = X.to_numpy().reshape(1,-1)
  distances, indices = model_knn.kneighbors(X,n_neighbors=8)
  recommended_books = []
  for x in reversed(range(1,6)):
      bookrecommended = [books_with_ratings_pivot.index[indices.flatten()[x]], distances.flatten()[x]]
      recommended_books.append(bookrecommended)
  recommended_books = [book, recommended_books]
  
  return recommended_books

books = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
print(books)

"""Use the cell below to test your function. The `test_book_recommendation()` function will inform you if you passed the challenge or need to keep trying."""

books = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
print(books)

def test_book_recommendation():
  test_pass = True
  recommends = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
  if recommends[0] != "Where the Heart Is (Oprah's Book Club (Paperback))":
    test_pass = False
  recommended_books = ["I'll Be Seeing You", 'The Weight of Water', 'The Surgeon', 'I Know This Much Is True']
  recommended_books_dist = [0.8, 0.77, 0.77, 0.77]
  for i in range(2): 
    if recommends[1][i][0] not in recommended_books:
      test_pass = False
    if abs(recommends[1][i][1] - recommended_books_dist[i]) >= 0.05:
      test_pass = False
  if test_pass:
    print("You passed the challenge! 🎉🎉🎉🎉🎉")
  else:
    print("You havn't passed yet. Keep trying!")

test_book_recommendation()