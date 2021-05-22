class Mapper:
    def map_race_data(self,race_data):
        return_races = []
        return_races_results = []

        for d in race_data:
            # races tuple
            node = d['node']
            horses = node['horses']

            city = node['city']
            c = node['class']
            country_code = node["country_code"]
            fee = node["fee"]
            length= node["length"]
            name=node["name"] 
            prizepool_first= node['prize_pool']['first']
            prizepool_second = node['prize_pool']["second"]
            prizepool_third = node['prize_pool']["third"]
            prizepool_total = node["prize_pool"]["total"]
            race_id=   node['race_id']
            start_time = node["start_time"]
            status = node["status"]
            weather = node["weather"]

            return_races.append((city, c, country_code , fee , length, name, prizepool_first, prizepool_second, prizepool_third , prizepool_total , race_id,
                start_time , status , weather ))

            # races_result tuple
            for horse in horses:
                horse_id = horse['horse_id']
                finish_time = horse['finish_time']
                final_position = horse['final_position']
                name = horse['name']
                gate = horse['gate']
                owner_address = horse['owner_address']
                bloodline = horse['bloodline']
                gender = horse['gender']
                breed_type = horse['breed_type']
                gen = horse['gen']
                races = horse['races']
                coat = horse['coat']
                win_rate = horse['win_rate']
                career = horse['career']
                hex_color = horse['hex_color']
                img_url = horse['img_url']
                horse_class = horse['class']
                stable_name = horse['stable_name']
                return_races_results.append(( race_id, horse_id ,
                                    finish_time , final_position ,
                                    name , gate , owner_address ,
                                    bloodline , gender , breed_type ,
                                    gen , races , coat , win_rate ,
                                    career , hex_color , img_url ,
                                    horse_class , stable_name ))

        return {"races": return_races, "races_results": return_races_results }




    def map_horses_data(self, horse_datas):
        return_datas = []
        for d in horse_datas:
            bloodline = d['bloodline']
            breed_type = d['breed_type']
            career_first = d['career']['first']
            career_second = d['career']['second']
            career_third  = d['career']['third']
            genotype = d['genotype']
            hashinfo_color = d['hash_info']['color']
            hashinfo_hexcode = d['hash_info']['hex_code']
            hashinfo_name=d['hash_info']['name']
            horse_id=d['horse_id']
            horse_type= d['horse_type']
            img_url=d['img_url']
            number_of_races= d['number_of_races']
            owner= d['owner']
            super_coat= d['super_coat']
            tx= d['tx']
            tx_date =d['tx_date']
            win_rate=d['win_rate']

            return_datas.append((bloodline , breed_type ,
                career_first , career_second , career_third, genotype ,
                hashinfo_color , hashinfo_hexcode , hashinfo_name, horse_id,
                horse_type, img_url, number_of_races, owner, super_coat, tx, tx_date , win_rate
                ))

        return return_datas
