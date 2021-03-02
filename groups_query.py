import pandas.io.sql as sqlio
import pandas as pd
from psycopg2 import *

class Groups:
    def __init__(self):
        self.years_cache = {}
        pass

    def get_groups(self, conn):
        get_groups_sql = """
            select distinct yg."name" 
            from fms_productapplied fp 
            join fms_field ff on ff.id = fp.field_id 
            join yagro_groups yg on yg.id = ff.group_id 
            order by yg."name" 
        """

        groups_df = sqlio.read_sql_query(get_groups_sql, conn)
        
        return groups_df["name"].unique()

    def get_years_for_group(self, conn, group):
        if group in self.years_cache:
            print("returning from cache")
            return self.years_cache[group]
        else:
            get_years_for_group_sql = """
                select distinct fp.harvest_year 
                from fms_productapplied fp 
                join fms_field ff on ff.id = fp.field_id 
                join yagro_groups yg on yg.id = ff.group_id 
                where yg."name" in ('{group}')
                order by fp.harvest_year 
            """.format(group=group)

            years_df = sqlio.read_sql_query(get_years_for_group_sql, conn)
            years = years_df["harvest_year"].unique()
            self.years_cache[group] = years
            print("returning from new query")
            return years
