import requests
import datetime
import time
import smtplib

API_SUN = "https://api.sunrise-sunset.org/json"
API_ISS = "http://api.open-notify.org/iss-now.json"
SILJAN_LAT = 59.276020
SILJAN_LNG = 9.713000


def iss_lat_long():
    iss_pos = {}
    iss_response = requests.get(url=API_ISS)
    iss_response.raise_for_status()
    iss_data = iss_response.json()

    iss_lat = float(iss_data["iss_position"]["latitude"])
    iss_lng = float(iss_data["iss_position"]["longitude"])
    iss_pos["lat"] = iss_lat
    iss_pos["lng"] = iss_lng
    return iss_pos


def is_iss_overhead():
    iss_pos = iss_lat_long()
    if (
        ((SILJAN_LNG - 5) < iss_pos["lng"])  # West of Siljan
        and ((SILJAN_LNG + 5) > iss_pos["lng"])  # East of Siljan
        and (iss_pos["lat"] > (SILJAN_LAT - 10))  # Long enough to North
    ):
        return True


def is_dark():
    parameters = {"lat": SILJAN_LAT, "lng": SILJAN_LNG, "formatted": 0}

    sun_response = requests.get(url=API_SUN, params=parameters)
    sun_response.raise_for_status()
    sun_data = sun_response.json()

    sunset_hour = int(sun_data["results"]["sunset"].split("T")[1].split(":")[0])
    sunrise_hour = int(sun_data["results"]["sunrise"].split("T")[1].split(":")[0])
    now = datetime.datetime.now()
    if now.hour > sunset_hour or now.hour < sunrise_hour:  # Between sunset and sunrise
        return True


def send_mail():
    gmail = "kristian.skreosen.test@gmail.com"  # smtp.gmail.com
    gmail_password = "qgow znse zjbi cjpz"  # app password
    iss_pos = iss_lat_long()
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=gmail, password=gmail_password)
        connection.sendmail(
            from_addr=gmail,
            to_addrs=gmail,
            msg=f'Subject:ISS overhead!\n\nLook up! ISS is at latitude: "{iss_pos["lat"]}" and longitude: "{iss_pos["lng"]}"',
        )


while True:
    if is_dark():
        if is_iss_overhead():
            send_mail()

    time.sleep(60)
