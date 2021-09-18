import os
import requests
import argparse
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def shorten_link(token, long_link):
    if not urlparse(long_link).scheme:
        long_link = f"http://{long_link}"
    bitlink_url = "https://api-ssl.bitly.com/v4/bitlinks"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"long_url": long_link}

    response = requests.post(
        bitlink_url,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    bitlink = response.json()["link"]
    return bitlink


def count_clicks(token, bitlink):
    count_clicks_url = ("https://api-ssl.bitly.com/v4/bitlinks/"
                        f"{bitlink}/clicks/summary")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"unit": "month"}

    response = requests.get(
        count_clicks_url,
        headers=headers,
        params=payload,
    )
    response.raise_for_status()
    clicks_count = response.json()["total_clicks"]
    return clicks_count


def is_bitlink(token, verified_link):
    bitly_service_url = "https://api-ssl.bitly.com/v4/expand"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"bitlink_id": verified_link}

    response = requests.post(
        bitly_service_url,
        headers=headers,
        json=payload,
    )
    return response.ok


def input_link():
    parser = argparse.ArgumentParser(
        description="Сокращаем длинную ссылку или"
                    "выводим количество переходов для короткой"
    )
    parser.add_argument(
        "link",
        help="Введите длинную ссылку для получения битлинка"
             "или короткую для просмотра количества переходов"
    )
    args = parser.parse_args()
    return args.link


def main():
    bitly_token = os.getenv("BITLY_TOKEN")
    user_link = input_link()
    bitlink = f"{urlparse(user_link).netloc}{urlparse(user_link).path}"

    try:
        if is_bitlink(bitly_token, bitlink):
            clicks_count = count_clicks(bitly_token, bitlink)
            print("Количество кликов:", clicks_count)
        else:
            new_bitlink = shorten_link(bitly_token, user_link)
            print(f"Битлинк {new_bitlink}")
    except requests.exceptions.HTTPError:
        print("Неверная ссылка")


if __name__ == "__main__":
    main()
