import requests


TOKEN = ""
QUERY_ID = ""
BASE_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet"


# Example usage:
if __name__ == "__main__":
    send_req_url = f"{BASE_URL}/FlexStatementService.SendRequest?t={TOKEN}&q={QUERY_ID}&v=3"
    resp = requests.get(send_req_url)
    print("SendRequest response:", resp.text)

    ref_code = resp.text.split("<ReferenceCode>")[1].split("</ReferenceCode>")[0]

    get_stmt_url = f"{BASE_URL}/FlexStatementService.GetStatement?q={ref_code}&t={TOKEN}&v=3"
    resp2 = requests.get(get_stmt_url)
    xml_file = resp2.text
    print("GetStatement response:", xml_file)
    with open("sample.anonymized.xml", "w") as f:
        f.write(xml_file)
