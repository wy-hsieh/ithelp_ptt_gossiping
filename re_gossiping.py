import requests
from bs4 import BeautifulSoup
import json

# # 方法 1 使用 cookie
# my_headers = {"cookie": "over18=1"}

# response = requests.get("https://www.ptt.cc/bbs/Gossiping/index.html", headers=my_headers)
# root = BeautifulSoup(response.text, "html.parser")

# links = root.find_all("div", class_ = "title")
# for link in links:
#   print(link.text.strip())




# 方法 2 使用 session

# 要 post 的資料
payload = {
  'from': '/bbs/Gossiping/index.html',
  'yes': 'yes',
}

# 整理匯出時需要的資料 (注意位置，因為是所有的資料，所以會在最外面的 for loop 中)
data = []

# 使用 session 紀錄此次使用的 cookie
rs = requests.session()

# post 資料
response = rs.post("https://www.ptt.cc/ask/over18", data=payload)

# get gossiping 文章頁面
response = rs.get("https://www.ptt.cc/bbs/Gossiping/index.html")
root = BeautifulSoup(response.text, "html.parser")

# 要取得連結，在 class title 中，所以先取得標題
links = root.find_all("div", class_ = "title")

# 此時標題為相對位置，將各標題換為絕對位置
for link in links:
  page_url = "https://www.ptt.cc" + link.a["href"]

  # 取得該連結中的文章標題、作者、時間
  response = rs.get(page_url)
  result = BeautifulSoup(response.text, "html.parser")

  # 一層一層撥開，已取得以上三項資料
  main_content = result.find("div", id = "main-content")
  article_info = main_content.find_all("span", class_ = "article-meta-value")

  # 檢查有無資料，並取得文章、作者、時間
  if len(article_info) != 0:
    author = article_info[0].text
    title = article_info[2].text
    time = article_info[3].text
  else:
    author = "無"
    title = "無"
    time = "無"

  


  # 取得文章內容
  all_text = main_content.text
  # 以 --切割文字，最後 -- 之後的文字沒又用要去除，[:-1]可以去除最後一段文字，但其他符合 -- 切割的地方要復原
  pre_text = all_text.split("--")[:-1]
  one_text = "--".join(pre_text)

  # 去除文章第一行的作者、看板、標題、時間 ，也就是第一個斷行處，一樣切完要將其他切割的地方復原
  text = one_text.split("\n")[1:]
  content = "\n".join(text)


  # 取得留言區資料，包含分類標籤、id、留言、時間
  comments = main_content.find_all("div", class_ = "push")

  # 建立存放推文的容器 list
  push_dic = []
  arrow_dic = []
  shu_dic = []

  # 取得四種資料
  for comment in comments:
    push_tag = comment.find("span", class_ = "push-tag").text
    push_userid = comment.find("span", class_ = "push-userid").text
    push_content = comment.find("span", class_ = "push-content").text
    push_time = comment.find("span", class_ = "push-ipdatetime").text
    
    # 建立 dictionary
    dict1 = { "push_userid": push_userid, "push_content": push_content, "push_time": push_time }
    # 存入 list
    if push_tag == "推 ":
      push_dic.append(dict1)
    if push_tag == "→ ":
      arrow_dic.append(dict1)
    if push_tag == "噓 ":
      shu_dic.append(dict1)

  # 整理匯出時需要的資料 (注意位置，因為是單一頁面的資料，所以會在最裡面的 for loop 中)
  article_data = {}
  comment_dic = {}

  # 整理要匯出的資料
  article_data["author"] = author
  article_data["title"] = title
  article_data["time"] = time
  article_data["content"] = content
  comment_dic["推"] = push_dic
  comment_dic["→"] = arrow_dic
  comment_dic["噓"] = shu_dic
  article_data["comment"] = comment_dic
  
  

  #  整合所有資料
  data.append(article_data)
  # print(article_data["content"])
  # 匯出成 json 檔，會是 utf8 編碼，可以使用 https://jsoneditoronline.org/#left=local.sizono&right=local.kopime 轉換家自動排版
  with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file)

print("完成")

  # 最後匯出有誤 10 筆資料都相同
