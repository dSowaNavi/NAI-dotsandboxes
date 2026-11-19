import json
import pandas as pd
from sklearn.cluster import KMeans


class RecommendationEngine:
    """
    This class aims to recommend movies for users using a kmeans clustering
    The algorithm groups users using their movie rating habits.
    It first uses kmeans in order to group these users, then a Pearson in order to determine similarity between these users,
    and using the same scores a weighted average determines which movie is recommended.

    Variables:
    Target (string) : Full name of the user receiving the recommendation.
    file_name (str) :  Path to the json file containing user names and their movie ratings.
    """
    def __init__(self, file_name):
        "Loads the user  data from a json file and stores it in variable dataset"
        self.target= ""
        self.file_name = file_name
        with open(self.file_name, "r", encoding="UTF-8") as file:
            self.dataset = json.load(file)


    def kmeans(self):
        """
        generates a movie recommendtion using k-means clustering
        1. Converts the JSON dataset into a pandas DataFrame.
        2. Normalises ratings by subtracting each user's average rating.
        3. Fills missing values with zero for K-Means clustering.
        4. Groups users into clusters based on their rating patterns.
        5. Finds user's cluster and calculates Pearson correlations between the target user
           and other users in the same cluster.
        6. Selects the five most similar users within the cluster, this was done to ensure strong connections as data is limited.
        8. Calculates weighted average movie ratings using the
           selected users' normalised ratings.
        9. Removes movies already rated by the target user.
        10. Sorts the remaining movies by predicted preference and prints them out.

        """
        #Convert json data to a panda's DataFrame
        matrix = pd.DataFrame.from_dict(self.dataset, orient="index")
        # Normalize all user ratings to better analise them
        normalized = matrix.sub(matrix.mean(axis=1), axis=0)
        # For handling clustering, filling missing data with 0.
        filled_data = normalized.fillna(0)
        # Cluster users
        kmeans = KMeans(n_clusters=3, n_init=10,  random_state=42)
        kmeans.fit(filled_data)

        # find out which cluster our target belongs to
        user_clusters = pd.Series(kmeans.labels_, index=matrix.index)
        cluster = user_clusters[self.target]

        # calculate how similar each user is to target using pearson method
        similarities = matrix.T.corr(method="pearson", min_periods=3)

        similar_users = similarities[self.target][
            user_clusters == cluster
            ].drop(self.target, errors='ignore')

        # drop NaN to avoid including missing connections
        similar_users = similar_users.dropna()
        # select 5 most similar users to target to gain the strongest recommendation
        similar_users = similar_users.nlargest(5)

        if similar_users.empty:
            print("No sufficiently similar users found.")
            return

        # grab ratings of similar users
        ratings = normalized.loc[similar_users.index]

        # Calculate a weighted average of all movies rated by similar users
        weighted_ratings = ratings.multiply(similar_users, axis=0)

        recommendations = (
                weighted_ratings.sum(axis=0) /
                ratings.notna().multiply(similar_users, axis=0).sum(axis=0)
        )

        # remove any movies already watched by our  target
        recommendations = recommendations.drop(
            matrix.loc[self.target].dropna().index,
            errors='ignore'
        )

        # get top 5 and bottom 5 recommended movies based on their  score
        recommendations = recommendations.dropna().sort_values(ascending=False).index.tolist()
        print(f'Top 5 most recommended movies: {recommendations[:5]}')
        print(f'Top 5 least recommended movies: {recommendations[-5:]}')
        print(f'Based on similar users: {similar_users.index.tolist()}')

    def handle_input(self):
        """
        simple function to handle input from the user. It takes asks for target user's full name,
        then checks if it exists within the  dataset.
        If it exists the  program can proceed.
        """
        target_user = input("Please enter target name (case sensitive): ")
        target_user = target_user.strip()
        if target_user not in self.dataset:
            print("This user is not in the dataset.")
        else:
            self.target = target_user
            engine.kmeans()

engine =  RecommendationEngine("ratings_dict.json")
engine.handle_input()






