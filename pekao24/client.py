# -*- coding: utf-8 -*-

import re
import mechanize
import cookielib
import urlparse
import urllib
import getpass
from BeautifulSoup import BeautifulSoup


class ConnectionError(Exception):
    pass


class AccessDenied(ConnectionError):
    MESSAGE = 'Wybrany serwis jest zablokowany'



class Pekao24(object):

    def __init__(self, client_id, password):
        self.client_id = client_id
        self.password = password
        self.connect()
        self.read_accounts()
        
    def connect(self):
        br = mechanize.Browser()

        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        br.set_handle_referer(True)
        br.set_handle_redirect(True)
        br.set_handle_equiv(True)

        # Follows refresh 0 but not hangs on refresh > 0
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # some headers
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.91 Safari/534.30')]

        # Debug
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)

        br.open('https://m.pekao24.pl/')
        br.select_form(nr=0)
        br['parUsername'] = str(self.client_id)
        response = br.submit()
        br.select_form(nr=0)

        password_pattern = ''

        soup = BeautifulSoup(response.get_data())
        labels = soup.find(None, {'class':'accoutNumber'}).findAll('label')
        for label in labels:
            text = label.string.strip()
            if text.startswith('#'):
                password_pattern += '#'
            elif text.startswith('['):
                password_pattern += '_'

        try:
            br['parPassword']
        except mechanize.ControlNotFoundError:
            br.form.new_control('password', 'parPassword', {})

        for idx, char in enumerate(self.password): 
            if password_pattern[idx] != '#':
                br['parPassword'] += char
        
        response = br.submit().get_data()
        if AccessDenied.MESSAGE in response:
            raise AccessDenied
        
        try:
            br.follow_link(text_regex=re.compile('rachunki', re.IGNORECASE))
            self.connected = True
        except mechanize.LinkNotFoundError:
            self.connected = False
            raise ConnectionError
        self.br = br
        
    def _get_params(self, url):
        return urlparse.parse_qs(urlparse.urlparse(url).query)
    
    def _get_opener(self):
        if not self.connected:
            raise ConnectionError
        return self.br
        
    def open_link(self, text_regex):
        response = self._get_opener().follow_link(text_regex=re.compile(text_regex, re.IGNORECASE))
        soup = BeautifulSoup(response.get_data())
        self.content = soup.find(id='content')
        return self.content
        
    def open_page(self, page_name, **params):
        current_params = self._get_params(self.br.geturl())
        current_params.update(params)
        
        url = 'https://m.pekao24.pl/MCP/%s.htm?%s' % (page_name, urllib.urlencode(current_params, True))
        response = self._get_opener().open(url)
        soup = BeautifulSoup(response.get_data())
        self.content = soup.find(id='content')
        return self.content
    
    def read_accounts(self):
        self.open_link('rachunki')
        self.open_link('lista rachunk')
        self.accounts = {}

        for table in self.content.findAll('table'):
            cells = table.findAll('td')
            account_url = cells[0].find('a').get('href')
            account_id = urlparse.parse_qs(urlparse.urlparse(account_url).query).get('parAccNum')[0]
            account_name = cells[0].text
            val = cells[3].text.split()
            amount, currency = val[0], val[-1]
            
            self.accounts[account_id] = {
                'id': account_id,
                'name': account_name,
                'amount': amount,
                'currency': currency
            }
   
    def get_accounts(self):
        return self.accounts.values()

    def get_transaction_history(self, account_id):
        assert account_id in self.accounts
        currency = self.accounts[account_id]['currency']
        self.open_page('CurrentAccount', PassedAccNum=account_id)

        form = self.content.find('form', action=re.compile('CurrentAccount'))
        transactions = []
        form.find('select').extract()
        
        for div in form.findAll('div', recursive=False):
            
            if currency in div.text:
                details_link = div.first('a', href=re.compile('parTransactionId'))
                if details_link:
                    details_link.extract()
                    transaction_id = self._get_params(details_link.get('href')).get('parTransactionId')[0]
                    x = self._get_params(details_link.get('href')).get('parTransactionId')[0]
                else:
                    transaction_id = ''
                
                contents = [el.string for el in div.firstText()]
                
                transaction = {
                    'id': transaction_id,
                    'date': contents[0].strip().strip(','),
                    'currency': currency,
                    'amount': contents[1],
                    'title': contents[-1],
                }
                transactions.append(transaction)
                
        return transactions                
        
        
    def get_transaction_details(self, transaction_id):
        pass
