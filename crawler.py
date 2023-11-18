import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 기본 URL 설정
base_url = "https://www.10000recipe.com"

# 웹페이지 URL 설정
url = f"{base_url}/recipe/list.html?q=쉬운요리"

# 웹페이지 가져오기
response = requests.get(url)
if response.status_code == 200:
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(response.text, 'html.parser')

    # 모든 class=common_sp_link인 <a> 태그 가져오기
    recipe_links = soup.find_all("a", class_="common_sp_link")

    # 각 레시피에 대한 정보 추출
    for idx, link in enumerate(recipe_links):
        if idx > 3:
            break
        relative_url = link.get("href")

        # 상대 URL을 절대 URL로 변환
        recipe_url = urljoin(base_url, relative_url)

        # 레시피 페이지로 이동하여 데이터 수집
        recipe_response = requests.get(recipe_url)
        if recipe_response.status_code == 200:
            recipe_soup = BeautifulSoup(recipe_response.text, 'html.parser')

            # 이미지 URL 찾기
            img_tag = recipe_soup.find("a", class_="common_sp_link").find("img")
            img_url = img_tag["src"] if img_tag else ""

            # 레시피 제목
            recipe_title = recipe_soup.find("h3").get_text()

            # 재료 목록
            soup = BeautifulSoup(response.text, 'html.parser')

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
            print("url: ", relative_url)
            print("이미지 URL:", img_url)
            print("레시피 제목:", recipe_title)
            print("재료 목록:", ingredient_list)
            print("양념 목록:", seasoning_list)
            print("순서: ")
            for i, s in enumerate(steps):
                print(i+1, ". ", s)
            print("\n")

else:
    print("웹페이지 가져오기 실패.")
