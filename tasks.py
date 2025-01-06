from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def open_robot_order_website():
    browser.configure(
        slowmo=1000,
    )
    open_robot_order_website()
    download_orders_file()
    fill_form_with_csv_data()
    archive_receipts()
    clean_up()

def open_robot_order_website():
    """Navigates to the given URL and clicks on pop up"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')

def download_orders_file():
    """Downloads the orders file from the give URL"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def click_another_bot():
    """Clicks on order another button for new order"""
    page = browser.page()
    page.click("#order-another")

def clicks_ok():
    """Clicks on ok after new order for bots"""
    page = browser.page()
    page.click('text=OK')

def fill_and_order_robot(order):
    """Fill up the order details and clicks the 'Order' button"""
    page = browser.page()
    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    head_number = order["Head"]
    page.select_option("#head", head_names.get(head_number))
    page.click(f"#id-body-{order['Body']}")
    # Fill the dynamic input field
    page.locator('input.form-control[type="number"][placeholder="Enter the part number for the legs"]').fill(order['Legs'])
    page.fill("#address",str(order['Address']))
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = receipt_as_pdf(int(order["Order number"]))
            screenshot_path = robot_screenshot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            click_another_bot()
            clicks_ok()
            break
        
def receipt_as_pdf(order_number):
    """This stores the robot order receipt as pdf"""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def fill_form_with_csv_data():
    """Read data from csv and fill in the robot order form"""
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        fill_and_order_robot(order)
          
def robot_screenshot(order_number):
    """Screenshot taken of the bot image"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embeds the screenshot to receipt pdf"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, source_path=pdf_path, output_path=pdf_path)
    
def archive_receipts():
    """Zip creation."""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def clean_up():
    """Removal of receipts and screenshots after embed to pdf."""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")


