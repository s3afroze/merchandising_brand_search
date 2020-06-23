
# coding: utf-8

# @author: Shahzeb Afroze
# 
# The project involves creating leads for the merchandising team
# 
# ## Case Study Points 
# 
# #### Required:
# * Brand Name
# * Website
# * associated tag for why the Brand is a good fit (i.e. emerging brand, fills a need, etc.)
# 
# #### Bonus Points:
# * contact information
# * social media metadata
# 
# #### Assumption:
# * All the categories sold are listed in the csv file
# 
# #### Categories Preferred:
# * gourmet grocery
# * health focused food and beverage
# * specialty diet food and beverage.
# 
# ## Code Implemention
# 
# #### Interesting Resources:
# * https://strategy.data.gov/proof-points/2019/09/06/usda-linked-nutrition-data/
# * https://www.ers.usda.gov/publications/pub-details/?pubid=92570
# * https://www.nal.usda.gov/fnic/nutrient-lists-standard-reference-legacy-2018 (creating nlp model)
# * Google Knowledge Graph API
# * Google migration to wikidata paper (discussion of graph) https://research.google.com/pubs/archive/44818.pdf
# * Wikidata https://janakiev.com/blog/wikidata-mayors/
# 
# #### Databases Available:
# * FDA API: https://open.fda.gov/apis/
# * FDA User Interface: https://datadashboard.fda.gov/ora/fd/fser.htm
# * FoodData Central API: https://fdc.nal.usda.gov/index.html
# * World Opendata API: https://github.com/openfoodfacts/openfoodfacts-python
# * Open product Data: https://product.okfn.org/
# * Barcode Lookup: https://www.barcodelookup.com/19022128593




# import library
# import googlesearch # not dependable
import clearbit
from requests_html import HTMLSession # scraping purposes
import random
import re
# from googlesearch import search # not dependable, replaced with API
import time
import urllib
import json
import pandas as pd
import os

# ### Merchandising Expertise Input

# In[2]:


# ingredients required
# category of product needed
# product barcode provied and similar products or brands required 

# create a trend score, look at clearbit info, retreive pytrend info and google knowledge graph - last priority


# ### Search Food Central Database to get companies that meet criteria

# In[3]:


import requests

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}
        
class FoodData_Central_Database:
    def __init__(self, api_key):
        """
        Engaging with food database to find products that meet criteria in order to generate required brands
        
        API Documentation: https://fdc.nal.usda.gov/api-spec/fdc_api.html#/
        
        NOTE: Category of product will be important to optimise accuracy of information, but preferring speed over accuract 
        """
        self.api_key = api_key
        self.headers = headers
        
    def search(self, query, number_of_leads):
        """
        Searches for a general query - this could included ingredients, special string
        Search Operators: https://fdc.nal.usda.gov/help.html#bkmk-2
        
        Parameters: 
        -----------
        query: str
            to be searched
        
        number_of_leads: int
            number of potential companies to be looked up
            
        Returns: 
        -------
        json_data: dict
        
        if there is no result for query, returns None 
        else, dictionary is returned
        
        json_data: dict 
            A lot of information sent back from the the api for search query
               
        """
        api_key = self.api_key
        headers = self.headers
        
        page_size = min(10000, number_of_leads) # maximum of 10K leads per search
        
        params = {
            'api_key': api_key,
            'query': query,
            'pageSize':page_size,
            "dataType":["Branded"]
        }
        
        # no result for query
        try:
            response = requests.get('https://api.nal.usda.gov/fdc/v1/foods/search', headers=headers, params=params)
            json_data = response.json()
            return json_data
        except:
            pass # returns None
        
        
    def search_by_fdc_id(self, fdc_id):
        """
        Searches for a specific food product
                
        Parameters: 
        -----------
        fdc_id: str or int
            unique database id of food cental datase
            
        Returns: 
        -------
        json_data: dict
        
        if there is no result for query, returns None 
        else, dictionary is returned
        
        json_data: dict 
            A lot of product specific information
               
        """
        api_key = self.api_key
        headers = self.headers
        
        params = {
            'api_key': api_key
        }
        
        fdc_id = str(fdc_id) # ensures that it is in string for api
        
        # no result for query
        try:
            response = requests.get(f'https://api.nal.usda.gov/fdc/v1/food/{fdc_id}', headers=headers, params=params)
            json_data = response.json()
            return json_data
        except:
            pass # returns None
    
    
    def get_product_category(self, fdc_id, index_pos):
        """
        Retrives brand category from json data and removes non-char 
                
        Parameters: 
        -----------
        fdc_id: str or int
            unique database id of food cental datase
        
        index_pos: int
            index position from list extracted to be. Error preventative measure is min of index and len of list
            
        Returns: 
        -------
        food_categ: str
            category of food that the company belongs to               
        """
        
        json_data = self.search_by_fdc_id(fdc_id)
        raw_food_categ_string = json_data['brandedFoodCategory']
        raw_food_categ_list = raw_food_categ_string.split(',')        

        food_categ_list = raw_food_categ_list.copy() # temp solution, need to look into suitable regex         
    
        index_pos = min(index_pos, len(food_categ_list)-1) # ensures that there are no errors, expected value is 0
        categ_value = food_categ_list[index_pos]
        
        return categ_value

        
    def similar_product_search(self, list_of_ingredients, number_of_leads):
        """
        Searches products which has ingredients in list
                
        Parameters: 
        -----------
        list_of_ingredients: list
            output from food output function - consists of required ingredients
        
        number_of_leads: int
            number of potential companies to be looked up            
            
        Returns: 
        -------        
        unique_companies: list of dict or NONE
            if NO result generated from critera, returns None             
            
            dict values inside list:
            
            company['fdcId']: str
                unique id of database
            
            company['brandOwner']: str
                name of food brand
            
            company['category']: str
                category of food that the company belongs to                        
        """
        
        # special operators
        list_of_ingredients_search = ['+' + ing for ing in list_of_ingredients]
        query = ' '.join(list_of_ingredients_search)
        
        unique_companies = self.execute(query, number_of_leads)
        
        return unique_companies
    
    def execute(self, query, number_of_leads):
        """
        Finds food brands that meet search criteria
                
        Parameters: 
        -----------
        query: str
            to be searched
        
        number_of_leads: int
            number of potential companies to be looked up            
            
        Returns: 
        -------        
        unique_companies: list of dict or NONE
            if NO result generated from critera, returns None             
            
            dict values inside list:
            
            company['fdcId']: str
                unique id of database
            
            company['brandOwner']: str
                name of food brand
            
            company['category']: str
                category of food that the company belongs to                        
        """
        
        json_data = self.search(query, number_of_leads)
        
        # if there is any result
        try:
            list_of_products = json_data['foods']

            all_possible_companies = []
            for product in list_of_products:
                company = {}
                company['fdcId'] = product['fdcId']
                company['brandOwner'] = product['brandOwner']
                all_possible_companies.append(company)

            # unique companies dict only
            # code bit from https://stackoverflow.com/questions/11092511/python-list-of-unique-dictionaries
            unique_companies = list({v['brandOwner']:v for v in all_possible_companies}.values())

#             for company in unique_companies:            
#                 fdcId = company['fdcId'] # extract to search
#                 category = self.get_product_category(fdcId, 0)            
#                 company['category'] = category # insert result

            return unique_companies
        except:
            pass # returns None
            

    


# ### Open Food Facts Search

# In[4]:


# not the fastest result

class Open_Food_Facts:
    """
    Engages with crowd sourced dataset for food
    
    https://us.openfoodfacts.org/product/7622210109767/the-natural-confectionery-co-candy-jungle-jellies    
    """
    def __init__(self):
        pass # no api_key needed
    
    def search_for_product_by_gtinUpc(self, gtinUpc):
        """
        Searches for the database by UPC
        
        Parameters: 
        -----------
        gtinUpc: handles both int and str 
            gtinUpc the unique barcode for a product.
            
        Returns: 
        -------
        product_data: dict or None
        
        if there is result for UPC, returns None 
        else, dictionary is returned
        
        product_data: dict 
            contains granular information for the product # https://github.com/openfoodfacts/OpenFoodFacts-APIRestPython
               
        """
        gtinUpc = str(gtinUpc)
        response = requests.get(f'https://world.openfoodfacts.org/api/v0/product/{gtinUpc}.json')
        
        # no try except return needed since API will send an empty key with dictionary
        json_data = response.json()
        product_data = json_data['product']        
        return product_data
        
    def get_ingredients_for_product(self, gtinUpc, propotion_of_ingredients):
        """
        Retreives ingredients for the product UPC
        
        Parameters: 
        -----------
        gtinUpc: handles both int and str 
            gtinUpc the unique barcode for a product.
        
        propotion_of_ingredients: int
            the propotion of ingredient list in the product list required
        
        Returns: 
        -------
        ingredients_selected: list or None
        
        if there is result for UPC, returns None 
        else, subset of ingredients is returned
        
        ingredients_selected: list 
            subset of ingredient to be used for searching Food Central Database
               
        """
        product_data = self.search_for_product_by_gtinUpc(gtinUpc)
        ingredients_tags = product_data['ingredients_tags']
        
        if ingredients_tags:
            ingredients_tags_cleaned = [ing.replace('en:', '') for ing in ingredients_tags]
            number_of_tags_to_select = round(len(ingredients_tags_cleaned)* float(propotion_of_ingredients/100))
            ingredients_selected = random.sample(ingredients_tags_cleaned, number_of_tags_to_select)
            return ingredients_selected
        


# ### Searching Company

# In[5]:


# # setup clearbit
# import clearbit
# import urllib
# import json


# # S1 Key - $7 for 10,000 Calls


# In[6]:


# import googlesearch

# setting parameter requirements - https://developers.google.com/knowledge-graph/reference/rest/v1
class Google_Knowledge_Graph:
    """
    Leverages algorithim that powers search engine to find the correct domain for the company and gives 
    confidence on searching for the business domain.

    Parameters: 
    -----------

    api_key: str
        Private API Key - 100K/day free limit
    """
    def __init__(self, api_key):
        
        self.service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        self.limit = 1
        self.indent = True
        self.category_of_search = 'Corporation'
        self.api_key = api_key
    
    def search_company(self, query):
        """
        Searches for the company in the google search engine graph
        
        Parameters: 
        -----------

        query: str
            name of company to be searched
            
        Returns: dict
        -------
        if there is no corporate with a 'similar' name, returns None 
        else, dictionary is returned 
        
        package['company_url']: str 
            possible empty string if confidence is not high enough
            
        package['graph_linkage_confidence']: float 
            indicates SEO level of company
            
        package['company_name_optimized']: str 
            what graph knowledge believe is the closest name
            
        package['company_name_food_data_central']: str
            food company name in food central database simply added to package
            
        """
        
        service_url = self.service_url
        limit = self.limit
        indent = self.indent
        category_of_search = self.category_of_search
        api_key = self.api_key
        
        # search with category
        params = {
            'query': query,
            'limit': limit,
            'indent': indent,
            'key': api_key,
            'types': category_of_search
        }
        
        url = service_url + '?' + urllib.parse.urlencode(params)
        response = json.loads(urllib.request.urlopen(url).read())
        
        # extract information which comes out
        try:
            result = response['itemListElement'][0]['result']
            company_name_optimized = result['name']            
            
            # url only comes for company with right seo
            try:
                company_url = result['url']
            except:
                company_url = ''
            
            confidence = response['itemListElement'][0]['resultScore'] # will help us in confidence scoring and if human input might be needed
            package = {}
            # create a dictionary to return
            package['company_url'] = company_url
            package['graph_linkage_confidence'] = float(confidence)
            package['company_name_optimized'] = company_name_optimized
            package['company_name_food_data_central'] = query # company searched      
        except:
            package = {}
            package['company_url'] = ''
            package['graph_linkage_confidence'] = 0.0
            package['company_name_optimized'] = query # necessary because domain search will be using the string to create variations. Preprocessing might help in only retreving unique values
            package['company_name_food_data_central'] = query # company searched
        
        return package  



# In[7]:


class Domain_Searcher:    
    """
    Finding the right domain is the key for getting information on the company and will have a dedicated
    class to combine various straegies and pick the ones that have 
    
    https://ahrefs.com/blog/google-advanced-search-operators/
    
    Parameters: 
    -----------    
    google_knowledge_graph: class
        initated class for searching on graph engine   

    Note: Simple rules being used, confidence metric would help the team who to target.    
    """
    
    def __init__(self, google_knowledge_graph):
         self.google_knowledge_graph = google_knowledge_graph
    
    def clearbit_name_lookup(self, company_name_optimized, company_name_food_data_central):
        """
        50K/month free search limit for the API. Attempts in matching company name to domain. 
        
        Parameters: 
        -----------
        company_name_optimized: str
            name of company linked with google graph

        company_name_food_data_central: str
            company name secured from food central database
        
        Returns: dict or None
        -------
        
        clearbit_package['domain_list']: str
            list of potential domains for the company
        
        clearbit_package['confidence']: bool
            Bool value for confidence in result. True if domain matched on the orignal string, False if variation matched
        
        clearbit_package['company_variants']: list
            variant of company name based on simple rule, might help in optimising google search
            
        NOTE:In case domain matched in first 2 (orignal) company name string, return value else get the all variation for confidence in result
        """
        
        variation_string_list = self.create_company_string_variation(company_name_optimized, company_name_food_data_central)
        
        clearbit_package = {}        
        response_list_raw = []
        
        for company_name_variant in variation_string_list:
            response = clearbit.NameToDomain.find(name=company_name_variant)
            response_list_raw.append(response)
        
        # remove None values in domain_list, sent back by clearbit API if company name not matched by them. 
        response_list = [i for i in response_list_raw if i] 

        # extract the domain_url from dict
        domain_list = [i['domain'] for i in response_list]
        
        # if domain results for the orig string, high confidence that the url is correct
        condition_1 = response_list_raw[0] is not None
        condition_2 = response_list_raw[1] is not None

        confidence = False
        clearbit_package['url'] = ''
        
        if condition_1 or condition_2:
            clearbit_package['url'] = domain_list[0]
            confidence = True
        
        # create the final package
        
        clearbit_package['confidence'] = confidence
        clearbit_package['company_variants'] = variation_string_list
        
        return clearbit_package
        
        
    def create_company_string_variation(self, company_name_optimized, company_name_food_data_central):
        """
        Parameters: 
        -----------
        company_name_optimized: str
            name of company linked with google graph

        company_name_food_data_central: str
            company name secured from food central database
        
        Returns: dict
        -------
        variation_string_list: list
            list of "simple" variations applied on company to get the domain from the 
            clearbit database. Higher the index, greater variations made on string. Much Higher confidence for result
            in first 2 name in list.
            
        NOTE: there has been case when word like corporation can limit matching the clearbit database. 
            The last 2 word in the list hopes to solve that issue. Advanced rules will involve NLP and will take
            more time in development.
        """
        
        variation_string_list = [company_name_optimized, company_name_food_data_central]
        
        try:
            variant_string_1 = company_name_optimized.rsplit(' ', 1)[0] 
            variant_string_2 = company_name_food_data_central.rsplit(' ', 1)[0] 

            variation_string_list.append(variant_string_1)
            variation_string_list.append(variant_string_2)
        except:
            pass # will just send back list with values sent
        
        return variation_string_list
    

    def general_bing_search(self, query):
        url = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
        payload = {'q': query, 'mkt':'en-US'}
        headers = {'Ocp-Apim-Subscription-Key': ''}
        r = requests.get(url, params=payload, headers=headers)
        json_data = r.json()
        subset_json_data = json_data.get('webPages', {}).get('value', {})        
        
        try:
            url = subset_json_data[0]['url'] # only first string retreived
            return url
        except:
            pass

        
    def bing_entity_search(self, query):
        """
        Returns a lot of information, currently only taking url
        """
        
        url = 'https://api.cognitive.microsoft.com/bing/v7.0/entities'
        payload = {'q': query, 'mkt':'en-US'}
        headers = {'Ocp-Apim-Subscription-Key': ''}
        r = requests.get(url, params=payload, headers=headers)
        json_data = r.json()
                
        try:
            package = {}
            url = json_data["places"]['value'][0]['url']
            telephone = json_data["places"]['value'][0]['telephone']
            package['url'] = url

            # telephones are difficult
            try:
                package['telephone'] = telephone
            except:
                package['telephone'] = ''
                
            return package
        except:
            pass

        
    def get_linkedin_company_members(self, position, company_name_optimized, company_name_food_data_central):
        linkedin_url_sales_team = f"site:linkedin.com/in AND '{position}' AND '{company_name_optimized}'OR {company_name_food_data_central}" # sales team set
        url = general_bing_search(linkedin_url_sales_team)
        
        return url
        
    def get_social_media_domains(self, company_name_optimized, company_name_food_data_central):
        """
        Needs a more pythonic formatting
        """
        social_media_channels = ['instagram', 'facebook', 'twitter']              
          
        social_media_package = {}        
        for social_media in social_media_channels:
            search_string = f'site:{social_media}.com "{company_name_optimized}"'
            url = self.general_bing_search(search_string)
                
            # save result        
            social_media_package[social_media] = url
        
        return social_media_package
                
        
    def execute(self, fdc_company_info, sleep_timer=2):
        """
        Parameters: 
        -----------

        fdc_company_info: dict
            company info from food central database
            
            fdc_company_info['brandOwner']: str
                name of company
                
            fdc_company_info['category']: str
                company category

        Returns: 
        -----------
        
        Note: pythonic conversion for maintance
        """
                
        google_knowledge_graph = self.google_knowledge_graph
        company_name = fdc_company_info['brandOwner']
#         category = fdc_company_info['category']
        
        lower_bound = 25.0 # compaies lower web presence will be difficult to find with simple conditional rules
        final_package = {} # dict holding for final info 
        
        time.sleep(sleep_timer) # avoiding google ip block
        
        # top strategy
        knowledge_package = google_knowledge_graph.search_company(company_name)
        
        company_url = knowledge_package['company_url']
        graph_linkage_confidence = knowledge_package['graph_linkage_confidence']
        company_name_optimized = knowledge_package['company_name_optimized']
        company_name_food_data_central = knowledge_package['company_name_food_data_central']
        
        # need to later change it to be more 'pythonic'
        
        # case when google graph has limited info on company!
        final_package['confidence'] = 'low' 
        final_package['company_name'] = company_name_food_data_central
        company_telephone = ''
        
        if graph_linkage_confidence>=lower_bound:
            final_package['confidence'] = 'high' 
            
            # case where google graph does not have company domain, they rarely do.
            if not company_url:
                final_package['confidence'] = 'medium'
                clearbit_package = self.clearbit_name_lookup(company_name_optimized, company_name_food_data_central)
                confidence_in_domains = clearbit_package['confidence'] 
                company_url = clearbit_package['url'] # take the first 1                
                
                # clearbit got the domain in their database!
                if not confidence_in_domains:
                    bing_response = self.bing_entity_search(company_name_food_data_central)
                    try:
                        company_telephone = bing_response['telephone']
                    except:
                        pass # telelphone already set as emptry str

                    try:
                        company_url = bing_response['url']                    
                    except:
                        pass # company_url already set as emptry str

                    final_package['company_telephone'] = company_telephone
                    
                    if not company_url:
                        company_url = self.general_bing_search(f'"{company_name_food_data_central}" OR {company_name_optimized}')
                        
        final_package['company_url'] = company_url
        social_media_package = self.get_social_media_domains(company_name_optimized, company_name_food_data_central)
        a = {**final_package, **social_media_package}

        return a
        


# In[20]:


class Merchandise_Optimization:
    # will use domain to extract necessary information or just package it into pandas to csv
    # will have an option to use clearbut domain lookup api or not. there are other alternatives available.
    # domain lookup is pretty expensive in general - can be built internally in a couple of days if needed
    def __init__(self):
        self.food_central_database = FoodData_Central_Database(food_central_database_api_key)
        self.open_food_facts = Open_Food_Facts()
        google_knowledge_graph = Google_Knowledge_Graph(google_graph_api_key)
        self.domain_searcher = Domain_Searcher(google_knowledge_graph)
        
    def execute_fdc(self, search_query, number_of_leads): 
        food_central_database = self.food_central_database
        domain_searcher = self.domain_searcher
        
        fdc_response = food_central_database.execute(search_query, number_of_leads)        
        
        final_package = []
        # checks if empty
        if fdc_response:
            for fdc_company_info in fdc_response:
                response_dict = domain_searcher.execute(fdc_company_info)
                final_package.append(response_dict)
        
        self.convert_dict_to_csv(final_package)
        
    def execute_open_food(self, upc, propotion, number_of_leads):        
        open_food_facts=self.open_food_facts
        food_central_database = self.food_central_database
        domain_searcher = self.domain_searcher
        
        propotion = min(100, propotion) # error prevent
        
        ing_list = open_food_facts.get_ingredients_for_product(upc, propotion)
        print(ing_list)
        
        if ing_list:
            fdc_response = food_central_database.similar_product_search(ing_list, number_of_leads)
            print(fdc_response)

            # checks if empty
            final_package = []
            if fdc_response:
                for fdc_company_info in fdc_response:
                    response_dict = domain_searcher.execute(fdc_company_info)
                    print()
                    final_package.append(response_dict)
                    
        self.convert_dict_to_csv(final_package)
        
    def convert_dict_to_csv(self, final_package):
        try:
            df = pd.DataFrame(final_package)
            df.to_csv(os.path.join('data', 'df.csv'))
        except:
            df = [{'no_result':'Need to opimise search'}]
        
        


# In[21]:


