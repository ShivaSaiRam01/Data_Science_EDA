# review.py


import urllib.request
from bs4 import BeautifulSoup
import time
import streamlit as st
import pandas as pd
import google.generativeai as genai

def main():

    def get_html(url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        return response.read()

    def parse_reviews(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        reviews = []
        for review_div in soup.find_all('div', {'data-hook': 'review'}):
            try:
                review_text = review_div.find('span', {'data-hook': 'review-body'}).text.strip()
                reviews.append(review_text)
            except AttributeError:
                continue
        return reviews

    def get_amazon_reviews(product_url, max_pages=5, max_reviews=50):
        reviews = []
        for page in range(1, max_pages + 1):
            if len(reviews) >= max_reviews:
                break
            url = f"{product_url}&pageNumber={page}"
            html_content = get_html(url)
            new_reviews = parse_reviews(html_content)
            if not new_reviews:
                break
            reviews.extend(new_reviews[:max_reviews - len(reviews)])
            time.sleep(4)
        return reviews

    # Streamlit interface
    st.title('Amazon Product Reviews Analyzer')
    url_amazon = st.text_input('Enter or paste the Amazon product URL: ')
    
    if st.button('Get Reviews'):
        if url_amazon:
            reviews = get_amazon_reviews(url_amazon, max_pages=5, max_reviews=50)
            # st.write("Fetched Reviews:")
            # for i, review in enumerate(reviews, 1):
            #     st.write(f"Review {i}: {review}")
            
            # AI categorization
            key = "AIzaSyDR2ZO3GBl2tm-dghyH476ycPPUKK3IWBA"
            # st.title('google api key')
            # key = st.text_input('Enter the API key : ')

            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-pro")
            
            prompt = f"categorize the given list {reviews} of reviews and give me wheather they are categorized a 'positive' or 'negative' responses and store them in a list"
            try:
                response = model.generate_content(prompt)
                categories = eval(response.text)  # Handle the response correctly
                data = pd.DataFrame(list(zip(reviews, categories)), columns=['Review', 'Category'])
                
                st.write("Categorized Reviews:")
                st.write(data)
            except Exception as e:
                st.error(f"Error in AI categorization: {e}")
        else:
            st.error("Please enter a valid Amazon product URL.")

if __name__ == '__main__':
    main()
