from typing import Final

BASE_URL: Final = "https://www.worldometers.info"
RTS_INIT_URL: Final = "https://www.realtimestatistics.net/rts/init.php"

TABLE_CACHE_TTL_SECONDS: Final = 1800
LIVE_CACHE_TTL_SECONDS: Final = 10
COUNTRY_LOOKUP_CACHE_TTL_SECONDS: Final = 1800

COUNTRY_CODES_SOURCE_PATH: Final = "/country-codes/"
POPULATION_BY_COUNTRY_SOURCE_PATH: Final = "/world-population/population-by-country/"
POPULATION_LARGEST_CITIES_SOURCE_PATH: Final = "/population/largest-cities-in-the-world/"
POPULATION_BY_YEAR_SOURCE_PATH: Final = "/world-population/world-population-by-year/"
POPULATION_PROJECTIONS_SOURCE_PATH: Final = "/world-population/world-population-projections/"
GEOGRAPHY_LARGEST_COUNTRIES_SOURCE_PATH: Final = "/geography/largest-countries-in-the-world/"
GEOGRAPHY_WORLD_COUNTRIES_SOURCE_PATH: Final = "/geography/how-many-countries-are-there-in-the-world/"
ENERGY_OVERVIEW_SOURCE_PATH: Final = "/energy/"
WATER_OVERVIEW_SOURCE_PATH: Final = "/water/"
WATER_COUNTRY_SOURCE_TEMPLATE: Final = "/water/{country_slug}-water/"
GDP_BY_COUNTRY_SOURCE_PATH: Final = "/gdp/gdp-by-country/"
GDP_PER_CAPITA_SOURCE_PATH: Final = "/gdp/gdp-per-capita/"
FOOD_AGRICULTURE_UNDERNOURISHMENT_SOURCE_PATH: Final = "/undernourishment/"
FOOD_AGRICULTURE_FOREST_SOURCE_PATH: Final = "/food-agriculture/forest-by-country/"
FOOD_AGRICULTURE_CROPLAND_SOURCE_PATH: Final = "/food-agriculture/cropland-by-country/"
FOOD_AGRICULTURE_PESTICIDES_SOURCE_PATH: Final = "/food-agriculture/pesticides-by-country/"
GHG_GREENHOUSE_OVERVIEW_SOURCE_PATH: Final = "/greenhouse-gas-emissions/"
GHG_GREENHOUSE_BY_COUNTRY_SOURCE_PATH: Final = (
    "/greenhouse-gas-emissions/greenhouse-gas-emissions-by-country/"
)
GHG_GREENHOUSE_BY_YEAR_SOURCE_PATH: Final = (
    "/greenhouse-gas-emissions/greenhouse-gas-emissions-by-year/"
)
GHG_GREENHOUSE_PER_CAPITA_SOURCE_PATH: Final = (
    "/greenhouse-gas-emissions/greenhouse-gas-emissions-per-capita/"
)
GHG_CO2_OVERVIEW_SOURCE_PATH: Final = "/co2-emissions/"
GHG_CO2_BY_COUNTRY_SOURCE_PATH: Final = "/co2-emissions/co2-emissions-by-country/"
GHG_CO2_BY_YEAR_SOURCE_PATH: Final = "/co2-emissions/co2-emissions-by-year/"
GHG_CO2_PER_CAPITA_SOURCE_PATH: Final = "/co2-emissions/co2-emissions-per-capita/"
MAPS_OVERVIEW_SOURCE_PATH: Final = "/maps/"

ENERGY_COUNTRY_DATASET_SOURCE_TEMPLATES: Final[dict[str, str]] = {
    "energy": "/energy/{country_slug}-energy/",
    "electricity": "/electricity/{country_slug}-electricity/",
    "gas": "/gas/{country_slug}-natural-gas/",
    "oil": "/oil/{country_slug}-oil/",
    "coal": "/coal/{country_slug}-coal/",
}

ENERGY_COUNTRY_DATASET_CHOICES: Final[dict[str, int]] = {
    "all": 0,
    "energy": 1,
    "electricity": 2,
    "gas": 3,
    "oil": 4,
    "coal": 5,
}

GDP_DATASET_CHOICES: Final[dict[str, int]] = {
    "by-country": 0,
    "per-capita": 1,
}

FOOD_AGRICULTURE_DATASET_CHOICES: Final[dict[str, int]] = {
    "undernourishment": 0,
    "forest": 1,
    "cropland": 2,
    "pesticides": 3,
}

GHG_COUNTRY_DATASET_CHOICES: Final[dict[str, int]] = {
    "all": 0,
    "greenhouse": 1,
    "co2": 2,
}

MAPS_TYPE_CHOICES: Final[dict[str, int]] = {
    "all": 0,
    "physical": 1,
    "political": 2,
    "road": 3,
    "locator": 4,
}

GDP_COUNTRY_SOURCE_INDEX_PATHS: Final[list[str]] = [
    GDP_BY_COUNTRY_SOURCE_PATH,
    GDP_PER_CAPITA_SOURCE_PATH,
]

FOOD_AGRICULTURE_COUNTRY_SOURCE_INDEX_PATHS: Final[list[str]] = [
    FOOD_AGRICULTURE_UNDERNOURISHMENT_SOURCE_PATH,
    FOOD_AGRICULTURE_FOREST_SOURCE_PATH,
    FOOD_AGRICULTURE_CROPLAND_SOURCE_PATH,
    FOOD_AGRICULTURE_PESTICIDES_SOURCE_PATH,
]

GHG_GREENHOUSE_COUNTRY_SOURCE_INDEX_PATHS: Final[list[str]] = [
    GHG_GREENHOUSE_BY_COUNTRY_SOURCE_PATH,
    GHG_GREENHOUSE_PER_CAPITA_SOURCE_PATH,
]

GHG_CO2_COUNTRY_SOURCE_INDEX_PATHS: Final[list[str]] = [
    GHG_CO2_BY_COUNTRY_SOURCE_PATH,
    GHG_CO2_PER_CAPITA_SOURCE_PATH,
]

MAPS_COUNTRY_SOURCE_INDEX_PATHS: Final[list[str]] = [
    MAPS_OVERVIEW_SOURCE_PATH,
]

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
    "population/country-codes": (COUNTRY_CODES_SOURCE_PATH, 0),
    "population/countries": (POPULATION_BY_COUNTRY_SOURCE_PATH, 0),
    "population/largest-cities": (POPULATION_LARGEST_CITIES_SOURCE_PATH, 0),
    "population/by-year": (POPULATION_BY_YEAR_SOURCE_PATH, 0),
    "population/projections": (POPULATION_PROJECTIONS_SOURCE_PATH, 0),
    "geography/largest-countries": (GEOGRAPHY_LARGEST_COUNTRIES_SOURCE_PATH, 0),
    "geography/world-countries": (GEOGRAPHY_WORLD_COUNTRIES_SOURCE_PATH, 0),
    "energy/overview": (ENERGY_OVERVIEW_SOURCE_PATH, 0),
    "water/overview": (WATER_OVERVIEW_SOURCE_PATH, 0),
    "gdp/by-country": (GDP_BY_COUNTRY_SOURCE_PATH, 0),
    "gdp/per-capita": (GDP_PER_CAPITA_SOURCE_PATH, 0),
    "food-agriculture/undernourishment": (FOOD_AGRICULTURE_UNDERNOURISHMENT_SOURCE_PATH, 0),
    "food-agriculture/forest": (FOOD_AGRICULTURE_FOREST_SOURCE_PATH, 0),
    "food-agriculture/cropland": (FOOD_AGRICULTURE_CROPLAND_SOURCE_PATH, 0),
    "food-agriculture/pesticides": (FOOD_AGRICULTURE_PESTICIDES_SOURCE_PATH, 0),
    "ghg-emissions/greenhouse/overview": (GHG_GREENHOUSE_OVERVIEW_SOURCE_PATH, 0),
    "ghg-emissions/greenhouse/by-country": (GHG_GREENHOUSE_BY_COUNTRY_SOURCE_PATH, 0),
    "ghg-emissions/greenhouse/by-year": (GHG_GREENHOUSE_BY_YEAR_SOURCE_PATH, 0),
    "ghg-emissions/greenhouse/per-capita": (GHG_GREENHOUSE_PER_CAPITA_SOURCE_PATH, 0),
    "ghg-emissions/co2/overview": (GHG_CO2_OVERVIEW_SOURCE_PATH, 0),
    "ghg-emissions/co2/by-country": (GHG_CO2_BY_COUNTRY_SOURCE_PATH, 0),
    "ghg-emissions/co2/by-year": (GHG_CO2_BY_YEAR_SOURCE_PATH, 0),
    "ghg-emissions/co2/per-capita": (GHG_CO2_PER_CAPITA_SOURCE_PATH, 0),
    "maps/overview": (MAPS_OVERVIEW_SOURCE_PATH, 0),
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
    "/live",
    "/population/country-codes",
    "/population/countries",
    "/population/most-populous?period=current|past|future",
    "/population/largest-cities",
    "/population/by-region?period=current|past|future",
    "/population/by-year",
    "/population/projections",
    "/population/region/{region}?dataset=subregions|historical|forecast",
    "/population/country/{countryIdentifier}",
    "/geography/largest-countries",
    "/geography/world-countries",
    "/geography/region/{region}?dataset=countries|dependencies",
    "/energy",
    "/energy/country/{countryIdentifier}?dataset=all|energy|electricity|gas|oil|coal",
    "/water",
    "/water/country/{countryIdentifier}",
    "/gdp?dataset=by-country|per-capita&source=imf|wb&region={region}&year={yyyy}&metric=nominal|ppp",
    "/gdp/country/{countryIdentifier}",
    "/food-agriculture?dataset=undernourishment|forest|cropland|pesticides",
    "/food-agriculture/undernourishment",
    "/food-agriculture/forest",
    "/food-agriculture/cropland",
    "/food-agriculture/pesticides",
    "/food-agriculture/country/{countryIdentifier}",
    "/ghg-emissions",
    "/ghg-emissions/greenhouse",
    "/ghg-emissions/greenhouse/by-country",
    "/ghg-emissions/greenhouse/by-year",
    "/ghg-emissions/greenhouse/per-capita",
    "/ghg-emissions/co2",
    "/ghg-emissions/co2/by-country",
    "/ghg-emissions/co2/by-year",
    "/ghg-emissions/co2/per-capita",
    "/ghg-emissions/country/{countryIdentifier}?dataset=all|greenhouse|co2",
    "/maps",
    "/maps/country/{countryIdentifier}",
    "/maps/physical/{countryIdentifier}",
    "/maps/political/{countryIdentifier}",
    "/maps/road/{countryIdentifier}",
    "/maps/locator/{countryIdentifier}",
]
