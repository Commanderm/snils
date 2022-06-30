# coding: utf-8
import re
from requests import post
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


def response_search(response_text):
    search_result = set()
    if isinstance(response_text, dict):
        for key in response_text:
            key_value = response_text[key]
    print(type(response_text))
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
    with open(args.image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response_text = request_analyze(vision_url, iam_token, args.folder_id, image_data)
    jdata = dict(response_text)
    response_search(jdata)
#    print(response_text)


#    print(args.oauth_token)
#    print(args.folder_id)
#    print(args.image_path)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
