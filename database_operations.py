import pandas.io.sql as sqlio
import pandas as pd
import numpy as np
from psycopg2 import *
from database_connection import DBConnection


class DatabaseOperations:
    def __init__(self):
        self.db_connection = DBConnection()
        self.groups_years_cache = {}

    def close_connection(self):
        self.db_connection.close_connection()

    def get_groups(self):
        get_groups_sql = """
            select distinct yg."name" 
            from fms_productapplied fp 
            join fms_field ff on ff.id = fp.field_id 
            join yagro_groups yg on yg.id = ff.group_id 
            order by yg."name" 
        """

        groups_df = sqlio.read_sql_query(
            get_groups_sql, self.db_connection.conn)

        return groups_df["name"].unique()

    def get_years_for_group(self, group):
        if group in self.groups_years_cache:
            return self.groups_years_cache[group]
        else:
            get_years_for_group_sql = """
                select distinct fp.harvest_year 
                from fms_productapplied fp 
                join fms_field ff on ff.id = fp.field_id 
                join yagro_groups yg on yg.id = ff.group_id 
                where yg."name" in ('{group}')
                order by fp.harvest_year 
            """.format(group=group)

            years_df = sqlio.read_sql_query(
                get_years_for_group_sql, self.db_connection.conn)
            years = years_df["harvest_year"].unique()
            self.groups_years_cache[group] = years
            return years

    def compare_products_with_rules(self, products):

        products = pd.DataFrame(products, columns=['product_name'])

        comparison_sql = """

                        select ir.serialised -> 'condition' -> 'when_all' -> 0 -> 'when' ->> 'value' as "product_name"
                        from ingestion_rule ir
                        join ingestion_ingestiontype ii on text(ii.id) = (ir.serialised ->> 'ingestion_type')
                        where ii."name" in ('Farm Products Used (Gatekeeper)');

                    """

        products_df = sqlio.read_sql(comparison_sql, self.db_connection.conn)

        # products_wo_rules = pd.merge(products, products_df, how='left', on='product_name')
        products_wo_rules = products_df["product_name"].to_list()

        products = products["product_name"].to_list()

        main_list = sorted(list(set(products) - set(products_wo_rules)))

        sep = "', '"
        main_list = [i[0:i.rfind(" (")].replace(
            "'", "") if " (" in i else i.replace("'", "") for i in main_list]
        list_of_no_rules = "'" + sep.join(main_list) + "'"

        product_name_compaison_sql = """
                        select yp."name" as "product_name"
                        from yagro_products yp
                        where yp."name" in ({})
                    """.format(list_of_no_rules)

        products_returned = sqlio.read_sql(
            product_name_compaison_sql, self.db_connection.conn)

        another_list = sorted(
            list(set(main_list) - set(products_returned["product_name"].to_list())))

        return another_list

    def do_farm_minmax_check(self, farm):

        farm_check_minmax_sql = """
                        SELECT
                            mins.harvest_year AS "Harvest year",
                            c.name AS "Crop",
                            i.name AS "Variety",
                            mins.cop::NUMERIC(32, 2) AS "Minimum CoP (£/t)",
                            gmin.name AS "Minimum grown by",
                            maxs.cop::NUMERIC(32, 2) AS "Maximum CoP (£/t)",
                            gmax.name AS "Maximum grown by"
                        FROM (
                            SELECT DISTINCT ON (harvest_year, variety_id)
                                harvest_year,
                                variety_id,
                                group_id,
                                "cost" / tonnage AS cop
                            FROM fms_costofproductiongroupvarietyyear
                            ORDER BY harvest_year, variety_id, "cost" / tonnage ASC
                        ) mins
                        JOIN (
                            select DISTINCT ON (harvest_year, variety_id)
                                harvest_year,
                                variety_id,
                                group_id,
                                "cost" / tonnage AS cop
                            FROM fms_costofproductiongroupvarietyyear
                            ORDER BY harvest_year, variety_id, "cost" / tonnage DESC
                        ) maxs
                            ON (mins.harvest_year, mins.variety_id) = (maxs.harvest_year, maxs.variety_id)
                        JOIN legacy_cropvariety cv
                            ON mins.variety_id = cv.id
                        JOIN yagro_crops c
                            ON cv.crop_id = c.id
                        JOIN yagro_ingredients i
                            ON cv.seed_id = i.id
                        JOIN yagro_groups gmin
                            ON mins.group_id = gmin.id
                        JOIN yagro_groups gmax
                            ON maxs.group_id = gmax.id
                        where gmin."name" in ('{farm}') or gmax."name" in ('{farm}')
                        ORDER BY mins.harvest_year DESC, c.name, i.name;
        """.format(farm=farm)

        min_max_df = sqlio.read_sql(
            farm_check_minmax_sql, self.db_connection.conn)

        return min_max_df

    def do_farm_apps_ings_check(self, farm):

        farm_check_apps_ings_sql = """
                    select distinct on (ff."name", fp.harvest_year) ff."name", fp.harvest_year,
                    yc2."name" as "Crop",
                    yi."name" as "Variety",
                    seed.seed_count,
                    seed_ing.seed_ing_count,
                    fert.fert_count,
                    fert_ing.fert_ing_count,
                    chem.chem_count,
                    chem_ing.chem_ing_count,
                    fy.value as "Yield"
                    from fms_productapplied fp
                    join fms_field ff on ff.id = fp.field_id 
                    join yagro_groups yg on yg.id = ff.group_id 
                    join legacy_cropvariety lc on lc.id = fp.variety_id 
                    join yagro_crops yc2 on yc2.id = lc.crop_id 
                    join yagro_ingredients yi on yi.id = lc.seed_id 
                    left join (
                        select distinct on (fp.field_id, fp.harvest_year) fp.field_id, fp.harvest_year, count(fp.product_id) as "seed_count"
                        from fms_productapplied fp
                        join yagro_products yp on yp.id = fp.product_id
                        where yp.cat_id = 5
                        group by fp.field_id, fp.harvest_year
                        order by fp.field_id, fp.harvest_year
                    ) seed on (seed.field_id, seed.harvest_year) = (fp.field_id, fp.harvest_year)
                    left join (
                        select distinct on (fiwa.field_id, fiwa.harvest_year) fiwa.field_id, fiwa.harvest_year, count(fiwa.category) as "seed_ing_count"
                        from fms_ingredientapplied_with_applied fiwa
                        join yagro_groups yg on yg.id = fiwa.group_id 
                        where fiwa.category in ('seed')
                        group by fiwa.field_id, fiwa.harvest_year
                        order by fiwa.field_id, fiwa.harvest_year 
                    ) seed_ing on (seed_ing.field_id, seed_ing.harvest_year) = (fp.field_id, fp.harvest_year)
                    left join (
                        select distinct on (fp.field_id, fp.harvest_year) fp.field_id, fp.harvest_year, count(fp.product_id) as "fert_count"
                        from fms_productapplied fp
                        join yagro_products yp on yp.id = fp.product_id
                        where yp.cat_id = 4
                        group by fp.field_id, fp.harvest_year
                        order by fp.field_id, fp.harvest_year
                    ) fert on (fert.field_id, fert.harvest_year) = (fp.field_id, fp.harvest_year)
                    left join (
                        select distinct on (fiwa.field_id, fiwa.harvest_year) fiwa.field_id, fiwa.harvest_year, count(fiwa.category) as "fert_ing_count"
                        from fms_ingredientapplied_with_applied fiwa
                        join yagro_groups yg on yg.id = fiwa.group_id 
                        where fiwa.category in ('fertiliser')
                        group by fiwa.field_id, fiwa.harvest_year
                        order by fiwa.field_id, fiwa.harvest_year 
                    ) fert_ing on (fert_ing.field_id, fert_ing.harvest_year) = (fp.field_id, fp.harvest_year)
                    left join (
                        select distinct on (fp.field_id, fp.harvest_year) fp.field_id, fp.harvest_year, count(fp.product_id) as "chem_count"
                        from fms_productapplied fp
                        join yagro_products yp on yp.id = fp.product_id
                        where yp.cat_id = 1
                        group by fp.field_id, fp.harvest_year
                        order by fp.field_id, fp.harvest_year
                    ) chem on (chem.field_id, chem.harvest_year) = (fp.field_id, fp.harvest_year)
                    left join (
                        select distinct on (fiwa.field_id, fiwa.harvest_year) fiwa.field_id, fiwa.harvest_year, count(fiwa.category) as "chem_ing_count"
                        from fms_ingredientapplied_with_applied fiwa
                        join yagro_groups yg on yg.id = fiwa.group_id 
                        where fiwa.category in ('fertiliser')
                        group by fiwa.field_id, fiwa.harvest_year
                        order by fiwa.field_id, fiwa.harvest_year 
                    ) chem_ing on (chem_ing.field_id, chem_ing.harvest_year) = (fp.field_id, fp.harvest_year)
                    left join fms_yield fy on (fy.field_id, fy.harvest_year) = (fp.field_id, fp.harvest_year)
                    join yagro_products yp on yp.id = fp.product_id 
                    join yagro_categories yc on yc.id = yp.cat_id 
                    where yg."name" in ('{farm}')
                    order by fp.harvest_year, ff."name"
        """.format(farm=farm)

        apps_ings_df = sqlio.read_sql(
            farm_check_apps_ings_sql, self.db_connection.conn)

        return apps_ings_df
