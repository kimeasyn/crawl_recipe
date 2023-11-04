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
    for link in recipe_links:
        # 상대 URL 추출
        relative_url = link.get("href")

        # 상대 URL을 절대 URL로 변환
        recipe_url = urljoin(base_url, relative_url)

        # 레시피 페이지로 이동하여 데이터 수집
        recipe_response = requests.get(recipe_url)
        if recipe_response.status_code == 200:
            recipe_soup = BeautifulSoup(recipe_response.text, 'html.parser')

            # 이미지 URL 찾기
            img_tag = recipe_soup.find("a", class_="common_sp_link").find("img")
            img_url = img_tag["src"] if img_tag else "이미지 없음"

            # 레시피 제목
            recipe_title = recipe_soup.find("h3").get_text()

            # 재료 목록
            ingredients = recipe_soup.find_all("div", class_="ready_ingre3")
            ingredient_list = []
            for ingredient in ingredients:
                ingredient_name = ingredient.find("a", class_="link_recipe").get_text()
                ingredient_quantity = ingredient.find("div", class_="infor")
                ingre_unit = ingredient_quantity.find("span", class_="cate").get_text()
                ingre_quantity = ingredient_quantity.find("span", class_="qty").get_text()
                ingredient_list.append(f"{ingredient_name} - {ingre_quantity} {ingre_unit}")

            # 양념 목록
            seasonings = recipe_soup.find_all("div", class_="ready_ingre3_1")
            seasoning_list = [seasoning.get_text() for seasoning in seasonings]

            # 결과 출력
            print("이미지 URL:", img_url)
            print("레시피 제목:", recipe_title)
            print("재료 목록:")
            for ingredient in ingredient_list:
                print(ingredient)
            print("양념 목록:", seasoning_list)
            print("\n")

else:
    print("웹페이지 가져오기 실패.")
