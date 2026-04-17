from typing import Final

BASE_URL: Final = "https://www.worldometers.info"
RTS_INIT_URL: Final = "https://www.realtimestatistics.net/rts/init.php"

TABLE_CACHE_TTL_SECONDS: Final = 1800
LIVE_CACHE_TTL_SECONDS: Final = 10

LIVE_COUNTER_MAP: Final[dict[str, dict[str, str]]] = {
    "world_population": {
        "current_population": "current_population",
        "births_today": "births_today",
        "births_this_year": "births_this_year",
        "deaths_today": "dth1s_today",
        "deaths_this_year": "dth1s_this_year",
        "net_population_growth_today": "absolute_growth",
        "net_population_growth_this_year": "absolute_growth_year",
    },
    "government_and_economics": {
        "public_healthcare_expenditure_today": "gov_expenditures_health/today",
        "public_education_expenditure_today": "gov_expenditures_education/today",
        "public_military_expenditure_today": "gov_expenditures_military/today",
        "cars_produced_this_year": "automobile_produced/this_year",
        "bicycles_produced_this_year": "bicycle_produced/this_year",
        "computers_produced_this_year": "computers_sold/this_year",
    },
    "society_and_media": {
        "new_book_titles_published_this_year": "books_published/this_year",
        "newspapers_circulated_today": "newspapers_circulated/today",
        "tv_sets_sold_worldwide_today": "tv/today",
        "cellular_phones_sold_today": "cellular/today",
        "money_spent_on_videogames_today": "videogames/today",
        "internet_users_in_the_world_today": "internet_users",
        "emails_sent_today": "em/today",
        "blog_posts_written_today": "blog_posts/today",
        "tweets_sent_today": "tweets/today",
        "google_searches_today": "google_searches/today",
    },
    "environment": {
        "forest_loss_this_year": "forest_loss/this_year",
        "land_lost_to_soil_erosion_this_year": "soil_erosion/this_year",
        "co2_emissions_this_year": "co2_emissions/this_year",
        "desertification_this_year": "desert_land_formed/this_year",
        "toxic_chemicals_released_in_the_environment_this_year": "tox_chem/this_year",
    },
    "food": {
        "undernourished_people_in_the_world": "undernourished",
        "overweight_people_in_the_world": "overweight",
        "obese_people_in_the_world": "obese",
        "people_who_died_of_hunger_today": "dth1_hunger/today",
        "money_spent_for_obesity_related_diseases_in_the_usa_today": "obesity_spending/today",
        "money_spent_on_weight_loss_programs_in_the_usa_today": "spending_on_weight_loss/today",
    },
    "water": {
        "water_used_this_year": "water_consumed/this_year",
        "deaths_caused_by_water_related_diseases_this_year": "water_disax/this_year",
        "people_with_no_access_to_a_safe_drinking_water_source": "nowater_population",
    },
    "energy": {
        "energy_used_today": "energy_used/today",
        "non_renewable_sources": "energy_nonren/today",
        "renewable_sources": "energy_ren/today",
        "solar_energy_striking_earth_today": "solar_energy/today",
        "oil_pumped_today": "oil_consumption/today",
        "oil_left": "oil_reserves",
        "days_to_the_end_of_oil": "oil_days",
        "natural_gas_left": "gas_reserves",
        "days_to_the_end_of_natural_gas": "gas_days",
        "coal_left": "coal_reserves",
        "days_to_the_end_of_coal": "coal_days",
    },
    "health": {
        "communicable_disease_deaths_this_year": "dth1s_communicable_disaxs/this_year",
        "seasonal_flu_deaths_this_year": "dth1s_flu/this_year",
        "deaths_of_children_under_5_this_year": "dth1s_children/this_year",
        "abortions_this_year": "ab/this_year",
        "deaths_of_mothers_during_birth_this_year": "dth1s_maternal/this_year",
        "hiv_aids_infected_people": "infections_hiv",
        "deaths_caused_by_hiv_aids_this_year": "dth1s_ads/this_year",
        "deaths_caused_by_cancer_this_year": "dth1s_cancer/this_year",
        "deaths_caused_by_malaria_this_year": "dth1s_malarial/this_year",
        "cigarettes_smoked_today": "cigarettes_smoked/today",
        "deaths_caused_by_smoking_this_year": "dth1s_cigarettes/this_year",
        "deaths_caused_by_alcohol_this_year": "dth1s_alchool/this_year",
        "suicides_this_year": "sui/this_year",
        "money_spent_on_illegal_drugs_this_year": "drug_spending/this_year",
        "road_traffic_accident_fatalities_this_year": "dth1s_cars/this_year",
    },
}

TABLE_ROUTES: Final[dict[str, tuple[str, int]]] = {
    "/api/country-codes": ("/country-codes/", 0),
    "/api/population/countries": ("/world-population/population-by-country/", 0),
    "/api/population/largest-cities": ("/population/largest-cities-in-the-world/", 0),
    "/api/population/by-year": ("/world-population/world-population-by-year/", 0),
    "/api/population/projections": ("/world-population/world-population-projections/", 0),
    "/api/geography/largest-countries": ("/geography/largest-countries-in-the-world/", 0),
    "/api/geography/world-countries": ("/geography/how-many-countries-are-there-in-the-world/", 0),
}

POPULATION_PERIOD_TABLE_INDEX: Final[dict[str, int]] = {
    "current": 0,
    "past": 1,
    "future": 2,
}

REGION_POPULATION_DATASET_INDEX: Final[dict[str, int]] = {
    "subregions": 0,
    "historical": 1,
    "forecast": 2,
}

GEOGRAPHY_REGION_DATASET_INDEX: Final[dict[str, int]] = {
    "countries": 0,
    "dependencies": 1,
}

REGION_GEOGRAPHY_PATHS: Final[dict[str, str]] = {
    "asia": "/geography/how-many-countries-in-asia/",
    "africa": "/geography/how-many-countries-in-africa/",
    "europe": "/geography/how-many-countries-in-europe/",
    "latin-america": "/geography/how-many-countries-in-latin-america/",
    "northern-america": "/geography/how-many-countries-in-northern-america/",
    "oceania": "/geography/how-many-countries-in-oceania/",
}

REGION_POPULATION_PATHS: Final[dict[str, str]] = {
    "asia": "/world-population/asia-population/",
    "africa": "/world-population/africa-population/",
    "europe": "/world-population/europe-population/",
    "latin-america": "/world-population/latin-america-and-the-caribbean-population/",
    "northern-america": "/world-population/northern-america-population/",
    "oceania": "/world-population/oceania-population/",
}

REGION_ALIASES: Final[dict[str, str]] = {
    "latin_america": "latin-america",
    "latin-america-and-the-caribbean": "latin-america",
    "latin-america-and-caribbean": "latin-america",
    "north-america": "northern-america",
    "northern_america": "northern-america",
}

SECONDS_NAME_ALIASES: Final[dict[str, str]] = {
    "population_measure": "may4",
    "previous_year": "ye",
    "occ": "occupazione",
    "cell": "celldate",
}

ROOT_ROUTES: Final[list[str]] = [
    "/",
    "/docs",
    "/api",
    "/openapi.json",
    "/api/live",
    "/api/country-codes",
    "/api/population/countries",
    "/api/population/most-populous?period=current|past|future",
    "/api/population/largest-cities",
    "/api/population/by-region?period=current|past|future",
    "/api/population/by-year",
    "/api/population/projections",
    "/api/population/region/{region}?dataset=subregions|historical|forecast",
    "/api/geography/largest-countries",
    "/api/geography/world-countries",
    "/api/geography/region/{region}?dataset=countries|dependencies",
]
