import traceback
import requests
from zedrunner_store import ZedRunnerStore
import argparse
import logging.config
import logging
from mapper import Mapper
from config import API_RETRY_COUNT

class ZedRun:

    def __init__(self, logger):
        self.mapper = Mapper()
        self.logger = logger
        self.store = ZedRunnerStore(logger)

    def make_api_calls(self,url, method, body=None, attempt=1):
        retry = API_RETRY_COUNT
        try:
            self.logger.debug(f"Calling '{url}' attempt:{attempt}")
            response = None
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response =  requests.post(url, json=body)
            self.logger.debug(f"StatusCode: {response.status_code}. Content: {response.text}")
            return response
            if response.status_code != 200:
                raise Exception(response.text)

            

        except Exception as e:
            attempt = attempt + 1
            if attempt <= retry:
                self.make_api_calls(url, method, body, attempt)
            else:
                self.logger.error("Retry attempts exceeded..")
                raise

    def fetch_race_data(self, forced=False):
        url = 'https://zed-ql.zed.run/graphql/'
        cursor = 'null'
        query ="""query{
        get_race_results(first:10, input: {only_my_racehorses: false, classes: [0,1,2,3,4,5]}, after: {0}) {
            edges {
            cursor
            node {
            country
            country_code
            city
            name
            length
            start_time
            fee
            race_id
            weather
            status
            class
            prize_pool {
                first
                second
                third
                total 
                }
            horses {
                horse_id 
                finish_time
                final_position
                name
                gate
                owner_address
                bloodline
                gender
                breed_type
                gen
                coat
                hex_color
                img_url
                class
                stable_name 
                } 
            }
            } 

            page_info {
                end_cursor
                has_next_page
            }
         }
            
        } """ 
        while True:
            after_query = query.replace('{0}',cursor)
            self.logger.info(f"Calling endpoint {url} with query: {after_query}")
            response = self.make_api_calls(url, method='POST', body={'query': after_query})
            self.logger.debug(f"Response: status_code: {response.status_code}, context: {response.text}")
            jsondata = response.json()
            self.logger.debug(jsondata)
            datas = jsondata['data']['get_race_results']['edges']

            cursor ='"'  + jsondata['data']['get_race_results']['page_info']['end_cursor'] + '"'

            has_next_page = jsondata['data']['get_race_results']['page_info']['has_next_page']

            data_set = self.mapper.map_race_data(datas)
            break_loop = True
            self.logger.debug("Last cursor is {cursor}")
            if forced or not self.store.race_exists(datas[0]):
                # store races data set
                self.logger.info("Storing races ...")
                self.store.store_races(data_set['races'])

                # store races data set
                self.logger.info("Storing races results...")
                self.store.store_races_result(data_set['races_results'])
                break_loop = False

            if  break_loop or not has_next_page:
                break
        
    def fetch_horse_data(self, forced=False):
        url = 'https://api.zed.run/api/v1/horses/roster?offset={0}&gen\[\]=1&gen\[\]=268&sort_by=created_by_desc'
        offset = 0
        while True:
            current_url = url.format(offset)
            self.logger.info(f"Calling endpoint: {current_url}")
            response = self.make_api_calls(current_url, method='GET')
            jsondata =response.json()
            self.logger.debug(f"Response from api: {jsondata}")
            break_loop = True
            count = len(jsondata)
            if count == 0:
                break

            offset = offset + count
            first_horse = jsondata[0]
            
            #self.logger.info(jsondata)

            if forced or not self.store.horse_exists(first_horse):
                horse_datas = self.mapper.map_horses_data(jsondata)
                self.logger.info('Store horses information to database.')
                self.store.store_horses(horse_datas)
                break_loop = False

            if break_loop:
                break

    def fetch_stable_data(self,forced=False):
        datas = self.store.distinct_owner_address()
        list_address = [d[0] for d in datas]

        url = 'https://api.zed.run/api/v1/horses/get_user_horses?public_address={0}&offset={1}&gen\[\]=1&gen\[\]=268&sort_by=created_by_desc'
        for address in list_address:
            self.logger.info(f"Fetching stable information for address {address}")
            offset = 0
            while True:
                current_url = url.format(address, offset)
                self.logger.info(f"Calling endpoint: {current_url}")
                response = self.make_api_calls(current_url,method='GET')
                jsondata =response.json()
                self.logger.debug(f"Response from api: {jsondata}")
                break_loop = True
                count = len(jsondata)
                if count == 0:
                    break

                offset = offset + count
                first_horse = jsondata[0]

                if forced or not self.store.stable_exists(first_horse):
                    horse_datas = self.mapper.map_stable_data(jsondata)
                    #horse_datas = self.mapper.map_horses_data(jsondata)
                    self.logger.info('Store stable information to database.')
                    self.store.store_stables(horse_datas)
                    break_loop = False

                if break_loop:
                    break

    def fetch_offspring_data(self,forced=False):
        datas = self.store.get_horse_ids()
        # horse_ids = [d[0] for d in datas]
        # type = [d[1] for d in datas]
        
        url = 'https://api.zed.run/api/v1/horses/offsprings/{0}'
        for parent_id, type in datas:
            self.logger.info(f"Fetching offspring information for horse id: {parent_id} of type {type}")
            current_url = url.format(parent_id)
            self.logger.info(f"Calling endpoint: {current_url}")
            try:
                response = self.make_api_calls(current_url,method='GET')
                child_datas=response.json()
                self.logger.debug(f"Response from api: {child_datas}")

                self.store.store_offspring(parent_id, child_datas, type)
                self.logger.info('Store offspring information to database.')
            except Exception as e:
                self.logger.info('Offspring fetch error:', e)



def main(type, forced):
    logging.config.fileConfig('logging.conf')
    message = f"Zed Run with settings Type:'{type}' and Forced: {forced}"
    logger = logging.getLogger('zedrunner')
    try:
        if(type not in ['horse', 'race', 'stable', 'offspring']):
            print(f"'{type}' is not supported")
            return

        logger.info(f"Starting {message}")

        run = ZedRun(logger)
        if(type == 'horse'):
            run.fetch_horse_data(forced)
        elif(type == 'race'):
            run.fetch_race_data(forced)
        elif(type == 'stable'):
            run.fetch_stable_data(forced)
        elif(type == 'offspring'):
            run.fetch_offspring_data(forced)

        success_message = message + " completed successfully."
        logger.info(success_message)
    except Exception as e:       
        failure_message = message + ' failed.'
        stacktrace = traceback.format_exc()
        logger.error(f"Error: {failure_message} Reason: {stacktrace}")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    # Add arguments to parser
    ap.add_argument("-t","--type", required=True, help="type can be horse, race or stable")
    ap.add_argument('-f', '--force', required=False, help="Force and restore cache")
    args = vars(ap.parse_args())
    type = args['type']
    force_string = args['force'] or 'False'
    forced = force_string.lower() in ['true', 't']
    main(type, forced)
