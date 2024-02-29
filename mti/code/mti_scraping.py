import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import json

df1 = pd.read_csv("../data/mti_urls.csv")

def scrape_and_compare(url1, url2):
    df1 = pd.read_csv(url1)
    try:
        response = requests.get(url2, timeout=(20, 15))
        response.raise_for_status()  
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    shows_list = soup.find_all(class_='region region-content')[0].find_all(class_='alphabetical-container')

    show_url = []

    for j in range(len(shows_list)):
        items = shows_list[j].find_all(class_='alphabetical-item')
        for i in range(len(items)):
            try:
                show_url.append((items[i].find('a', href=True))['href'])
            except:
                show_url.append(None)

    data = {
        'show_url': show_url
    }

    df2 = pd.DataFrame(data)

    new_urls = df1[]
    merged_df = df1.merge(df2, on='show_url', how='outer', indicator=True)

    not_common = merged_df[merged_df['_merge'] != 'both']

    remaining_urls = not_common['show_url']

    if len(remaining_urls) == 0:
        print("No new URLs found. Exiting without scraping.")
        return None
    else:
        print("Scraping data for new URLs...")
        print(len(remaining_urls))
        try:
            raw_data = scrape_data_for_urls(remaining_urls)
            print("trying to append the data to test csv")
            raw_data.to_csv("../data/mti_raw_data.csv", index=False, header = True)
            print("data appended to test csv")
            remaining_urls.to_csv(url1, mode='a', index=False, header=False)
            return remaining_urls
        except Exception as e:
            print("couldnot scrap the data", e)
            raise(e)
        
    
def scrape_data_for_urls(urls):
    raw_data = pd.DataFrame()

    show_title = []
    show_url = []
    brief_synopsis = []
    number_of_roles = []
    rating_of_show = []
    number_of_acts = []
    cast_size = []
    cast_type = []
    dance_requirement = []
    character_name = []
    character_description = []
    character_age = []
    character_gender = []
    logo_url = []
    characters_data = []
    song_data = []
    billing = []
    show_tags = []
    similar_shows = []
    resources = []
    video_warning = []
    award = []
    credits = []
    version = []
    full_synopsis = []
    synopsis_brief = []
    available_resource = []

    print("Inside scrape data for urls")
    for url in urls:
        try:
            individual_play_page = requests.get(url, timeout=(20, 10))

            individual_play_page_soup = BeautifulSoup(individual_play_page.content, 'html.parser')
            individual_play_print_page_link = individual_play_page_soup.find(class_='mti-print-button')
        except:
            print("couldnot get the response for inside page")

            continue
        
        songs = []
        songs_list = individual_play_page_soup.find_all(class_='field-name-field-show-songs')
        if len(songs_list) > 0:
            for song_name in songs_list:
                song = {
                    'song_title': song_name.find(class_='field-show-song-title').text,
                    'song_url': song_name.find('audio').find('source')['src']
                }
                songs.append(song)
            
            song_json = json.dumps(songs)
            song_data.append(song_json)
        else:
            song_data.append(None)
        

        tag = []
        tags = individual_play_page_soup.find(class_='group-tags').find_all(class_='field-type-taxonomy-term-reference')
        if len(tags) > 0:
            for i in range (len(tags)):
                tag.append(tags[i].text.strip())
            show_tags.append(tag)
        else:
            show_tags.append(None)

        show = []
        similar_shows_divs = individual_play_page_soup.find_all('div', class_='field-name-field-show-similar-shows')
        if len(similar_shows_divs) > 0:
            similar_show = {}
            for div in similar_shows_divs:
                show_name = div.a.text.strip()
                show_link = 'www.mtishows.com' + div.a['href']
                similar_show = {
                    'show_name': show_name,
                    'show_url': show_link
                }
                show.append(similar_show)

            similar_shows.append(show)
        else:
            similar_shows.append(None)

        show_version = individual_play_page_soup.find(class_='field-name-field-show-version')

        try:
            version.append(show_version.text.strip())
        except:
            version.append(None) 

        try:
            synopsis_brief.append(individual_play_page_soup.find(class_ = "field-name-field-show-synopsis-brief").text.strip())
        except:
            synopsis_brief.append(None)

        try:
            resource = individual_play_page_soup.find(class_="resource-results-view").find_all(class_="resource-results-view-content")
            resources_for_show = []
            for resource_item in resource:
                resource_link = resource_item.find('div', class_='resource-view-title').find('a')['href']
                resource_name = resource_item.find('div', class_='resource-view-title').text.strip()
                resource_description = resource_item.find('div', class_='resource-view-description').text.strip()
                resource_type = resource_item.find('div', class_='resource-view-type-wrapper').text.strip()
                resource_logo = resource_item.find('div', class_='resource-view-image').find('img')['src']

                resource_data = {
                    'resource_name': resource_name,
                    'resource_link': resource_link,
                    'resource_description': resource_description,
                    'resource_type': resource_type,
                    'resource_logo': resource_logo
                }

                resources_for_show.append(resource_data)

            available_resource.append(resources_for_show)
        except Exception as e:
            print('Error processing available resources:', e)
            available_resource.append(None)

        try:
            resources_link = individual_play_page_soup.find(class_='mti-show-materials')
        except:
            print("couldnot get response for resource link url")

        try:
            resources_link_request = requests.get('https://www.mtishows.com' + resources_link['href'], timeout=(20, 10))
            resources_page_soup = BeautifulSoup(resources_link_request.content, 'html.parser')
     
            header = resources_page_soup.find('h1')
            table = header.find_next('table', class_='table-styled')

            table_data_materials = []
            for row in table.find_all('tr'):
                columns = [col.text.strip() for col in row.find_all('td')]
                if len(columns) == 2:  
                    resource, quantity = columns
                    table_data_materials.append({"Resource": resource, "Quantity": quantity})

            headers = resources_page_soup.find_all('h3', string=['STANDARD ORCHESTRATION', 'ALTERNATE ORCHESTRATION'])

            table_data_orchestration = {}
            for header in headers:
                table = header.find_next('table', class_='table-styled')
                table_data = []
                for row in table.find_all('tr'):
                    columns = [col.text.strip() for col in row.find_all('td')]
                    if len(columns) == 3:  
                        instrumentation, doubling, quantity = columns
                        table_data.append({"Instrumentation": instrumentation, "Doubling": doubling, "Quantity": quantity})
                table_data_orchestration[header.text.strip()] = table_data

            data = {
                "Materials": table_data_materials,
                "Orchestration": table_data_orchestration
            }

            json_data = json.dumps(data, indent=4)

            resources.append(data)
            
        except:
            print("couldnot get 200 for resources link i.e no resource link button")
            resources.append(None)

        
        play_print_page_url = 'https://www.mtishows.com' +  individual_play_print_page_link['href']

        time.sleep(2)
        try:
            play_print_page_request = requests.get(play_print_page_url, timeout=(20, 10))
        except:
            print('Couldnot get the response for print page link')

        play_print_page_soup = BeautifulSoup(play_print_page_request.content, 'html.parser')


        try:
            title = play_print_page_soup.find(class_='field-name-field-show-title-full').text.strip()
            print(title)
            show_title.append(title)
        except:
            show_title.append(None)
        
        try:
            show_url.append(url)
        except:
            show_url.append(None)
            
        try:
            brief_synopsis.append(play_print_page_soup.find(class_='field-name-field-show-synopsis-summary').text.strip())
        except:
            brief_synopsis.append(None)
        
        try:
            number_of_roles.append(play_print_page_soup.find(class_='infographic__roles').text.strip())
        except:
            number_of_roles.append(None)
        
        try:
            rating_of_show.append(play_print_page_soup.find(class_='infographic__rated').find(class_='infographic__value').text.strip())
        except:
            rating_of_show.append(None)
            
        try:
            number_of_acts.append(play_print_page_soup.find(class_='infographic__acts').find(class_='infographic__value').text.strip())
        except:
            number_of_acts.append(None)
        
        try:
            cast_size.append(play_print_page_soup.find(class_='cast-info__name-size').text.split(': ')[1])
        except:
            cast_size.append(None)

        try:
            cast_type.append(play_print_page_soup.find(class_='cast-info__name-type').text.split(': ')[1])
        except:
            cast_type.append(None)

        try:
            dance_requirement.append(play_print_page_soup.find(class_='cast-info__name-requirements').text.split(': ')[1])
        except:
            dance_requirement.append(None)

        character_row_div = play_print_page_soup.find_all(class_='character__row')

        for row_div in character_row_div:
            try:
                character_name.append(row_div.find_previous_sibling('div').text)
            except:
                character_name.append(None)
            try:
                character_age.append(row_div.find(class_='character__age').text.split(': ')[1])
            except:
                character_age.append(None)
            try:
                character_gender.append(row_div.find(class_='character__gender').text.split(': ')[1])
            except:
                character_gender.append(None)

            try:    
                character_description.append(row_div.find(class_='character__description').text)
            except:
                character_description.append(None)


        try:
            video_warnings = play_print_page_soup.find(class_='show-billing__video-warning')
            warning_text = video_warnings.text.strip()
            warning_text = warning_text.replace('\n', '').replace('\r', '')
            warning_text = warning_text.replace('Video Warning', '', 1).strip()
            video_warning.append(warning_text)
        except:
            video_warning.append(None)
            
            
        try:
            logo_url.append(play_print_page_soup.find(class_='field-name-field-show-logo').find('img')['src'])
        except:
            logo_url.append(None)

        try:
            awards = play_print_page_soup.find(class_='show_awards_container')
            awards_data = {}
            awards_group  = awards.find_all(class_='show-awards__group')
            if len(awards_group) > 0:
                for group in awards_group:
                    award_type = group.find(class_='awards_type_group').text.strip()
                    awards_data[award_type] = []
                    for item in group.find_all(class_='awards__item'):
                        award_text = item.text.strip()
                        awards_data[award_type].append(award_text)
                award.append(awards_data)
            else:
                award.append(None)
        except:
            awards_data = None
            award.append(awards_data)

        try:
            characters = []
            if len(character_row_div) > 0:
                for row_div in character_row_div:
                    character = {
                        'Name': row_div.find_previous_sibling('div').text,
                        'Age': row_div.find(class_='character__age').text.split(': ')[1] if row_div.find(class_='character__age') else None,
                        'Gender': row_div.find(class_='character__gender').text.split(': ')[1] if row_div.find(class_='character__gender') else None,
                        'Description': row_div.find(class_='character__description').text
                    }
                    characters.append(character)

                characters_json = json.dumps(characters)
                characters_data.append(characters_json)
            else:
                characters_data.append(None)
        except:
            characters = None
            characters_data.append(characters)


        


        attributions = play_print_page_soup.find_all('div', class_='field-attribution-label')
        if len(attributions) > 0:
            billing_dict = {}

            for attribution in attributions:

                key = attribution.text.strip()

                value_div = attribution.find_next('div', class_='item-list')

                value = [item.text.strip() for item in value_div.find_all('a')]

                billing_dict[key] = value

            billing.append(billing_dict)
        else:
            billing.append(None)
        # Requirements (Credit)
        try:
            credit_requiements = play_print_page_soup.find(class_='show-billing__rider-wrapper')
            billing_requirements_text = credit_requiements.text.strip()
            cleaned_text = re.sub(r'\n+', ' ', billing_requirements_text)
            cleaned_text = re.sub(r'\xa0+', ' ', cleaned_text)
            cleaned_text = cleaned_text.replace('Requirements', '', 1).strip()
            credits.append(cleaned_text)
        except:
            credits.append(None)


        try:
            full_synopsis.append(play_print_page_soup.find(class_ = 'field-name-field-show-synopsis-long').text.strip())
        except:
            full_synopsis.append(None)
        
        
        

    data = {
        'show_title': show_title,
        'logo_url': logo_url,
        'show_url': show_url,
        'brief_synopsis': brief_synopsis,
        'dance_requirement': dance_requirement,
        'number_of_roles': number_of_roles,
        'rating_of_show': rating_of_show,
        'number_of_acts': number_of_acts,
        'cast_size': cast_size,
        'cast_type': cast_type,
        'characters': characters_data,
        'songs': song_data,
        'billing': billing,
        'tags': show_tags,
        'similar_shows': similar_shows,
        'orchestration_resources': resources,
        'video_warning': video_warning,
        'credit_requirements': credits,
        'awards': award,
        'version': version,
        'full_synopsis': full_synopsis,
        'available_resource': available_resource,
        'synopsis_brief': synopsis_brief
    }

    # print("Lengths - Show Title:", len(show_title), "Brief Synopsis:", len(brief_synopsis), "Number of Roles:", len(number_of_roles), "Rating of Show:", len(rating_of_show), "Number of Acts:", len(number_of_acts), "Cast Size:", len(cast_size), "Cast Type:", len(cast_type), "Dance Requirement:", len(dance_requirement), "Characters:", len([characters]), "Logo URL:", len(logo_url))

    df = pd.DataFrame(data)
    raw_data = raw_data._append(df, ignore_index=True)
    print("result data successfully appended.")

    return raw_data



if __name__ == "__main__":
    url1 = "../data/mti_urls.csv"
    url2 = "https://www.mtishows.com/shows/all"
    result = scrape_and_compare(url1, url2)

    if result is not None and len(result) > 0:
        print("Scrapping completed successfully.")

    else:
        print("No urls found.")
    
