# coding: utf-8
import os
from requests import post
from pathlib import Path
import json
import argparse
import base64


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Функция возвращает IAM-токен для аккаунта на Яндексе.
def get_iam_token(iam_url, oauth_token):
    response = post(iam_url, json={"yandexPassportOauthToken": oauth_token})
    json_data = json.loads(response.text)
    if json_data is not None and 'iamToken' in json_data:
        return json_data['iamToken']
    return None


# Функция отправляет на сервер запрос на распознавание изображения и возвращает ответ сервера.
def request_analyze(vision_url, iam_token, folder_id, image_data):
    response = post(vision_url, headers={'Authorization': 'Bearer ' + iam_token}, json={
        'folderId': folder_id,
        'analyze_specs': [
            {
                'content': image_data,
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                        'textDetectionConfig': {'languageCodes': ['en', 'ru']}
                    }
                ],
            }
        ]})
    return response.text


def response_search(response_text, search_for_first_only=False):
    search_result = list()
    if isinstance(response_text, dict):
        for key in response_text:
            key_value = response_text[key]
            if key == "text":
                if search_for_first_only:
                    return key_value
                else:
                    search_result += [key_value]
            if isinstance(key_value, dict) or isinstance(key_value, list) or isinstance(key_value, set):
                _search_result = response_search(key_value, search_for_first_only)
                if _search_result and search_for_first_only:
                    return _search_result
                elif _search_result:
                    for result in _search_result:
                        search_result += [result]
    elif isinstance(response_text, list) or isinstance(response_text, set):
        for element in response_text:
            if isinstance(element, list) or isinstance(element, set) or isinstance(element, dict):
                _search_result = response_search(element, search_for_first_only)
                if _search_result and search_for_first_only:
                    return _search_result
                elif _search_result:
                    for result in _search_result:
                        search_result += [result]

    return search_result if search_result else None


#    print(type(response_text))
#    for line in response_text:
#       if re.search('text', line):
#            print(line),


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder-id', required=True)
    parser.add_argument('--oauth-token', required=True)
    parser.add_argument('--image-path', required=True)
    args = parser.parse_args()

    iam_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'

    iam_token = get_iam_token(iam_url, args.oauth_token)

    # создать новый текстовый файл
    text_file = open("text.csv", "w")
    directory = './'
    files = Path(directory).glob('*.jpg')
    for file in files:
        print(file)
#        with open(args.image_path, "rb") as f:
        with open(file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        response_text = request_analyze(vision_url, iam_token, args.folder_id, image_data)
        jdata = json.loads(response_text)
        snils_text=response_search(jdata)
##    print(snils_text)
##    7 8 10 11 12
        snils = snils_text[7]+" "+snils_text[8]
        second_name = snils_text[10]
        fist_name = snils_text[11]
        therd_name = snils_text[12]
        # переименовать xxxx.jpg на фамилия_имя_отчество.jpg
        os.rename(file, second_name+'_'+fist_name+'_'+therd_name+'.jpg')
        text_file.write(second_name+','+fist_name+','+therd_name+','+snils+','+second_name+'_'+fist_name+'_'+therd_name+".jpg\n")
        print(second_name+' '+fist_name+' '+therd_name+' - '+snils)
##    print(response_text)
##    print(jdata)


#    print(args.oauth_token)
#    print(args.folder_id)
#    print(args.image_path)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/