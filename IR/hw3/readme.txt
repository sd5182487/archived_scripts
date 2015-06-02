Readme
Q&A for problem 1 and 2. Comment in source code will help as well
P1:
1. why do it like this? Why choose 2? And what might be a more intelligent (but more work-intensive) way of doing this?
A:
If missing ratings takes majority of all ratings, the avg rating would be very low.This biased rating is more far from real user ratings.I think we choose 2 because the expect avg score is 3,by -2, scores on the left(of 3) become <= 0,scores on the right(and 3) become >0 but smaller. This will let the score be more accurate after resift the data back.

More intelligent way : I think we could recursively use this predict function to fill all missing ratings, then make a predict.But of course this will be very very slow...

P2:
1.compare results from 1 and 2
P2 runs much faster than p1,as model based won’t need to query whole data set, and number of movies is much smaller than users. And p2 result tend to be more accurate,if we choose a representative enough model, it’s easier to try to avoid overfitting situations.Meanwhile, the data chose to make the model could be biased,which will cause the result far from real rating.
2.
According to users who like/dislike the movie(ratings), if the movie got some similar movies, user tend to rate these movies with similar ratings.
We are assuming the select users can represent all users in data set(all users’ idea towards a movie is same).
3.
Memory based : For some certain user/movie pairs, we can’t get a prediction if he active user has no items in common with all people who have rated the target movie.And even very few people rated the movie would bias the rating, prediction is alike of these few users.
And as we take the avg value of all ratings as standard, for those high/low rating users, predict result would be biased.

Model based: If the model is build upon biased data(which is likely to happen), the result of whole data set is biased.So the quality depends on how representative the model is.

solution: combine these 2 algorithms together，use ‘enough’ data(memory based) to make better predict models(model based), but how to determine it’s enough is another tricky thing.Further and deeper research needed.

****************************************************
Thanks to Yilin for helping me get through p2 matrix things and enlighten me on some algorithm
****************************************************