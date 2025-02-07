from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, desc
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import tweepy
from langchain.chat_models import ChatOpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Automatically load the .env file from the current directory
load_dotenv()


# X API Credentials (Set in environment variables)
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")


# FastAPI app
app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://user:password@localhost:5432/media_agent"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model to store recent searches
class RecentSearch(Base):
    __tablename__ = "recent_searches"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    timestamp = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()))

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_SECRET)
api = tweepy.API(auth)

# LangChain setup
llm = ChatOpenAI(model_name="gpt-4", temperature=0.5)

def fetch_tweets(username: str):
    """Fetches tweets from the past 24 hours."""
    try:
        user = api.get_user(screen_name=username)
    except tweepy.TweepError:
        raise HTTPException(status_code=400, detail="Invalid username or user does not exist.")
    
    since_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    tweets = api.user_timeline(screen_name=username, tweet_mode="extended", count=100)
    return [tweet.full_text for tweet in tweets if tweet.created_at.strftime('%Y-%m-%d') >= since_date]

def summarize_tweets(tweets):
    """Summarizes the tweets using LangChain."""
    tweet_list = "***".join(tweets)
    prompt = """Your task is to generate a comprehensive summary report that includes all tweets, but with the following conditions:

Prioritization:

Financial Content First: Reorder the tweets so that all tweets containing financial content are listed at the top of the report. Financial content includes any mention of companies, stocks, cryptocurrencies, or ticker symbols (e.g., $TSLA, $XRP).
Non-Financial Content Afterwards: After the financial tweets, include the remaining tweets (e.g., personal updates, lifestyle content).
Financial Data Handling:

Consolidation of Entities: For tweets with financial content, if both a company name and its corresponding ticker symbol appear in the text, you do not need to capture them separately. Instead, consolidate the information so that the financial entity is represented just once along with all the associated data (such as news about earnings reports, stock price surges, or product announcements).
Associated Data Inclusion: Ensure that any financial details (e.g., “earnings report,” “new battery technology,” “stock surge”) are clearly captured with the tweet’s content.
Report Format:

The report should be organized with clear headings or sections. For example, you might use:
Financial Tweets: List all tweets with financial content, preserving their original content and context.
Other Tweets: List the remaining tweets that do not contain financial content.
Use bullet points, numbered lists, or sections to ensure the report is easy to read and clearly separates the financial information from the non-financial.
Content Inclusion:

All Tweets Included: Do not omit any tweet from the final report. Every tweet in the list must be present, but the order should reflect the financial prioritization as described.
Preserve Original Text: While you may reorganize and annotate the tweets, ensure that the original text content is preserved and clearly visible.
Additional Considerations:

If any tweet contains ambiguous content (e.g., a company name that might also refer to a non-financial term), use the context provided in the tweet to determine if it should be considered financial.
The final output should be a well-organized, easy-to-read summary report that clearly distinguishes between financial and non-financial content. '***' is the tweet separator to use for your tweet list provided below.

tweets: 
[{tweet_list}]


Using this prompt, generate a summary report that follows the above instructions. Make sure the final output is clear, well-organized, and includes all tweets with the financial content appearing first."""
    return llm.predict(prompt)

@app.post("/generate_report/")
def generate_report(username: str, db: Session = Depends(get_db)):
    """Fetch tweets, summarize, and return a report."""
    tweets = fetch_tweets(username)
    if not tweets:
        raise HTTPException(status_code=404, detail="No tweets found in the last 24 hours.")
    
    report = summarize_tweets(tweets)
    
    # Save recent search
    existing_search = db.query(RecentSearch).filter(RecentSearch.username == username).first()
    if not existing_search:
        db.add(RecentSearch(username=username))
        db.commit()
    
    # Keep only the 5 most recent searches
    recent_searches = db.query(RecentSearch).order_by(desc(RecentSearch.timestamp)).all()
    if len(recent_searches) > 5:
        for entry in recent_searches[5:]:
            db.delete(entry)
        db.commit()
    
    return {"report": report}

@app.get("/recent_searches/")
def get_recent_searches(db: Session = Depends(get_db)):
    """Returns the 5 most recent searched usernames."""
    searches = db.query(RecentSearch).order_by(desc(RecentSearch.timestamp)).limit(5).all()
    return [search.username for search in searches]
