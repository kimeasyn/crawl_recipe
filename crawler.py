import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://www.10000recipe.com"
url = f"{base_url}/recipe/list.html?q=쉬운요리"


def print_object(obj):
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


def main():
    response = requests.get(url)
    if response.status_code == 200:
        # BeautifulSoup 객체 생성
        soup = BeautifulSoup(response.text, 'html.parser')

        # 모든 class=common_sp_link인 <a> 태그 가져오기
        recipe_links = soup.find_all("a", class_="common_sp_link")

        # 각 레시피에 대한 정보 추출
        for idx, link in enumerate(recipe_links):
            recipe_soup = get_soup(link)
            obj = find_object(recipe_soup)
            obj['idx'] = idx + 1
            print_object(obj)
    else:
        print("웹페이지 가져오기 실패.")


if __name__ == "__main__":
    main()

