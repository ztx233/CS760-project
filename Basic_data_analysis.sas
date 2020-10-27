data movies;
	length MovieID 8 Title $40 Genres $40;
	infile "/folders/myfolders/STATS785/others/data.txt" delimiter=";" firstobs=1;
	input MovieID Title $ Genres $;
run;

data users;
	infile "/folders/myfolders/STATS785/others/users.dat" delimiter=":" firstobs=1;
	input UserID Gender $ Age Occupation Zipcode;
run;

data ratings;
	infile "/folders/myfolders/STATS785/others/ratings.dat" delimiter=":" 
		firstobs=1;
	input UserID MovieID Rating Timestamp;
run;

ods output summary=a;

proc means data=ratings;
	class movieid;
	var rating;
run;

proc sgplot data=a;
	scatter x=rating_n y=rating_mean;
	XAXIS LABEL="Rating times of a movie";
	YAXIS LABEL="Average Rating";
run;

ods output summary=b;

proc means data=ratings;
	class userid;
	var rating;
run;

proc sgplot data=b;
	scatter x=rating_n y=rating_mean;
	XAXIS LABEL="Rating times of a user";
	YAXIS LABEL="Average Rating";
run;

proc sgplot data=ratings;
	HISTOGRAM rating;
run;

data user_ratings;
	merge users(in=a) b;
	by userid;

	if a;
run;

proc sgplot data=user_ratings;
	density rating_mean / group=gender;
run;

ods output summary=c;

proc means data=user_ratings;
	class age;
	var rating_mean;
run;

proc sgplot data=c;
	series x=age y=rating_mean_mean;
	YAXIS LABEL="Average Rating";
run;

PROC FORMAT;
	VALUE index_to_occu 0="other or not specified" 1="academic/educator" 
		2="artist" 3="clerical/admin" 4="college/grad student" 5="customer service" 
		6="doctor/health care" 7="executive/managerial" 8="farmer" 9="homemaker" 
		10="K-12 student" 11="lawyer" 12="programmer" 13="retired" 
		14="sales/marketing" 15="scientist" 16="self-employed" 
		17="technician/engineer" 18="tradesman/craftsman" 19="unemployed" 20="writer";
RUN;

proc sgplot data=user_ratings;
	format occupation index_to_occu.;
	density rating_mean / group=occupation;
	legend 

run;