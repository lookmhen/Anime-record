import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Get the path of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to urls.txt and previous_content.csv
urls_file_path = os.path.join(current_directory, 'urls.txt')
csv_file_path = os.path.join(current_directory, 'previous_content.csv')


# กำหนด token สำหรับ Line Notify
token = os.getenv('LINE_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/x-www-form-urlencoded'}

# กำหนด user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'

# ฟังก์ชันสำหรับส่งการแจ้งเตือนผ่าน Line Notify
def send_line_notification(message):
    payload = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print('Failed to send message.')
        print(response.text)

# ฟังก์ชันสำหรับอ่านเนื้อหาก่อนหน้าจากไฟล์ CSV
def read_previous_content():
    previous_content = {}
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:  # เช็คว่ารายการมีองค์ประกอบอย่างน้อย 2 ตัว
                    previous_content[row[0]] = row[1]
    except FileNotFoundError:
        return previous_content  # คืนค่าพจนานุกรมเปล่าหากไม่พบไฟล์
    return previous_content


# ฟังก์ชันสำหรับบันทึกเนื้อหาล่าสุดไปยังไฟล์ CSV
def save_previous_content(previous_content):
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        for url, content in previous_content.items():
            writer.writerow([url, content])


def main():
    # Get the path of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # get full path file url และ เปิดไฟล์ list URL การ์ตูน
    urls_file_path = os.path.join(current_directory, 'urls.txt')
    with open(urls_file_path, 'r') as file:
        urls = file.readlines()

    # เรียกใช้ฟังก์ชันสำหรับอ่านเนื้อหาก่อนหน้าจากไฟล์ CSV
    previous_content = read_previous_content()

    # สำหรับแต่ละ URL
    for url in urls:
        # ตรวจสอบว่า URL ถูกทำเครื่องหมายว่า "skip" หรือไม่ ถ้ามีคือข้าม
        if url.strip().startswith('skip-'):
            continue  # ข้าม URL นี้ไป

        # ส่งคำขอ request GET ไปยัง URL พร้อมกับ user agent
        response = requests.get(url.strip(), headers={'User-Agent': USER_AGENT})

        # ดึงเนื้อหา HTML ด้วย BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # แยกเนื้อหาข้อความขององค์ประกอบที่มีคลาส "content" หากมี
        content_node = soup.select_one('#single > div.content > div.dt-breadcrumb.breadcrumb_bottom > ol > li:nth-child(3) > a > span')
        epall = soup.find_all('ul', class_='episodios')

        if content_node:
            content_text = content_node.text.strip()

            for ep in epall:
                selectep = ep.find_all('a', href=True)
                if selectep:
                    last_link = selectep[-1]
                    lastepisode = last_link.string + '\n' + 'ลิงก์:' + last_link['href']
                else:
                    content_text = 'ไม่เจอ'

            # ตรวจสอบว่าตรวจว่าการ์ตูนมีตอนใหม่หรือไม่เมื่อเทียบกับบันทึกตอนเก่าในcsvและพิมพ์แจ้งเตือนถ้ามีการเปลี่ยนแปลง
            if url.strip() in previous_content and previous_content[url.strip()] != content_text:
                print(f'{previous_content[url.strip()]} \n มีตอนใหม่ \n ลิงก์::{lastepisode} \n ---------------------------------------------- ')
                send_line_notification(lastepisode+'\n ---------------------------------------------- ')

            # อัปเดตเนื้อหาสำหรับ URL นี้ในพจนานุกรม
            previous_content[url.strip()] = content_text

    # เรียกใช้ฟังก์ชันสำหรับบันทึกเนื้อหาล่าสุดไปยังไฟล์ CSV
    save_previous_content(previous_content)
    
# Run the main function
if __name__ == '__main__':
    main()