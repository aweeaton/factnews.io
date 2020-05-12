from app import classes, credibility_model
from datetime import date
from app import sift


def test_UserFromDB():
    """
    Testing the User class atributes from the database
    """
    val = True
    assert classes.UserBL.UserFromDB("usertest").email == "usertest@gmail.com"
    assert classes.UserBL.UserFromDB("usertest").username == "usertest"
    assert classes.UserBL.UserFromDB("usertest").check_password("1234") == val


def test_EmailFromDB():
    """
    Testing the User class atributes from the database
    """
    val = True
    assert classes.UserBL.EmailFromDB("usertest@gmail.com").email \
        == "usertest@gmail.com"
    assert classes.UserBL.EmailFromDB("usertest@gmail.com").username \
        == "usertest"
    assert classes.UserBL.EmailFromDB("usertest@gmail.com"). \
        check_password("1234") == val


def test_register():
    """
    Testing the registration for new users (base flow)
    """
    username = "alumni"
    email = "alumni@gmail.com"
    password = "1234"
    user = classes.User(username, email, password)
    msg = classes.UserBL.RegisterUserDB(user)
    user = classes.UserBL.UserFromDB(username)
    val = True
    assert msg == "User registered"
    assert user.email == email
    assert user.username == username
    assert user.check_password(password) == val

    classes.UserBL.DeleteUserDB(username)


def test_existing_user():
    """
    Assuming that the usertest has previously been registered
    """
    user = classes.User.query.first()
    msg = classes.UserBL.RegisterUserDB(user)

    assert msg != "User registered"


def test_sift_retrieve_article_details():
    """
    Given an URL we check the title, summary and encoded txt
    """
    url = "https://www.bbc.com/news/av/science-environment-34921000"
    url = url + "/what-is-albert-einstein-s-theory-of-general-relativity"
    title, summary, encoded_txt = sift.retrieve_article_details(url)

    test_summary = "VideoOne hundred years ago today, Albert Einstein \
submitted his Theory of General Relativity, a pillar \
of modern physics that has transformed our understanding \
of space, time and gravity.\nBut what exactly is general \
relativity and what did Einstein predict?\nPhysicist Dr \
Toby Wiseman, from Imperial College London, explains."

    encoded_summary = "VideoOne hundred years ago today, Albert Einstein \
submitted his Theory of General Relativity, a pillar of \
modern physics that has transformed our understanding of \
space, time and gravity.But what exactly is general relativity \
and what did Einstein predict?Physicist Dr Toby Wiseman, \
from Imperial College London, explains."

    assert title == "What is Albert Einstein's Theory of General Relativity?"
    assert summary == test_summary
    assert encoded_txt == encoded_summary


def test_sift_reveal_source():

    url = 'https://www.bbc.com/news/av/science-environment-\
34921000/what-is-albert-einstein-s-theory-of-general-relativity'

    home_page, domain_name, subdomain_name = sift.reveal_source(url)

    assert home_page == 'https://www.bbc.com'
    assert domain_name == 'bbc'
    assert subdomain_name == 'bbc'


def test_sift_google_query():

    query = "https://www.google.com/search?q=What+is+\
Albert+Einstein's+Theory+of+General+Relativity?"

    all_links, query_page = sift.google_query(query,
                                              num_results=10,
                                              header={'User-agent':
                                                      'your bot 0'})

    assert len(all_links) == 10
    assert query_page == "https://www.google.com/search?q=https:\
//www.google.com/search?q=What+is+Albert+Einstein's\
+Theory+of+General+Relativity?"


def test_investigate_source():
    """
    Testing the wikipedia summary and self summary from
    investigate source function.
    """
    url = "https://www.bbc.com/news/av/science-environment-\
34921000/what-is-albert-einstein-s-theory-of-general-relativity"

    wiki_sum_gt = "The British Broadcasting Corporation (BBC) is a \
British public service broadcaster. Its headquarters are at \
Broadcasting House in Westminster, London. It is the world’s \
oldest national broadcaster, and the largest broadcaster in the \
world by number of employees. It employs over 22,000 staff in"

    self_sum_gt = ['Breaking news, sport, TV, radio and a whole lot \
more.\n        The BBC informs, educates and entertains \
- wherever you are, whatever your age.']

    self_wiki_link = 'https://en.wikipedia.org/wiki/BBC'
    self_desc = 'meta'

    wiki_link, self_desc_src, wiki_summary, self_summary = \
        sift.investigate_source(url)

    assert wiki_summary[:50] == wiki_sum_gt[:50]
    assert self_summary == self_sum_gt[0]
    assert wiki_link == self_wiki_link
    assert self_desc_src == self_desc


def test_find_better_coverage():
    """
    Tests top 5 results and query page from find better coverage function.
    """
    url = "https://www.bbc.com/news/av/science-\
environment-34921000/what-is-albert-einstein-s-theory-of-general-relativity"
    top_5_results, query_page = sift.find_better_coverage(url)

    query_page_gt = "https://www.google.com/search?\
q=Albert+Theory+General+Relativity"

    assert len(top_5_results) == 4
    assert query_page == query_page_gt


def test_credibility_model():

    url = "https://www.bbc.com/news/av/science-environment-34921000"
    url = url + "/what-is-albert-einstein-s-theory-of-general-relativity"

    title, summary, encoded_txt = sift.retrieve_article_details(url)
    score = credibility_model.predict_credibility(encoded_txt)

    assert score == 11
