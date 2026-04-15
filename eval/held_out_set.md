# Held-Out Set

Record held-out evaluation queries and expected answer notes here.

## Template

```md
## Query ID
Dataset:
Question:
Expected answer notes:
Why this query matters:
```

## yelp-q1
Dataset: yelp
Question: What is the average rating of all businesses located in Indianapolis, Indiana?
Expected answer notes: Average should resolve near 3.55 and pass the validator.
Why this query matters: Exercises the base cross-database Yelp rating path.

## yelp-q2
Dataset: yelp
Question: Which U.S. state has the highest number of reviews, and what is the average rating of businesses in that state?
Expected answer notes: State should resolve to PA/Pennsylvania; numeric value should match validator tolerance near 3.6994.
Why this query matters: Exercises cross-source mapping and aggregation semantics.

## yelp-q3
Dataset: yelp
Question: During 2018, how many businesses that received reviews offered either business parking or bike parking?
Expected answer notes: Count should resolve to 35 in the verified path.
Why this query matters: Exercises attribute parsing and year extraction under mixed date formats.

## yelp-q4
Dataset: yelp
Question: What category has the highest business count, and what is the average rating for that category?
Expected answer notes: Category should resolve to Restaurant / Restaurants with average rating near 3.63.
Why this query matters: Exercises category aggregation and validator-friendly output formatting.

## yelp-q5
Dataset: yelp
Question: Which state has the highest average rating among businesses with reviews?
Expected answer notes: State should resolve to PA with average rating near 3.48.
Why this query matters: Exercises state-level ranking and numeric aggregation.

## yelp-q6
Dataset: yelp
Question: Which business received the highest average rating between January 1, 2016 and June 30, 2016, and what category does it belong to? Consider only businesses with at least 5 reviews.
Expected answer notes: Business should resolve to Coffee House Too Cafe with categories present.
Why this query matters: Exercises date-window filtering plus category extraction quality.

## yelp-q7
Dataset: yelp
Question: Among users who registered on Yelp in 2016, which 5 business categories have received the most total reviews from those users since 2016?
Expected answer notes: The validated category set is Restaurants, Food, American (New), Shopping, Breakfast & Brunch.
Why this query matters: Exercises user date filtering, category extraction, and final answer synthesis.
