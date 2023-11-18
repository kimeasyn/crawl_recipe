import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://www.10000recipe.com"


def print_object(obj):
    print("Page: ", obj['page'])
    print("No: ", obj['idx'])
    # print("url: ", obj['relative_url'])
    print("이미지 URL:", obj['img_url'])
    print("레시피 제목:", obj['recipe_title'])
    print("재료 목록:", obj['ingredient_list'])
    print("양념 목록:", obj['seasoning_list'])
    print("순서: ")
    for i, s in enumerate(obj['steps']):
        print(i + 1, ". ", s)
    print("\n")


def get_soup(link):
    relative_url = link.get("href")

    # 상대 URL을 절대 URL로 변환
    recipe_url = urljoin(base_url, relative_url)
    recipe_response = requests.get(recipe_url)

    soup = None
    if recipe_response.status_code == 200:
        soup = BeautifulSoup(recipe_response.text, 'html.parser')

    return soup


def find_object(recipe_soup):
    img_tag = recipe_soup.find("a", class_="common_sp_link").find("img")
    img_url = img_tag["src"] if img_tag else ""

    # 레시피 제목
    recipe_title = recipe_soup.find("h3").get_text()

    # 재료 목록이 있는 HTML 요소 선택
    wrapper = recipe_soup.find("div", class_="ready_ingre3")
    ul_elements = wrapper.find_all("ul")

    ingredient_list = []
    seasoning_list = []
    for ul in ul_elements:
        name = ul.find('b')
        if name.text[1:3] == '재료':
            li_elements = ul.find_all("li")
            for li in li_elements:
                ingredient_name = li.contents[0].strip()
                ingredient_amt = li.find('span').text
                ingredient_list.append({
                    'name': ingredient_name,
                    'amt': ingredient_amt
                })
        elif name.text[1:3] == '양념':
            li_elements = ul.find_all("li")
            for li in li_elements:
                seasoning_name = li.contents[0].strip()
                seasoning_amt = li.find('span').text
                seasoning_list.append({
                    'name': seasoning_name,
                    'amt': seasoning_amt
                })

    steps = []
    step_wrapper = recipe_soup.find("div", class_="view_step")
    view_steps = step_wrapper.find_all("div", class_="media-body")
    for step in view_steps:
        steps.append(step.text)

    # 결과 출력
    obj = {
        # 'relative_url': relative_url,
        'img_url': img_url,
        'recipe_title': recipe_title,
        'ingredient_list': ingredient_list,
        'seasoning_list': seasoning_list,
        'steps': steps
    }

    return obj


def get_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response
    else:
        return None


def main():
    url = f"{base_url}/recipe/list.html?q=쉬운요리"
    response = get_content(url)
    cnt = 1
    while response:
        if response.status_code == 200:
            # 첫 페이지 BeautifulSoup 객체 생성
            soup = BeautifulSoup(response.text, 'html.parser')
            # pagination 정보 get
            pagination_class = soup.find("ul", class_="pagination")
            pages = pagination_class.find_all('a')
            is_continue = True
            while is_continue:
                for page_link in pages:
                    page_url = base_url + page_link["href"]
                    if page_link.text.isnumeric():
                        current_page = int(page_link.text)
                        if current_page > 1:
                            soup = BeautifulSoup(response.text, 'html.parser')
                        recipe_links = soup.find_all("a", class_="common_sp_link")

                        # 각 레시피에 대한 정보 추출 및 출력
                        for idx, link in enumerate(recipe_links):
                            recipe_soup = get_soup(link)
                            obj = find_object(recipe_soup)
                            print(cnt)
                            obj['idx'] = idx + 1
                            obj['page'] = current_page
                            print_object(obj)
                            cnt += 1
                    else:
                        response = get_content(page_url)
                        is_continue = False
                if len(pages) < 11:
                    response = None


if __name__ == "__main__":
    main()

